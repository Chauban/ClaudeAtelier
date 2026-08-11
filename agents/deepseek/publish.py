"""发布：压缩版 webp、文字副本 md、台账追加、以及提交路径白名单校验。

**绝不触碰** README.md、Cards/cards-index.csv、任何 NO.* 文件。
那三样是 Claude 的写入面；两边同时写会让 sync-to-github.bat 的
pull --rebase 冲突并 goto FAIL，卡片静默积压 —— 那正是 2026-08-05
（4 张卡 20 小时）和 08-08（3 张卡）两次事故的形状。
白名单是机械执行的，不靠自觉。
"""
import io
import os
import re
import subprocess

import config
import ledger


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
    if expected is not None:
        # 统一连号之后，DeepSeek 的文件名也是 NO.*，靠前缀已经分不出两家。
        # 改成校验「暂存区恰好等于本次该写的那几条路径」—— 比模式匹配更严：
        # 不只挡住不该碰的，还挡住「多写了一个本不该有的文件」。
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
    bad = [p for p in paths if not re.match(config.COMMIT_ALLOW, p)]
    if bad:
        raise RuntimeError(
            "提交里出现了不该碰的路径，已中止：\n  - {}\n\n"
            "只允许：Cards/cards-index-deepseek.csv、web/YYYY-MM/DS.*.webp、"
            "text/YYYY-MM/DS.*.md\n"
            "尤其不能碰 README.md、Cards/cards-index.csv 和任何 NO.* 文件 —— "
            "那会让 Claude 侧的同步 rebase 冲突并停摆。".format("\n  - ".join(bad)))
    return paths
