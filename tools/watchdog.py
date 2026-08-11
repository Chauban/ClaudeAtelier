"""巡检：每条产线是不是还在出卡。

这个项目最贵的教训不是「哪里写错了」，而是**失败是无声的**：
2026-08-05 沙箱留下的 git 锁让 Windows 侧连续五次同步全部失败，四张卡
积压近 20 小时才被发现；08-08 又因远端有未合并的提交，连挂三次。两次
都是等人注意到网站不更新才知道。

所以这里不看「有没有报错」，只看一件事：**每条产线最新那张卡有多旧**。
不管是沙箱留了锁、Windows 计划任务没跑、gh 登录过期、还是 Actions 被
限流，症状都一样 —— 卡不再出现。用症状做判据，比逐个监控环节可靠。

只读，不改任何东西。退出码：0 = 都新鲜；1 = 有产线卡住了。
"""
import argparse
import calendar
import csv
import glob
import io
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ_OFFSET = 8               # 台账 datetime 写的是本地时间（UTC+8）
STALE_HOURS = 10.0          # 4 小时一班，超过 10 小时 = 连丢两班以上


def ledgers():
    out = [("claude", os.path.join(ROOT, "Cards", "cards-index.csv"))]
    for p in sorted(glob.glob(os.path.join(ROOT, "*", "Cards", "cards-index*.csv"))):
        out.append((os.path.basename(os.path.dirname(os.path.dirname(p))), p))
    return [(n, p) for n, p in out if os.path.exists(p)]


def newest(path):
    try:
        with io.open(path, encoding="utf-8-sig", newline="") as f:
            rows = [r for r in csv.DictReader(f) if (r.get("datetime") or "").strip()]
    except Exception as e:
        return None, "台账读不了：{}".format(e)
    if not rows:
        return None, "台账是空的"
    rows.sort(key=lambda r: r["datetime"])
    last = rows[-1]
    try:
        # 台账写的是 UTC+8 的挂钟时间。**不能用 mktime** —— 它按本机时区
        # 解释，脚本在 UTC 的 runner 和 UTC+8 的本机上会给出差 8 小时的
        # 两个答案。timegm 固定按 UTC 解释，再减去偏移，与本机时区无关。
        epoch = calendar.timegm(
            time.strptime(last["datetime"].strip(), "%Y-%m-%d %H:%M")) - TZ_OFFSET * 3600
    except Exception:
        return None, "最后一行的时间解析不了：{!r}".format(last["datetime"])
    return (time.time() - epoch) / 3600.0, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-hours", type=float, default=STALE_HOURS)
    a = ap.parse_args()

    lines, stalled = [], []
    for name, path in ledgers():
        age, info = newest(path)
        if age is None:
            # 空台账不算故障：新接入的产线还没出过卡
            lines.append("  {:16s} {}".format(name, info))
            continue
        mark = "停摆" if age > a.stale_hours else "正常"
        lines.append("  {:16s} {}  最新 NO.{} {}（{:.1f} 小时前）".format(
            name, mark, info.get("no"), info.get("datetime"), age))
        if age > a.stale_hours:
            stalled.append((name, age, info.get("datetime"), info.get("no")))

    print("产线巡检（阈值 {:.0f} 小时）".format(a.stale_hours))
    print("\n".join(lines))

    if stalled:
        print("\n以下产线已停摆：")
        for name, age, dt, no in stalled:
            print("  {} —— 最新一张是 NO.{}（{}），已 {:.1f} 小时没有新卡".format(
                name, no, dt, age))
        print("\n排查顺序（按历史事故的频率）：")
        print("  claude   1) find .git -name '*.lock'  沙箱留下的锁会让同步全部失败")
        print("           2) tail -20 sync.log        看推送是成功还是 rebase 冲突")
        print("           3) 电脑是否开着、计划任务是否还在")
        print("  其他产线 1) Actions 页面看最近几次运行")
        print("           2) 搜索被限流时会跳过本班次，日志里会写明")
        return 1
    print("\n全部正常。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
