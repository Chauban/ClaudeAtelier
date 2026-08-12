"""台账与本地原图对账。

为什么需要：卡片的原图是这个项目唯一不可再生的东西 —— 台账行、webp、
文字副本都在 git 里，丢了能找回来；原图只在这台电脑上。DeepSeek 那边
更险：原图先存在 GitHub artifact 里，**只保留 90 天**，取回任务没跑到
就是永久丢失，而且丢得无声无息。

这个脚本把「有没有丢」变成一条随时可跑的命令。只读，不改任何东西。

    python tools/check_originals.py
    python tools/check_originals.py --quiet    # 只在有问题时输出（给计划任务用）

退出码：0 = 没问题；1 = 有台账行找不到对应原图
"""
import argparse
import csv
import glob
import io
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DAYS = 90          # GitHub artifact 保留期
WARN_DAYS = 75              # 离过期还剩这么多天就该催了


def ledgers():
    """[(展区名, 台账路径, 该展区的根目录)]。根目录下的那份属于 Claude。"""
    out = [("claude", os.path.join(ROOT, "Cards", "cards-index.csv"), ROOT)]
    for p in sorted(glob.glob(os.path.join(ROOT, "*", "Cards", "cards-index*.csv"))):
        base = os.path.dirname(os.path.dirname(p))
        out.append((os.path.basename(base), p, base))
    return [(n, p, b) for n, p, b in out if os.path.exists(p)]


def read(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if (r.get("no") or "").strip()]


def age_days(dt_str):
    try:
        t = time.mktime(time.strptime(dt_str.strip(), "%Y-%m-%d %H:%M"))
    except Exception:
        return None
    return (time.time() - t) / 86400.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true",
                    help="只在发现问题时输出，适合挂计划任务")
    a = ap.parse_args()

    lines, missing_total, orphan_total, urgent = [], 0, 0, []

    for name, ledger_path, base in ledgers():
        rows = read(ledger_path)
        cards_dir = os.path.join(base, "Cards")

        # 台账有行，本地有没有图
        missing = []
        for r in rows:
            rel = (r.get("filename") or "").strip().replace("/", os.sep)
            if not rel:
                continue
            if not os.path.exists(os.path.join(cards_dir, rel)):
                d = age_days(r.get("datetime") or "")
                missing.append((r.get("no"), rel, d))
                if d is not None and d >= WARN_DAYS:
                    urgent.append((name, r.get("no"), d))

        # 本地有图，台账有没有行。两个下划线目录不参与对账 —— 它们本来就
        # 不在编号序列里：
        #   _retired  刻意退休、被取代的稿子
        #   _orphans  生成成功、原图也取回来了，但没进台账的（发布那步没跑成）
        # 都留着不删：图还在就是记录，删了才是丢档案。但它们不该再触发告警，
        # 也不该继续占着 2026-08/ 里的位置 —— 那个序号迟早会被下一张卡用掉。
        on_disk, parked = set(), []
        for p in glob.glob(os.path.join(cards_dir, "*", "*.png")):
            rel = os.path.relpath(p, cards_dir).replace(os.sep, "/")
            if rel.startswith("_retired/") or rel.startswith("_orphans/"):
                parked.append(rel)
                continue
            on_disk.add(rel)
        in_ledger = {(r.get("filename") or "").strip() for r in rows}
        orphans = sorted(on_disk - in_ledger)

        missing_total += len(missing)
        orphan_total += len(orphans)

        lines.append("[{}] 台账 {} 行 · 本地原图 {} 张".format(
            name, len(rows), len(on_disk)))
        if missing:
            lines.append("  缺原图 {} 张：".format(len(missing)))
            for no, rel, d in missing[:20]:
                tag = ""
                if d is not None:
                    left = ARTIFACT_DAYS - d
                    tag = "（{:.0f} 天前，artifact 还剩约 {:.0f} 天）".format(d, left) \
                        if left > 0 else "（{:.0f} 天前，**artifact 多半已过期**）".format(d)
                lines.append("    NO.{:<5} {} {}".format(no, rel, tag))
            if len(missing) > 20:
                lines.append("    …… 另有 {} 张".format(len(missing) - 20))
        if orphans:
            lines.append("  有图但台账里没有 {} 张（多半是失败运行留下的）：".format(len(orphans)))
            for rel in orphans[:10]:
                lines.append("    " + rel)
            lines.append("    → 确认不发布的话，挪进 Cards/_orphans/ 就不再报了。")
        # 只报个数，不当问题。存着是有意的，看得见就够了。
        if parked:
            lines.append("  另有 {} 张存在 _retired/ _orphans/，不参与对账。".format(
                len(parked)))

    ok = missing_total == 0
    if urgent:
        lines.append("")
        lines.append("!! 以下缺口临近 artifact 过期，再不取回就永久丢失：")
        for name, no, d in urgent:
            lines.append("   [{}] NO.{}  已 {:.0f} 天".format(name, no, d))
    lines.append("")
    lines.append("合计：缺原图 {} 张 · 孤儿原图 {} 张".format(missing_total, orphan_total))
    if ok and not orphan_total:
        lines.append("对账通过：每一行台账都有对应的本地原图。")

    if not a.quiet or not ok or urgent:
        print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
