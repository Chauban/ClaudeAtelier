"""看得见图的那条线：写脚本 -> 子进程执行 -> **把图发回去让它自己看** -> 自己改。

与 compose.py（盲模型那条）是同一件事的两种做法，差别只在反馈通道：

    compose.py         受控画布当场抛错 + 文字版画面报告（占位图、直方图、墨迹重心）
    compose_vision.py  真图

这里刻意**没有** lint、没有受控画布、没有构图警告。不是省事，是因为那些东西
对有视力的模型是在替它看，而「它看不看得懂自己画的图」正是要展出的东西。
Claude 那条线也是这么跑的（写脚本 → 用 Read 看 PNG → 自己改），这条线要和它对齐。

唯一保留的机器判定是「脚本跑没跑起来、图落没落地」—— 那与艺术无关。

CLAUDE.md 里最贵的那条教训是：**「看得见」是能力，不是习惯** —— 模型很容易
画完就报告成功。所以这里不问「你觉得行吗」，而是强制它交一份结构化判词，
并且**连判词一起存档公开**。说了 ok 而图上有毛病，那是留得下来的记录。
"""
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import client  # noqa: E402
import config  # noqa: E402
import guard  # noqa: E402

MAX_ROUNDS = config.MAX_ROUNDS
CHARTER = config.CHARTER


def _read(p):
    return io.open(p, encoding="utf-8").read()


def extract_code(txt):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", txt, re.S)
    if m:
        return max(m, key=len).strip()
    return txt.strip()


def feedback_image(png_path):
    """把原图压成回灌用的 JPEG 字节。

    原图是 scale=2 的 2000×3000+，直接发既贵又没必要 —— 一张卡的毛病在 1024 宽
    上全看得见。质量不敢再压：JPEG 糊掉细字会变成「它自己画的毛病」，
    那等于我们伪造了证据。
    """
    from PIL import Image
    with Image.open(png_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        nw = min(config.VISION_FEEDBACK_WIDTH, w)
        nh = max(1, round(h * nw / float(w)))
        im = im.resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=config.VISION_FEEDBACK_QUALITY, optimize=True)
    return buf.getvalue(), (nw, nh)


def build_prompt(brief):
    charter = _read(CHARTER)
    appendix = _read(os.path.join(HERE, "prompts", "runtime_appendix_vision.md"))
    sysmsg = (
        "你是 ClaudeAtelier 的卡片设计师。严格遵守《卡片创作章程》的全部条款。\n"
        "你能看见自己画出的图——每一轮渲染后我们会把它发给你，"
        "画面上的一切问题只能由你自己发现。\n"
        "写脚本时只输出可直接执行的 Python 代码，不要解释，不要 markdown 围栏。\n\n"
        "════════ 卡片创作章程 ════════\n" + charter +
        "\n\n════════ 环境说明 ════════\n" + appendix)

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
        # ctx_block 当取值传，不能拼进模板 —— 模型写的自由文本里一个 { 就会炸掉
        "{CTX_BLOCK}"
        "请写出完整的渲染脚本。QUOTE / FACT / SERIAL / DATE / OUT_PATH "
        "已是脚本里的全局变量，直接引用，不要重新定义。"
        "最后把图存到 OUT_PATH。"
    ).format(CTX_BLOCK=ctx_block, **brief)
    return [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]


CRITIQUE_ASK = (
    "这是你刚画出来的那张卡（等比缩到 {w}×{h} 给你看，原图是它的 {mul} 倍）。\n\n"
    "请**逐块**检查：金句、冷知识、流水号、日期 —— 每一块是否完整、清晰、"
    "没被装饰或图层盖住、没超出画布、字号在缩略图尺寸下仍读得出来；"
    "中文有没有变成方框；字形是不是该地区的。\n"
    "然后退开看整张：构图重心、留白、以及有多像「{style}」这个风格。\n\n"
    "只输出那个 JSON 判词（ok / problems / style_fidelity / notes），不要别的话。")


def critique(messages, png_path, brief, verbose=True):
    """把图发回去，要一份结构化判词。返回 (verdict_dict, meta)。"""
    img, (w, h) = feedback_image(png_path)
    ask = CRITIQUE_ASK.format(
        w=w, h=h, mul=2, style=brief["STYLE_NAME"])
    msgs = messages + [{"role": "user", "content": ask}]
    msg, meta = client.chat(msgs, images=[img], json_mode=True, stage="critique")
    txt = msg.get("content") or ""
    try:
        v = client.extract_json(txt)
    except client.ClientError:
        # 判词解析不了不该报废整张卡：当作「它没说清楚」，按通过处理并留痕。
        # 宁可把一张可能有小毛病的卡发出去，也不要因为 JSON 格式把好卡毙掉 ——
        # 何况「判词都写不明白」本身就是关于这只手的信息。
        v = {"ok": True, "problems": [], "style_fidelity": None,
             "notes": "（判词无法解析，原样存档）", "raw": txt[:800]}
    v.setdefault("ok", True)
    v.setdefault("problems", [])
    return v, meta


def _fmt_problems(v):
    out = []
    for p in (v.get("problems") or []):
        if isinstance(p, dict):
            out.append("  - {}：{}（建议：{}）".format(
                p.get("where") or "?", p.get("what") or "?", p.get("fix") or "—"))
        else:
            out.append("  - {}".format(p))
    return "\n".join(out)


def run(brief, workdir, verbose=True):
    os.makedirs(workdir, exist_ok=True)
    brief_path = os.path.join(workdir, "brief.json")
    io.open(brief_path, "w", encoding="utf-8").write(
        json.dumps(brief, ensure_ascii=False))

    messages = build_prompt(brief)
    history, critiques = [], []
    keep = None          # 最后一版真的画出图的，判词没过也留着 —— 宁可发张有毛病的
    resolved = None

    for rd in range(1, MAX_ROUNDS + 1):
        if verbose:
            print("\n--- 第 {} 轮 ---".format(rd))
        msg, meta = client.chat(messages, stage="render")
        resolved = meta.get("model") or resolved
        txt = msg.get("content") or ""
        if verbose:
            print("  模型返回 {}s, 输出 {} token（其中推理 {}）, finish={}".format(
                meta["sec"], meta["out"], meta["reasoning"], meta["finish"]))
        code = extract_code(txt)

        if not code.strip():
            # 推理烧光预算 -> 可见输出为空。别拿假报错误导它，重发同一轮。
            history.append({"round": rd, "stage": "empty",
                            "error": "模型没有产出可见内容（finish={}）".format(meta["finish"])})
            if verbose:
                print("  [空输出] finish={} —— 重来一次并要求精简思考".format(meta["finish"]))
            messages = messages[:2] + [{"role": "user", "content":
                messages[1]["content"] +
                "\n\n注意：上一次你把全部预算用在了思考上，没有输出代码。"
                "请把思考压到最短，直接开始写脚本。"}]
            continue

        code_path = os.path.join(workdir, "render_r{}.py".format(rd))
        io.open(code_path, "w", encoding="utf-8").write(code)

        # ---- 静态检查（只管安全，不管排版：allow_raw_text 跟着 config.VISION）
        try:
            warns = guard.check(code)
            if warns and verbose:
                for w in warns[:3]:
                    print("  [warn] {}".format(w))
        except guard.GuardError as e:
            history.append({"round": rd, "stage": "guard", "error": str(e)})
            if verbose:
                print("  [守卫拦截] {}".format(str(e).splitlines()[0]))
            messages += [{"role": "assistant", "content": code},
                         {"role": "user", "content":
                          "静态检查没通过：\n\n{}\n\n请修正后重新给出完整脚本。".format(e)}]
            continue

        # ---- 子进程执行
        report_path = os.path.join(workdir, "report_r{}.json".format(rd))
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "runner_plain.py"),
             brief_path, code_path, report_path],
            capture_output=True, text=True, timeout=300)
        if not os.path.exists(report_path):
            err = (proc.stderr or proc.stdout or "")[-1500:]
            history.append({"round": rd, "stage": "crash", "error": err})
            messages += [{"role": "assistant", "content": code},
                         {"role": "user", "content":
                          "脚本执行崩溃：\n\n{}\n\n请修正后重新给出完整脚本。".format(err)}]
            continue

        rep = json.load(io.open(report_path, encoding="utf-8"))
        history.append({"round": rd, "stage": rep["stage"],
                        "error": rep.get("error"), "png": rep.get("png")})
        if not rep["ok"]:
            if verbose:
                print("  [{}] {}".format(rep["stage"], (rep["error"] or "").splitlines()[0]))
            messages += [{"role": "assistant", "content": code},
                         {"role": "user", "content":
                          "这一轮没能出图。\n\n{}\n\n"
                          "请修正后重新给出完整脚本（不要只给片段）。".format(rep["error"])}]
            continue

        png = brief["OUT_PATH"]
        # 到这里图已经在磁盘上了。哪怕后面判词说不行，也先留着这一版 ——
        # 轮次耗尽时宁可发一张它自己都不满意的卡，也不空一班：
        # 画得不好是看得见的，而空着只是一个格子，什么都说明不了。
        keep = {"ok": True, "rounds": rd, "code": code, "model": resolved,
                "png": png, "report": rep}

        # ---- 让它自己看
        t0 = time.time()
        v, cmeta = critique(messages, png, brief, verbose=verbose)
        resolved = cmeta.get("model") or resolved
        v["round"] = rd
        critiques.append(v)
        if verbose:
            print("  [看图] ok={} 风格贴合={} 问题 {} 项（{}s）".format(
                v.get("ok"), v.get("style_fidelity"),
                len(v.get("problems") or []), round(time.time() - t0, 1)))
            for line in _fmt_problems(v).splitlines()[:3]:
                print("   {}".format(line))

        if v.get("ok") and not (v.get("problems") or []):
            return {"ok": True, "rounds": rd, "code": code, "model": resolved,
                    "png": png, "report": rep, "history": history,
                    "critiques": critiques}

        if rd >= MAX_ROUNDS:
            break

        probs = _fmt_problems(v) or "  - （你说不行，但没列出具体问题）"
        messages += [{"role": "assistant", "content": code},
                     {"role": "user", "content":
                      "你自己看过图之后列出的问题：\n\n{}\n\n"
                      "请针对这些问题修正，重新给出完整脚本（不要只给片段）。"
                      "风格、金句、冷知识都不要动。".format(probs)}]

        # 控制上下文膨胀：只保留系统提示 + 首个任务 + 最近两轮往返。
        # **历史轮的图不留**（本来也没进 messages —— critique 用的是临时副本），
        # 否则 7 轮下来上下文里躺着 7 张 3000px 的卡。
        if len(messages) > 8:
            messages = messages[:2] + messages[-4:]

    if keep:
        keep.update({"history": history, "critiques": critiques,
                     "model": resolved or keep.get("model"),
                     "degraded": True})
        if verbose:
            print("\n  [轮次耗尽，采用最后一版画出来的图]"
                  " —— 它自己仍标了 {} 项问题，会记进台账".format(
                      len((critiques[-1].get("problems") if critiques else []) or [])))
        return keep
    return {"ok": False, "rounds": MAX_ROUNDS, "model": resolved,
            "history": history, "critiques": critiques}
