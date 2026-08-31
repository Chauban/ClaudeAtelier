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
import meter  # noqa: E402

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
    # 字体清单当场扫出来注入。环境说明里原先是一份写死的表格，自己写着「清单会
    # 过时，先查再用，不要照抄」—— 而脚本不能 import os、跑不了 shell，它根本
    # 没有查的手段。**既要求先查、又不给查的手段**，是 2026-09-01 之前的一处
    # 自相矛盾；Claude 那条线的 SKILL.md 让它开工前先 ls 字体目录，这里补上等价物。
    #
    # inventory_text() 刻意不排序、不打分、不筛选：查是我们代它做的（它做不到），
    # 选是它自己的事 —— 避开 Italic/Condensed、按 face 名分 SC/TC/HK 那些判断，
    # Claude 自己做，这条线也得自己做。扫不出来不该拖垮整张卡，降级成一句提示。
    try:
        import fonts
        inv = fonts.inventory_text()
    except Exception as e:                                   # noqa: BLE001
        inv = u"（字体清单没扫出来：{}。先用小字号试画一行确认字体可用。）".format(e)
    appendix = appendix.replace("{{FONT_INVENTORY}}", inv)
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


CRITIQUE_SYS = (
    "你是 ClaudeAtelier 的验片员。看一张刚渲染出来的卡片，指出画面上的问题。\n"
    "只输出一个 JSON 对象：\n"
    '{"ok": true/false, '
    '"problems": [{"where":"位置", "what":"什么毛病", "fix":"怎么改"}], '
    '"style_fidelity": 1-5, "notes": "一句话总评"}\n'
    "不要输出别的任何文字。")

CRITIQUE_ASK = (
    # 只陈述事实，不据此调低标准 —— 「我们只给你看小图，所以你别那么挑」
    # 是拿环境的省钱去换判断的准头，方向反了。真觉得看不清，该给更大的图。
    #
    # 2026-09-01 更正措辞。原话是「等比缩到 {w}×{h}，原图是它的 2 倍」，听上去
    # 像在道歉：你看到的是被砍过的版本 —— 于是「大概是缩图糊了」就成了放过一处
    # 毛病的现成理由。事实相反：卡按逻辑宽 800~1200、scale=2 渲染，回灌的 1024
    # 宽正好是这张卡设计时的那个尺寸。而且 Claude 那条线用 Read 看 PNG 同样降
    # 采样（长边约 1568，一张 2000×3560 到手约 880 宽），两边看到的分辨率本来
    # 就在同一档。所以该改的是这句话，不是 VISION_FEEDBACK_WIDTH。
    "这是刚画出来的卡，等比缩到 {w}×{h} —— 这就是这张卡设计时的尺寸"
    "（原图是它的 2 倍，那是为印刷留的余量），不是缩略图；看不清就是真的看不清。"
    "目标风格：{style}。\n\n"
    "卡面上应当**且只应当**出现这四样文字，逐字如下：\n"
    "  流水号：{serial}\n  日期：{date}\n  金句：{quote}\n  冷知识：{fact}\n\n"
    "请**逐块**核对：每一块是否完整、逐字无误（标点的全形半形也算）、清晰、"
    "没被装饰或图层盖住、没超出画布、字号在这个尺寸下仍读得出来；"
    "中文有没有变成方框；字形是不是{lang}该用的；西文单词有没有被从中间断行；"
    "标点有没有落在行首。\n"
    "然后退开看整张：构图重心、留白、以及有多像「{style}」。\n\n"
    # ★ 这几行必须逐字对齐章程第 11 节「成品自检」，那是所有产出方共用的标准，
    #   而且章程明说「要达到的标准相同」。
    #
    #   2026-08-13 我曾在这里另写过一套：加了「ok 不等于完美」「缩略尺寸下看不
    #   真切的别当问题」，还加了「每多返工一轮都有实实在在的成本」。最后那条是
    #   拿账单去压一只手的艺术判断，而 Claude 那条线一个字的成本压力都没有 ——
    #   那不是能力差别，是规则差别。当时轮数从 11 降到 3、成本从 8.75 降到 3.96，
    #   但那个数字是污染过的：分不清多少来自「标准说清楚了」、多少来自
    #   「我让它别那么挑」。章程的改动纪律写着任何一方不得另写一份创作要求，
    #   我干的正是这件事。**要改这条标准，去改章程，两边同时生效。**
    "判定标准（章程第 11 节，各产出方相同）：\n"
    "  检查溢出、重叠、方框字、字号过小、编号日期是否清晰；"
    "有问题改脚本重渲染，直到画面干净。\n"
    "  画面干净就判 ok=true。你仍然可以在 problems 里列出还能更好的地方，"
    "那不影响 ok=true，会连同判词一起存档。\n\n"
    "只输出那个 JSON 判词。**每条 problem 三个字段各一句话，不要展开论述**；没毛病就交空数组。")


def critique(messages, png_path, brief, verbose=True):
    """把图发回去，要一份结构化判词。返回 (verdict_dict, meta)。

    **刻意不带渲染会话的历史。** 早先这里是 `messages + 问题`，于是每次自检都
    连章程全文、环境说明和模型刚写的那份脚本一起重发一遍 —— 2026-08-12 第一张
    卡 14 元，这是两个大头之一。验片只需要「风格 + 四段文字 + 那张图」，
    代码长什么样与画面对不对无关。

    额外的好处：不给它看自己的代码，它就只能**从图上**判断，而不是从代码里
    推断画面应该是什么样 —— 这条线要测的恰恰是前者。
    """
    img, (w, h) = feedback_image(png_path)
    ask = CRITIQUE_ASK.format(
        w=w, h=h, style=brief["STYLE_NAME"], lang=brief["LANG"],
        serial=brief["SERIAL"], date=brief["DATE"],
        quote=brief["QUOTE"], fact=brief["FACT"])
    msgs = [{"role": "system", "content": CRITIQUE_SYS},
            {"role": "user", "content": ask}]
    # 判词是结构化的短文本，给它 4000 就绰绰有余。不设上限时实测每条写到
    # 1638 token（11 条 = 1.8 元），全花在 fix 字段的长篇建议上。
    msg, meta = client.chat(msgs, images=[img], json_mode=True,
                            stage="critique", max_tokens=4000)
    meter.record("critique", meta)
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
    # 后端指纹，写进台账的 fingerprint 列。取值口径与 resolved 逐字相同
    # （最后一次回声，渲染和判词两处调用都算）—— 两列并排放在台账里，
    # 口径不一样会比缺一列更误导人。
    fp = None
    # 本轮的思考档位。None = 用厂商客户端为 render 阶段定的默认值（K3 是 high）。
    # 只有真撞上「推理烧光预算、可见输出为零」时，才把之后的轮次降到 low。
    # 预先降档是拿成本去换这只手的思考深度，而 Claude 那条线写脚本时想多久都行 ——
    # 那不是能力差别，是规则差别。
    effort = None

    for rd in range(1, MAX_ROUNDS + 1):
        if verbose:
            print("\n--- 第 {} 轮 ---".format(rd))
        msg, meta = client.chat(messages, stage="render", reasoning=effort)
        meter.record("render", meta)
        resolved = meta.get("model") or resolved
        fp = meta.get("fingerprint") or fp
        txt = msg.get("content") or ""
        if verbose:
            print("  模型返回 {}s, 输出 {} token（其中推理 {}）, finish={}".format(
                meta["sec"], meta["out"], meta["reasoning"], meta["finish"]))
        code = extract_code(txt)

        if not code.strip():
            # 推理烧光预算 -> 可见输出为空。别拿假报错误导它，重发同一轮。
            history.append({"round": rd, "stage": "empty",
                            "error": "模型没有产出可见内容（finish={}）".format(meta["finish"])})
            effort = "low"   # 事后止损，不是每张卡预先付的税
            if verbose:
                print("  [空输出] finish={} —— 降到 low 重来一次并要求精简思考".format(
                    meta["finish"]))
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
                "fingerprint": fp, "png": png, "report": rep}

        # ---- 让它自己看
        t0 = time.time()
        v, cmeta = critique(messages, png, brief, verbose=verbose)
        resolved = cmeta.get("model") or resolved
        fp = cmeta.get("fingerprint") or fp
        v["round"] = rd
        critiques.append(v)
        if verbose:
            print("  [看图] ok={} 风格贴合={} 问题 {} 项（{}s）".format(
                v.get("ok"), v.get("style_fidelity"),
                len(v.get("problems") or []), round(time.time() - t0, 1)))
            for line in _fmt_problems(v).splitlines()[:3]:
                print("   {}".format(line))

        # **以它自己的 ok 为准，不再额外要求「问题列表为空」。**
        #
        # 2026-08-13 的教训：环境说明里写着「ok：这张卡能不能发出去，只有你自己
        # 说了算」，代码里却写成 `ok and not problems`。而它说 ok 的时候照例会
        # 附几条「还可以更好」的小建议，于是永远不满足 —— 第 5 轮它就认可了，
        # 硬生生磨到第 12 轮，多花 8 轮的钱，而且第 11、12 轮反而退回 ok=False，
        # 越磨越差。把判断权交出去就要真交，不能嘴上交、代码里留一手。
        #
        # ok=True 时残留的建议不丢：写进 text/*.md 的「看图自检」一节存档。
        if v.get("ok"):
            return {"ok": True, "rounds": rd, "code": code, "model": resolved,
                    "fingerprint": fp,
                    "png": png, "report": rep, "history": history,
                    "critiques": critiques,
                    "problems": [p for p in (v.get("problems") or [])]}

        if rd >= MAX_ROUNDS:
            break

        probs = _fmt_problems(v) or "  - （你说不行，但没列出具体问题）"
        messages += [{"role": "assistant", "content": code},
                     {"role": "user", "content":
                      "你自己看过图之后列出的问题：\n\n{}\n\n"
                      "请针对这些问题修正，重新给出完整脚本（不要只给片段）。"
                      "风格、金句、冷知识都不要动。".format(probs)}]

        # 控制上下文膨胀：保留系统提示 + 首个任务 + 最近四轮往返。
        # **历史轮的图不留**（本来也没进 messages —— critique 用的是临时副本），
        # 否则 12 轮下来上下文里躺着 12 张 3000px 的卡。
        #
        # 2026-09-01 从「最近两轮」放宽到四轮。截断本身是必要的（图不留、上下文
        # 不能无限涨），但砍到两轮纯粹是省钱：模型看不见自己第 2 轮试过什么、
        # 为什么放弃，就会绕回去再改一遍同一处 —— 而 Claude 那条线的会话从头到尾
        # 完整，记得自己每一版做过什么。这一刀砍掉的不是算力，是记性。
        # 四轮往返里仍然一张图都没有，涨的只是文本。
        if len(messages) > 12:
            messages = messages[:2] + messages[-8:]

    if keep:
        keep.update({"history": history, "critiques": critiques,
                     "model": resolved or keep.get("model"),
                     "fingerprint": fp or keep.get("fingerprint"),
                     "degraded": True})
        if verbose:
            print("\n  [轮次耗尽，采用最后一版画出来的图]"
                  " —— 它自己仍标了 {} 项问题，会记进台账".format(
                      len((critiques[-1].get("problems") if critiques else []) or [])))
        return keep
    return {"ok": False, "rounds": MAX_ROUNDS, "model": resolved,
            "fingerprint": fp, "history": history, "critiques": critiques}
