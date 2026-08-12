"""publish job 用：把 artifact 里的发布物落到仓库，并守住提交路径白名单。

这一段**只跑仓库自有代码**，不执行任何模型产物 —— 它是唯一拿到
contents:write 的地方，所以必须干净。
"""
import argparse
import io
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config    # noqa: E402
import ledger    # noqa: E402
import publish   # noqa: E402


def place(incoming):
    row = json.load(io.open(os.path.join(incoming, "row.json"), encoding="utf-8"))
    moved = []
    for sub, root in (("web", config.WEB_DIR), ("text", config.TEXT_DIR),
                      ("code", config.CODE_DIR)):
        src_root = os.path.join(incoming, sub)
        if not os.path.isdir(src_root):
            continue
        for dirpath, _, files in os.walk(src_root):
            for fn in files:
                src = os.path.join(dirpath, fn)
                rel = os.path.relpath(src, src_root)
                dst = os.path.join(root, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                # 绝不原地覆盖已发布的图：_headers 让 web/* 一年 immutable，
                # 覆盖了 CDN 也不会重新取，只会造成线上线下不一致。
                if os.path.exists(dst):
                    raise RuntimeError(
                        "目标已存在，拒绝覆盖：{}\n"
                        "  web/* 是 immutable 缓存，文件名带编号本就该唯一。"
                        "出现同名说明发号逻辑出了问题，先查清楚。".format(dst))
                shutil.copy2(src, dst)
                moved.append(dst)

    if any(str(r.get("no")) == str(row["no"]) for r in ledger.load_own()):
        raise RuntimeError(
            "台账里已经有 no={} 了，拒绝重复写入。".format(row["no"]))
    moved.append(publish.append_ledger(row))

    msg = "{} · {} · {}".format(row["serial"], row["style"], row["lang"])
    io.open(os.path.join(incoming, "commit_msg.txt"), "w",
            encoding="utf-8", newline="\n").write(msg + "\n")
    print("已落地 {} 个文件".format(len(moved)))
    for m in moved:
        print("  " + os.path.relpath(m, config.ROOT).replace("\\", "/"))
    print("提交信息：" + msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incoming")
    ap.add_argument("--check-staged", action="store_true")
    a = ap.parse_args()
    if a.check_staged:
        # 统一连号后文件名也是 NO.*，靠前缀分不出两家，改成校验
        # 「暂存区恰好等于本次该写的那三条」。incoming/row.json 是权威来源。
        expected = None
        if a.incoming:
            row = json.load(io.open(os.path.join(a.incoming, "row.json"),
                                    encoding="utf-8"))
            rel = row["filename"]
            b = config.AI_DIR + "/"
            expected = [b + "Cards/" + config.LEDGER_NAME,
                        b + "web/" + rel.replace(".png", ".webp"),
                        b + "text/" + rel.replace(".png", ".md"),
                        b + "code/" + rel.replace(".png", ".py")]
        paths = publish.check_commit_allowlist(expected=expected)
        print("暂存区 {} 条路径，与本次应写的完全一致：".format(len(paths)))
        for p in paths:
            print("  " + p)
        return 0
    if not a.incoming:
        ap.error("要么 --incoming，要么 --check-staged")
    place(a.incoming)
    return 0


if __name__ == "__main__":
    sys.exit(main())
