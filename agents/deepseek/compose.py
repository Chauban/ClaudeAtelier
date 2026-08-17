"""让 DeepSeek 盲着把卡画出来：写脚本 -> 静态检查 -> 子进程执行 -> 报错回灌 -> 重来。

这是 Phase 1 的全部意义所在：一个看不见图的模型，能不能靠
「异常消息 + 文字版画面报告」把一张卡画干净。
"""
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import client  # noqa: E402
import config  # noqa: E402
import guard  # noqa: E402
import meter  # noqa: E402

MAX_ROUNDS = config.MAX_ROUNDS
CHARTER = config.CHARTER


def _read(p):
    return io.open(p, encoding="utf-8").read()


def chat(messages, max_tokens=None, timeout=None):
    """转调共用客户端。重试、超时、token 预算全在 config/client 里统一管。"""
    msg, meta = client.chat(messages, max_tokens=max_tokens, timeout=timeout)
    meter.record("render", meta)
    return (msg.get("content") or ""), {
        "s": meta["sec"], "out": meta["out"],
        "reason": meta["reasoning"], "finish": meta["finish"],
        "model": meta.get("model"),
        "fingerprint": meta.get("fingerprint"),
    }


def extract_code(txt):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", txt, re.S)
    if m:
        return max(m, key=len).strip()
    return txt.strip()


def build_prompt(brief):
    charter = _read(CHARTER)
    appendix = _read(os.path.join(HERE, "prompts", "runtime_appendix.md"))
    sysmsg = (
        "你是 ClaudeAtelier 的卡片设计师。严格遵守《卡片创作章程》的全部条款。\n"
        "你没有视觉能力，看不见自己画出的图——所以必须靠报错信息和文字版画面报告来判断对错。\n"
        "只输出可直接执行的 Python 代码，不要解释，不要 markdown 围栏。\n\n"
        "════════ 卡片创作章程 ════════\n" + charter +
        "\n\n════════ 环境说明 ════════\n" + appendix)
    # 背景：给构图用的语感，**不是**卡面内容。刻意不把它放进渲染脚本的
    # 全局命名空间（见 runner.py 传入的那几个键）—— 模型引用不到，也就
    # 画不上去，比反复叮嘱可靠。
    ctx = (brief.get("CONTEXT") or "").strip()
    ctx_block = ("【背景】以下几句**不要印到卡上**，只用来帮你决定构图、"
                 "意象和配色：\n{}\n\n".format(ctx)) if ctx else ""

    user = (
        "本次任务（编号、风格、语言、领域都是强制的，不许更换）：\n\n"
        "  流水号 SERIAL = {SERIAL}\n"
        "  日期   DATE   = {DATE}\n"
        "  风格   S={STYLE_NO}  {STYLE_NAME}\n"
        "  语言   {LANG}（代码 {LANG_CODE}）\n"
        "  领域   {TOPIC}\n\n"
        "金句 QUOTE（逐字使用，不要改写）：\n{QUOTE}\n\n"
        "冷知识 FACT（逐字使用，不要改写）：\n{FACT}\n\n"
        # ctx_block 必须当**取值**传进去，不能拼进模板 ——
        # 它是模型写的自由文本，里面一个 { 就会让 .format 炸掉。
        "{CTX_BLOCK}"
        "卡面上只出现 QUOTE、FACT、SERIAL、DATE 四样文字，别的都不要写上去。\n\n"
        "请写出完整的渲染脚本。记住：QUOTE / FACT / SERIAL / DATE / OUT_PATH "
        "已是脚本里的全局变量，直接引用，不要重新定义。"
        "最后必须 sf.save(OUT_PATH)。\n\n"
        # 实测：首轮在复杂风格上会把 40000 token 全烧在推理里、可见输出为零，
        # 白费约 6 分钟。把这句放进首轮提示，能直接避免那一轮。
        "重要：不要在心里反复推敲版面。先定下画布尺寸和几个关键 y 坐标，"
        "直接开始写代码——写错了会有带坐标的报错告诉你怎么改，改起来比空想快得多。"
    ).format(CTX_BLOCK=ctx_block, **brief)
    return [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]


def run(brief, workdir, verbose=True):
    os.makedirs(workdir, exist_ok=True)
    brief_path = os.path.join(workdir, "brief.json")
    io.open(brief_path, "w", encoding="utf-8").write(
        json.dumps(brief, ensure_ascii=False))

    messages = build_prompt(brief)
    history = []
    improved = False      # 构图改进机会只给一次
    keep = None           # 已通过硬检查的那一版，改进失败时兜底
    drawn = None          # **最后一版真的把图画出来了的**（哪怕没过检查）
    resolved = None       # 服务端回声的模型号，写进台账的 model 列
    # 后端指纹，写进台账的 fingerprint 列。和 resolved 一样取**最后一次回声**：
    # 一次生卡要发好几轮请求，后端热更新的话轮次之间可以不一样，而决定这张
    # 画面的是最后那一轮。刻意不收集成集合 —— 这一列回答的是「画出这张图的
    # 那次调用跑在什么后端上」，不是「这次生卡途经过哪些后端」。
    fp = None

    def _mtime():
        try:
            return os.path.getmtime(brief["OUT_PATH"])
        except OSError:
            return None

    for rd in range(1, MAX_ROUNDS + 1):
        if verbose:
            print("\n--- 第 {} 轮 ---".format(rd))
        txt, meta = chat(messages)
        resolved = meta.get("model") or resolved
        fp = meta.get("fingerprint") or fp
        if verbose:
            print("  模型返回 {}s, 输出 {} token（其中推理 {}）, finish={}".format(
                meta["s"], meta["out"], meta["reason"], meta["finish"]))
        code = extract_code(txt)

        # 推理烧光预算 -> 可见输出为空。这不是设计错误，别拿假报错去误导模型，
        # 直接重发同一轮请求（不追加对话），并提醒它先写代码。
        if not code.strip():
            if verbose:
                print("  [空输出] finish={} —— 推理占满预算，重来一次并要求精简思考".format(
                    meta["finish"]))
            history.append({"round": rd, "stage": "empty", "error":
                            "模型没有产出可见内容（finish={}）".format(meta["finish"])})
            messages = messages[:2] + [{"role": "user", "content":
                messages[1]["content"] +
                "\n\n注意：上一次你把全部预算用在了思考上，没有输出代码。"
                "请把思考压到最短，直接开始写脚本。"}]
            continue

        code_path = os.path.join(workdir, "render_r{}.py".format(rd))
        io.open(code_path, "w", encoding="utf-8").write(code)

        # ---- 静态检查
        try:
            warns = guard.check(code)
            if warns and verbose:
                for w in warns[:3]:
                    print("  [warn] {}".format(w))
        except guard.GuardError as e:
            if verbose:
                print("  [守卫拦截] {}".format(str(e).splitlines()[0]))
            history.append({"round": rd, "stage": "guard", "error": str(e)})
            messages += [{"role": "assistant", "content": code},
                         {"role": "user", "content":
                          "静态检查没通过：\n\n{}\n\n请修正后重新给出完整脚本。".format(e)}]
            continue

        # ---- 子进程执行 + 检查
        report_path = os.path.join(workdir, "report_r{}.json".format(rd))
        # 记下执行前的 mtime：轮次耗尽时要发「最后一版画出来的图」，而磁盘上那张
        # 必须和存档的手稿是同一轮的。只看文件存不存在会张冠李戴 ——
        # 第 5 轮画出了图、第 6 轮崩在 save 之前，文件还是第 5 轮的。
        before = _mtime()
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "runner.py"),
             brief_path, code_path, report_path],
            capture_output=True, text=True, timeout=180)
        if not os.path.exists(report_path):
            err = (proc.stderr or proc.stdout or "")[-1500:]
            history.append({"round": rd, "stage": "crash", "error": err})
            messages += [{"role": "assistant", "content": code},
                         {"role": "user", "content":
                          "脚本执行崩溃：\n\n{}\n\n请修正后重新给出完整脚本。".format(err)}]
            if verbose:
                print("  [崩溃] {}".format(err.strip().splitlines()[-1:] or ""))
            continue

        rep = json.load(io.open(report_path, encoding="utf-8"))
        history.append({"round": rd, "stage": rep["stage"],
                        "error": rep.get("error"), "metrics": rep.get("metrics")})
        after = _mtime()
        if after is not None and after != before:
            drawn = {"rounds": rd, "code": code, "report": rep}

        if rep["ok"]:
            warns = (rep.get("metrics") or {}).get("warnings") or []
            # 硬检查过了但构图有毛病：给一次改进机会，改不好就用现有这张。
            # 不硬性拦截，是因为留白到底是不是毛病属于审美判断，规则不该代劳。
            if warns and not improved and rd < MAX_ROUNDS:
                improved = True
                keep = {"ok": True, "rounds": rd, "code": code, "model": resolved,
                        "fingerprint": fp,
                        "png": brief["OUT_PATH"], "report": rep, "history": history}
                if verbose:
                    print("  [通过但有构图警告] {}".format(warns[0][:70]))
                messages += [{"role": "assistant", "content": code},
                             {"role": "user", "content":
                              "硬性检查已全部通过，但构图上还有问题：\n\n  - {}\n\n"
                              "【当前画面报告】\n{}\n\n"
                              "请在保持现有风格与内容不变的前提下改进版面，"
                              "重新给出完整脚本。".format(
                                  "\n  - ".join(warns), rep.get("preview") or "")}]
                continue
            if verbose:
                print("  [通过] 指标 {}".format(
                    {k: v for k, v in rep["metrics"].items() if k != "warnings"}))
            return {"ok": True, "rounds": rd, "code": code, "model": resolved,
                    "fingerprint": fp,
                    "png": brief["OUT_PATH"], "report": rep, "history": history}

        if verbose:
            print("  [{}] {}".format(rep["stage"], (rep["error"] or "").splitlines()[0]))

        feedback = "这一轮没通过。\n\n【问题】\n{}\n".format(rep["error"])
        if rep.get("preview"):
            feedback += "\n【当前画面报告】\n{}\n".format(rep["preview"])
        feedback += "\n请针对上面的问题修正，重新给出完整脚本（不要只给片段）。"
        messages += [{"role": "assistant", "content": code},
                     {"role": "user", "content": feedback}]

        # 控制上下文膨胀：只保留系统提示 + 首个任务 + 最近两轮往返
        if len(messages) > 8:
            messages = messages[:2] + messages[-4:]

    # 轮次耗尽。若中途有一版已过硬检查（只是构图警告没改好），就用那一版。
    if keep:
        keep["history"] = history
        keep["model"] = resolved or keep.get("model")
        keep["fingerprint"] = fp or keep.get("fingerprint")
        if verbose:
            print("  [改进未果，采用先前通过的那一版]")
        return keep

    # 一版都没过硬检查，但磁盘上有图 —— 照发，打降级标记。
    #
    # 2026-08-12 由项目所有者决定改掉原来的「宁可空一班」：空卡在展墙上只是一个
    # 「未出卡」的格子，什么都说明不了；一张有毛病的卡是实打实的证物，
    # 而且毛病是**看得见**的，读者不会被误导。fail closed 那条原则仍然管着
    # 「连图都没有」的情况 —— 那时确实只能空。
    if drawn:
        probs = ((drawn["report"].get("problems") or [])
                 if isinstance(drawn.get("report"), dict) else [])
        if verbose:
            print("  [{} 轮都没过检查，采用最后一版画出来的图]"
                  " —— 遗留 {} 项问题，会记进台账".format(MAX_ROUNDS, len(probs)))
        return {"ok": True, "degraded": True, "rounds": drawn["rounds"],
                "code": drawn["code"], "model": resolved, "fingerprint": fp,
                "png": brief["OUT_PATH"], "report": drawn["report"],
                "problems": probs, "history": history}

    return {"ok": False, "rounds": MAX_ROUNDS, "model": resolved,
            "fingerprint": fp, "history": history}
