"""发布：压缩版 webp、文字副本 md、台账追加、以及提交路径白名单校验。

**绝不触碰** README.md、Cards/cards-index.csv、任何 NO.* 文件。
那三样是 Claude 的写入面；两边同时写会让 sync-to-github.bat 的
pull --rebase 冲突并 goto FAIL，卡片静默积压 —— 那正是 2026-08-05
（4 张卡 20 小时）和 08-08（3 张卡）两次事故的形状。
白名单是机械执行的，不靠自觉。
"""
import hashlib
import io
import os
import re
import subprocess

import config
import ledger


def sha256_file(path, chunk=1 << 20):
    """原图指纹。原图不进仓库（400MB+ 只在本地和 90 天的 artifact 里），
    这一列是它唯一进得了 git 的部分 —— 将来核对异地副本、判断某张图有没有
    被改动过，只能靠它。"""
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def make_code(code_text, out_path):
    """手稿：模型为这张卡现写的渲染脚本，原样存档。

    **不做任何整理、格式化或删注释**。档案存的是当时那份，不是好看的那份。
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    io.open(out_path, "w", encoding="utf-8", newline="\n").write(
        code_text if code_text.endswith("\n") else code_text + "\n")
    return out_path


def make_webp(png_path, out_path):
    from PIL import Image
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    nw = config.WEBP_WIDTH
    nh = round(h * nw / float(w))
    im.resize((nw, nh), Image.LANCZOS).save(
        out_path, "WEBP", quality=config.WEBP_QUALITY, method=5)
    return out_path


def _oneline(s):
    """压成一行，供 markdown 列表项使用。

    claims 里的 evidence 是网页原句，可能带换行、也可能带 markdown 记号 ——
    直接塞进列表项会把版面撑坏。这里只做最低限度的整形：合并空白、砍掉围栏。
    """
    return re.sub(r"\s+", " ", str(s or "").replace("```", "")).strip()


def make_text_md(meta, out_path):
    """文字副本。结构照搬现有 text/*.md，好让两边的文字页长得一样。"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rel = meta["filename"]
    lines = [
        "# {}".format(meta["serial"]),
        "",
        "- 日期：{}".format(meta["datetime"]),
        "- 风格：{}（S={}）".format(meta["style"], meta["S"]),
        "- 语言：{}".format(meta["lang"]),
        "- 冷知识领域：{}".format(meta["topic"]),
        "- 生成：{}（{}）".format(config.AI_LABEL, meta["model"]),
        "",
        "## 金句",
        "",
        "> {}".format(meta["quote"]),
        "",
        "## 冷知识",
        "",
        meta["fact"],
        "",
    ]
    if meta.get("source"):
        lines += ["来源：{}".format(meta["source"]), ""]

    # 背景：给渲染用的语感，不上卡。存档是因为它解释了这张卡为什么长这样。
    if (meta.get("context") or "").strip():
        lines += ["## 背景", "",
                  "*（不印在卡面上，只用来帮渲染决定构图与意象。）*", "",
                  meta["context"].strip(), ""]

    # 引用：模型选题时声称的证据。**这是事后核实点评唯一的输入** ——
    # 证据闸门 2026-08-12 下线，evidence.json 只活在 artifact 里（90 天，
    # 且不在提交白名单内），不落到这里就等于没有。
    claims = [c for c in (meta.get("claims") or []) if isinstance(c, dict)]
    if claims:
        lines += ["## 引用", "",
                  "*（模型选题时声称的证据，**未经程序校验**，留作事后核实。）*", ""]
        for i, c in enumerate(claims, 1):
            claim = _oneline(c.get("claim"))
            url = _oneline(c.get("url"))
            ev = _oneline(c.get("evidence"))
            lines.append("{}. {}".format(i, claim or "（未写明断言）"))
            if url:
                lines.append("   - 来源：<{}>".format(url))
            if ev:
                lines.append("   - 原句：{}".format(ev))
        lines.append("")

    # 看图判词：有视力那条线每一轮看完图说的话。**这是它视觉理解能力的证物** ——
    # 它说 ok 而图上确实有毛病，日后对照得出来。盲线没有这一节（它没眼睛，
    # 它的对应物是 lint 的读数），这一节空着本身就是产线形状的说明。
    crits = [c for c in (meta.get("critiques") or []) if isinstance(c, dict)]
    if crits:
        lines += ["## 看图自检", "",
                  "*（每轮渲染后模型自己看图给出的判词，原样存档。）*", ""]
        for c in crits:
            head = "**第 {} 轮** — ok={}".format(c.get("round", "?"), c.get("ok"))
            if c.get("style_fidelity") is not None:
                head += " · 风格贴合 {}/5".format(c["style_fidelity"])
            lines += [head, ""]
            for p in (c.get("problems") or []):
                if isinstance(p, dict):
                    lines.append("- {}：{}（建议：{}）".format(
                        _oneline(p.get("where")) or "?",
                        _oneline(p.get("what")) or "?",
                        _oneline(p.get("fix")) or "—"))
                else:
                    lines.append("- {}".format(_oneline(p)))
            if c.get("notes"):
                lines.append("- *总评：{}*".format(_oneline(c["notes"])))
            lines.append("")

    # 降级发布时遗留的问题。发出去的图永久不可覆盖（web/* 一年 immutable），
    # 所以这份记录必须和图同时落地，事后补不上。
    if meta.get("flags"):
        lines += ["## 降级发布", "",
                  "标记：`{}`".format(meta["flags"]), ""]
        probs = meta.get("problems") or []
        if probs:
            lines.append("发布时仍未解决的问题：")
            lines.append("")
            for p in probs:
                lines.append("- {}".format(_oneline(
                    p if not isinstance(p, dict) else p.get("what") or p)))
            lines.append("")

    lines += [
        "---",
        "图片：[原图](../../Cards/{}) ｜ [压缩版](../../web/{})".format(
            rel, rel.replace(".png", ".webp")),
        "",
    ]
    io.open(out_path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    return out_path


def append_ledger(meta):
    return ledger.append({
        "no": meta["no"], "datetime": meta["datetime"],
        "S": meta["S"], "style": meta["style"],
        "K": meta["K"], "topic": meta["topic"],
        "L": meta["L"], "lang": meta["lang"],
        "filename": meta["filename"],
        "quote": meta["quote"], "fact": meta["fact"], "source": meta["source"],
        "ai": config.AI_KEY, "model": meta["model"],
        # 过程记录。缺了不影响展出，所以一律 get 取值、给空默认 ——
        # 一个记不全的字段不该让整张卡发不出去。
        "slot": meta.get("slot", ""),
        "rounds": meta.get("rounds", ""),
        "research_attempts": meta.get("research_attempts", ""),
        "duration_s": meta.get("duration_s", ""),
        "sha256": meta.get("sha256", ""),
        "flags": meta.get("flags", ""),
        "fingerprint": meta.get("fingerprint", ""),
    })


def check_commit_allowlist(repo_root=None, expected=None):
    """已暂存的每一条路径都必须匹配白名单，否则抛错中止。

    必须用 -z 和 core.quotePath=false 取原始路径：
    git 默认会把非 ASCII 文件名加引号并转成八进制转义（港式霓虹招牌 ->
    \\346\\270\\257...），而风格简名恰恰都是中文。第一次真实发布就栽在这里 ——
    转义里的反斜杠被当成路径分隔符处理掉，正则再也匹配不上，
    于是守卫把自己该放行的文件拦了下来。
    """
    repo_root = repo_root or config.ROOT
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "diff", "--cached", "--name-only", "-z"],
        cwd=repo_root, capture_output=True)
    raw = out.stdout.decode("utf-8", "replace")
    paths = [p for p in raw.split("\0") if p.strip()]

    # 两层独立校验，都要过。以前是二选一（给了 expected 就不查白名单），
    # 那样算 expected 的代码一旦出错就没有兜底了 —— 而它的输入是模型产物
    # 派生出来的 row.json。两层的失效原因不相关，才叫纵深防御。
    #
    # 第一层：每条路径都必须落在自己的地盘里。
    bad = [p for p in paths if not re.match(config.COMMIT_ALLOW, p)]
    if bad:
        raise RuntimeError(
            "提交里出现了不该碰的路径，已中止：\n  - {}\n\n"
            "只允许 {d}/ 下的：Cards/{l}、web/YYYY-MM/*.webp、"
            "text/YYYY-MM/*.md、code/YYYY-MM/*.py\n"
            "尤其不能碰别人的 README.md、台账和图片 —— "
            "那会让对方的同步 rebase 冲突并停摆。".format(
                "\n  - ".join(bad), d=config.AI_DIR, l=config.LEDGER_NAME))

    # 第二层：暂存区必须**恰好**等于本次该写的那几条 —— 比模式匹配更严，
    # 不只挡住不该碰的，还挡住「多写了一个本不该有的文件」。
    if expected is not None:
        want, got = set(expected), set(paths)
        if want != got:
            raise RuntimeError(
                "暂存区与本次应写的文件对不上，已中止：\n"
                "  应写：{}\n"
                "  实际：{}\n"
                "  多出：{}\n"
                "  缺少：{}".format(
                    sorted(want), sorted(got),
                    sorted(got - want) or "无", sorted(want - got) or "无"))
    return paths
