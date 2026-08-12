"""一次运行花了多少钱 —— 按阶段记账。

为什么要有它：2026-08-12 第一张 K3 卡花了 14 元，而当时日志里只有输出 token，
「钱花在哪个阶段」完全看不出来，只能靠估。一条每 4 小时跑一次、跑很多年的
产线，成本必须是可见的量，不是事后拍脑袋。

单价放在 config.PROVIDERS 里（元 / 百万 token）。**拿不到单价就只报 token 数，
不瞎算钱** —— 报一个错的数字比不报更糟。
"""
import config

_ROWS = []


def record(stage, meta):
    """记一次调用。stage: research / render / critique / preflight …"""
    _ROWS.append({
        "stage": stage,
        "in": meta.get("in") or 0,
        "cached": meta.get("cached") or 0,
        "out": meta.get("out") or 0,
        "reasoning": meta.get("reasoning") or 0,
        "sec": meta.get("sec") or 0,
    })


def totals():
    t = {"calls": len(_ROWS), "in": 0, "cached": 0, "out": 0, "reasoning": 0, "sec": 0.0}
    for r in _ROWS:
        for k in ("in", "cached", "out", "reasoning"):
            t[k] += r[k]
        t["sec"] += r["sec"]
    return t


def _price():
    p = (config.PROVIDERS.get(config.PROVIDER) or {}).get("price") or {}
    if all(k in p for k in ("in_miss", "in_hit", "out")):
        return p
    return None


def cost(t=None):
    """返回 (金额, 币种)；没有单价表就返回 (None, None)。"""
    t = t or totals()
    p = _price()
    if not p:
        return None, None
    miss = max(0, t["in"] - t["cached"])
    amount = (miss * p["in_miss"] + t["cached"] * p["in_hit"]
              + t["out"] * p["out"]) / 1e6
    return round(amount, 2), p.get("unit", "元")


def report():
    t = totals()
    by = {}
    for r in _ROWS:
        b = by.setdefault(r["stage"], {"calls": 0, "in": 0, "cached": 0, "out": 0})
        b["calls"] += 1
        for k in ("in", "cached", "out"):
            b[k] += r[k]

    lines = ["  {:<10} {:>5} {:>10} {:>10} {:>9}".format(
        "阶段", "次数", "输入", "其中缓存", "输出")]
    for stage, b in sorted(by.items(), key=lambda kv: -kv[1]["in"]):
        lines.append("  {:<10} {:>5} {:>10,} {:>10,} {:>9,}".format(
            stage, b["calls"], b["in"], b["cached"], b["out"]))
    hit = (100.0 * t["cached"] / t["in"]) if t["in"] else 0.0
    lines.append("  {:<10} {:>5} {:>10,} {:>10,} {:>9,}".format(
        "合计", t["calls"], t["in"], t["cached"], t["out"]))
    lines.append("  缓存命中率 {:.0f}%（命中价通常是未命中的十分之一，"
                 "这个数就是成本的头号变量）".format(hit))
    amount, unit = cost(t)
    if amount is not None:
        lines.append("  估算成本 {:.2f} {}".format(amount, unit))
    else:
        lines.append("  （该厂商没配单价表，只报 token 不估价）")
    return "\n".join(lines)
