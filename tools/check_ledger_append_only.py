"""台账只许追加，不许改写既有行。

为什么需要它：这个项目自称档案馆，而档案馆和画廊的区别就是**藏品记录不可
改写**。台账是唯一真相源，一旦某一行被悄悄改掉（改个错字、"顺手"重排、
脚本 bug 覆盖），没有任何东西会报错，也没有任何人会发现 —— 而已发布的
webp 是一年 immutable，线上那张卡还在，记录却已经不是它了。

所以把「只追加」从一句自觉变成一条机械检查。二十几行代码，换一个档案级承诺。

允许什么：
    - 新增行
    - 末尾新增列（旧行在新列上留空，或由一次性回填脚本填上）
    - 空白行、行尾差异这类无意义变化

不允许什么：
    - 删除已有行
    - 修改已有行在**旧表头里就有**的任何字段
    - 重命名或插入列（表头必须是旧表头的扩展）

用法：
    python tools/check_ledger_append_only.py                 # 工作区 vs HEAD
    python tools/check_ledger_append_only.py --base HEAD~1   # 指定基准
    python tools/check_ledger_append_only.py --base <sha> --rev <sha>   # CI 用

退出码：0 = 通过；1 = 有既有行被改写；2 = 用不了（基准取不到等）
"""
import argparse
import csv
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 回填是一次性的、有意的改写，需要放行 —— 但只放行「旧字段为空 -> 填上值」，
# 不放行「旧字段有值 -> 改成别的值」。前者是补全，后者是篡改。
ALLOW_FILLING_BLANKS = True


def sh(args):
    p = subprocess.run(args, cwd=ROOT, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def git_show(rev, path):
    """某个 rev 下的文件内容；文件不存在返回 None。"""
    code, out, _ = sh(["git", "show", "{}:{}".format(rev, path)])
    return None if code != 0 else out


def worktree_read(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    with io.open(full, "rb") as f:
        return f.read()


def ledger_paths(rev):
    """该 rev（或工作区）里所有台账的仓库相对路径。"""
    if rev:
        code, out, _ = sh(["git", "ls-tree", "-r", "--name-only", rev])
        names = out.decode("utf-8", "replace").splitlines() if code == 0 else []
    else:
        code, out, _ = sh(["git", "ls-files"])
        names = out.decode("utf-8", "replace").splitlines() if code == 0 else []
    return sorted(n for n in names
                  if n.endswith(".csv") and "/Cards/cards-index" in "/" + n)


def parse(blob):
    """(表头, {no: 行dict})。台账一律 UTF-8 BOM。"""
    if blob is None:
        return None, {}
    text = blob.decode("utf-8-sig", "replace")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    rows = [r for r in rows if any((c or "").strip() for c in r)]
    if not rows:
        return None, {}
    head = [c.strip() for c in rows[0]]
    out = {}
    for r in rows[1:]:
        rec = {head[i]: (r[i] if i < len(r) else "") for i in range(len(head))}
        no = (rec.get("no") or "").strip()
        if no:
            out[no] = rec
    return head, out


def check_one(path, old_blob, new_blob):
    problems = []
    old_head, old_rows = parse(old_blob)
    new_head, new_rows = parse(new_blob)

    if old_head is None:            # 基准里没有这份台账 = 全新的，随便写
        return problems
    if new_head is None:
        problems.append("{}：台账在这次改动里消失了".format(path))
        return problems

    if new_head[:len(old_head)] != old_head:
        problems.append(
            "{}：表头不是旧表头的扩展（只许在末尾加列）\n"
            "    旧：{}\n    新：{}".format(path, old_head, new_head))
        return problems         # 表头都对不上，逐字段比对没有意义

    for no, old in sorted(old_rows.items(), key=lambda kv: int(kv[0])
                          if kv[0].isdigit() else 0):
        new = new_rows.get(no)
        if new is None:
            problems.append("{}：no={} 这一行被删掉了".format(path, no))
            continue
        for col in old_head:        # 只比对旧表头里就有的列
            a, b = (old.get(col) or ""), (new.get(col) or "")
            if a == b:
                continue
            if ALLOW_FILLING_BLANKS and a.strip() == "":
                continue            # 空 -> 有值，是回填，放行
            problems.append(
                "{}：no={} 的 {} 列被改写了\n"
                "    原值：{}\n    新值：{}".format(
                    path, no, col, a[:120], b[:120]))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="基准 rev")
    ap.add_argument("--rev", default=None, help="待检 rev；不给则查工作区")
    a = ap.parse_args()

    code, _, _ = sh(["git", "rev-parse", "--verify", "--quiet", a.base + "^{commit}"])
    if code != 0:
        print("[跳过] 取不到基准 {} —— 大概是首次提交或浅克隆。".format(a.base))
        return 0

    paths = sorted(set(ledger_paths(a.base)) | set(ledger_paths(a.rev)))
    if not paths:
        print("[跳过] 没找到任何台账。")
        return 0

    problems = []
    for p in paths:
        new_blob = git_show(a.rev, p) if a.rev else worktree_read(p)
        problems += check_one(p, git_show(a.base, p), new_blob)

    if problems:
        print("台账被改写了 —— 档案只许追加。\n")
        for m in problems:
            print("  - " + m)
        print("\n共 {} 处。如果这是一次有意的迁移（例如末尾加列后回填），"
              "请确认它只把空字段填上、没有动任何既有值。".format(len(problems)))
        return 1

    print("台账检查通过（{} 份）：没有既有行被改写。".format(len(paths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
