"""一次性回填：给已发布的行补上新加的那几列。

2026-08-12 台账末尾加了 slot / rounds / research_attempts / duration_s / sha256。
新卡由 run.py 直接写；已经发出去的那几张只能事后补，而且只有两列补得回来：

    slot    可以从 datetime + K + L 反解 —— 两个同余式同时成立，周期
            lcm(17,7)=119 小时，蒙中的概率约 1/119，实际是解方程不是猜。
    sha256  原图还在本地就能算。

rounds / research_attempts / duration_s **补不回来**，当时没记。留空，
不要瞎填 —— 档案里「不知道」和「是 0」是两回事。

只动 AI_REGISTRY 里各家自己的台账，**绝不碰根目录 Claude 那份**。

    python tools/backfill_ledger.py            # 先看会改什么（不写）
    python tools/backfill_ledger.py --apply    # 真的写
"""
import argparse
import csv
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agents", "deepseek"))

TZ_OFFSET = 8
SLOT_HOURS = 4
DRIFT = [0, -1, 1, -2, 2, -3, 3]      # 小时步长，与前端 slotOf 同口径


def solve_slot(dt, K, L):
    """从 datetime(UTC+8) + K + L 反解出题用的那个 N。解不出返回 None。

    **slot 记的是「出题用的 N」，不是「这张卡该属于哪一班」。** 两者对新卡
    是同一个值（slot_now 向下取整到 4 小时边界），但对 2026-08-12 之前的卡
    不是：那时 K/L 直接按当前小时算，Actions 一迟到就会算出非边界的 N。

    NO.0004 就是这么来的 —— K=4 L=7 对应 N=496250，496250 % 4 == 2，
    不在任何班次边界上。它正是 HANDOFF 第 6.1 节记的那张「谁也配不上的孤卡」。

    所以这里按小时步长搜，不按班次步长搜：非边界值不是解错了，它就是答案，
    而且是那次班次漂移事故留下的唯一直接物证。写下 496250 是记录，
    改写成 496248 是**伪造一次从未发生的配对** —— 那一班没有别的卡与它同题。
    档案不修补藏品，对不上本身就是记录。
    """
    import calendar
    import time
    try:
        epoch = calendar.timegm(time.strptime(dt.strip()[:16], "%Y-%m-%d %H:%M"))
    except Exception:
        return None
    n0 = epoch // 3600 - TZ_OFFSET
    for d in DRIFT:
        n = n0 + d
        if n % 17 + 1 == K and n % 7 + 1 == L:
            return n
    return None


def run(ai_env, apply):
    os.environ["ATELIER_AI"] = ai_env
    for m in ("config", "ledger", "publish"):
        sys.modules.pop(m, None)                # 换租户要重新加载配置
    import config
    import ledger
    import publish

    path = config.LEDGER
    print("\n=== {} ({})".format(config.AI_LABEL, os.path.relpath(path, ROOT)))
    if not os.path.exists(path):
        print("  台账还不存在，跳过。")
        return 0

    if apply:
        if ledger.ensure_header(path):
            print("  表头已补齐到 {} 列".format(len(config.COLUMNS)))

    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head = [c.strip() for c in rows[0]]
    body = [r for r in rows[1:] if any((c or "").strip() for c in r)]

    idx = {c: i for i, c in enumerate(head)}
    width = len(config.COLUMNS)
    changed = 0
    out = []
    for r in body:
        r = list(r) + [""] * (width - len(r))
        get = lambda c: (r[idx[c]] if c in idx and idx[c] < len(r) else "").strip()  # noqa: E731

        def put(col, val):
            nonlocal changed
            i = config.COLUMNS.index(col)
            if r[i].strip() == "" and val not in (None, ""):
                r[i] = str(val)
                print("    no={} {} <- {}".format(get("no"), col, str(val)[:20]))
                changed += 1

        if get("slot") == "":
            try:
                n = solve_slot(get("datetime"), int(get("K")), int(get("L")))
            except Exception:
                n = None
            if n is None:
                print("    no={} slot 解不出 —— K/L 是人工指定的，留空".format(get("no")))
            else:
                if n % SLOT_HOURS:
                    print("    no={} slot={} 不在班次边界上 —— "
                          "这是 08-12 班次漂移留下的孤卡，照实记".format(get("no"), n))
                put("slot", n)

        if get("sha256") == "":
            png = os.path.join(config.CARDS_DIR, get("filename").replace("/", os.sep))
            if os.path.exists(png):
                put("sha256", publish.sha256_file(png))
            else:
                print("    no={} 本地找不到原图，sha256 留空：{}".format(
                    get("no"), get("filename")))
        out.append(r)

    if not apply:
        print("  （预演）会补 {} 处。加 --apply 才真写。".format(changed))
        return changed

    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(config.COLUMNS)
        for r in out:
            w.writerow(r)
    os.replace(tmp, path)
    print("  已补 {} 处，共 {} 行。".format(changed, len(out)))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    os.environ.setdefault("ATELIER_AI", "flash")
    sys.path.insert(0, os.path.join(ROOT, "agents", "deepseek"))
    import config
    names = sorted(config.AI_REGISTRY)

    total = 0
    for n in names:
        total += run(n, a.apply)
    print("\n合计 {} 处{}。".format(total, "" if a.apply else "（预演）"))
    if a.apply:
        print("接着跑：python tools/check_ledger_append_only.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
