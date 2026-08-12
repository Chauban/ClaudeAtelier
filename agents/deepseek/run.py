"""编排入口：把该由代码决定的全部定死，只把创作留给模型。

    run.py 决定      K、L、S、编号、文件名、日期、画布倍率、字体、输出路径
    模型决定         金句、冷知识、来源与证据、渲染脚本

「抽到的 S 是强制的」因此从一句反复强调的祈使句，变成了程序事实 ——
模型被告知 S，从头到尾看不到其他选项，没有退回舒适区的可能。

失败一律 fail closed：什么都不发布。_headers 让 web/* 一年 immutable，
发出去的图**永久不可覆盖**，所以宁可空一班。
"""
import argparse
import io
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import compose        # noqa: E402
import config         # noqa: E402
import ledger         # noqa: E402
import publish        # noqa: E402
import research       # noqa: E402
import tables         # noqa: E402


def freshness_ok(max_age_hours=3):
    """本班次是否该跑。GitHub cron 常迟到、偶尔重复触发，
    用「上一张卡多久以前」来判断，比指望定时器准点可靠。"""
    last = ledger.last_datetime()
    if not last:
        return True, "台账为空，首次运行"
    try:
        # 台账写的是 UTC+8 挂钟时间。不能用 mktime —— 它按本机时区解释，
        # 在 UTC 的 runner 和 UTC+8 的开发机上会差 8 小时。timegm 固定按
        # UTC 解释再减偏移，与本机时区无关。
        import calendar
        epoch = calendar.timegm(
            time.strptime(last, "%Y-%m-%d %H:%M")) - config.TZ_OFFSET_HOURS * 3600
    except Exception:
        return True, "台账时间解析不了，照常运行"
    age = (time.time() - epoch) / 3600.0
    if age < max_age_hours:
        return False, "上一张卡是 {:.1f} 小时前（{}），还太新，跳过".format(age, last)
    return True, "上一张卡是 {:.1f} 小时前".format(age)


def build_brief(seed=None, force_style=None):
    rng = random.Random(seed)
    n = ledger.slot_now()
    K, L = ledger.kl_from_clock(n)
    S, style_name, pool = (force_style, tables.style(force_style), 1) if force_style \
        else ledger.pick_style(rng, n)
    # 本班是不是共享风格班。只影响日志和交接文案，不影响取值。
    shared = force_style is None and ledger.shared_style_for(n) is not None
    lang_name = tables.lang(L)
    if L == 7:
        lang_name, code = ledger.pick_lang7(rng)
    else:
        code = tables.LANG_CODE[L]
    dt, ym, ymd = ledger.local_now()
    no = ledger.next_no()
    serial = ledger.serial(no)
    fname = "{}_{}_S{}-{}_{}.png".format(
        serial, ymd, S, tables.short_style_name(style_name), code)
    return {
        "no": no, "SERIAL": serial, "DATE": ymd, "datetime": dt, "ym": ym,
        # 班次 N。K/L 本来就是从它算出来的，只是此前没有落到台账里 ——
        # 前端只好用 datetime+K+L 反解，而那容许不了 Actions 迟到超过 2 小时。
        "slot": n, "SHARED_STYLE": shared,
        "K": K, "TOPIC": tables.topic(K),
        "L": L, "LANG": lang_name, "LANG_CODE": code,
        "STYLE_NO": S, "STYLE_NAME": style_name, "style_pool": pool,
        "filename": "{}/{}".format(ym, fname),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out", help="产物目录")
    ap.add_argument("--dry-run", action="store_true", help="只生成，不写台账不发布")
    ap.add_argument("--force-style", type=int, help="调试用：指定 S")
    ap.add_argument("--skip-freshness", action="store_true")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()

    # 台账的 datetime 是**开工**时刻（build_brief 在核实和渲染之前就取好了），
    # 所以这里从进程起点计时，duration_s 与它相加才是完工时刻。
    t0 = time.time()

    os.makedirs(a.out, exist_ok=True)

    def status(v):
        """把「这一班做了什么」写给 workflow 看。

        「本班不该出卡」和「本班出卡失败」是两回事，workflow 必须能分开：
        没有这个标记，新鲜度跳过时 out/publish/ 是空的，上传产物那步的
        if-no-files-found: error 会把一次正确的跳过判成失败。
        """
        io.open(os.path.join(a.out, "status.txt"), "w", encoding="utf-8").write(v)
        return v

    if not a.skip_freshness:
        ok, why = freshness_ok()
        print("[新鲜度] {}".format(why))
        if not ok:
            status("skipped")
            return 0

    brief = build_brief(a.seed, a.force_style)
    print("[本次] {} · S{} {} · {} · {}（S 候选 {} 种）".format(
        brief["SERIAL"], brief["STYLE_NO"], brief["STYLE_NAME"],
        brief["LANG"], brief["TOPIC"], brief["style_pool"]))
    if brief["SHARED_STYLE"]:
        print("[共享风格班] 本班 S 由班次号算出，各产出方拿到的是同一个 S —— "
              "这一班的唯一变量是执笔者本身。")

    orig_dir = os.path.join(a.out, "original")
    pub_dir = os.path.join(a.out, "publish")
    os.makedirs(orig_dir, exist_ok=True)
    os.makedirs(pub_dir, exist_ok=True)
    png_path = os.path.join(orig_dir, os.path.basename(brief["filename"]))

    # ---------------------------------------------------------- 一、选题核实
    print("\n[1/3] 选题与核实")
    payload, report = research.run(brief)
    brief["QUOTE"] = payload["quote"]
    brief["FACT"] = payload["fact"]
    brief["OUT_PATH"] = png_path.replace("\\", "/")
    print("  金句：{}".format(payload["quote"][:60]))
    print("  冷知识：{}".format(payload["fact"][:60]))
    print("  来源：{}".format(payload["source"]))

    # ---------------------------------------------------------- 二、渲染
    print("\n[2/3] 渲染")
    res = compose.run(brief, os.path.join(a.out, "work"))
    if not res.get("ok"):
        print("\n渲染在 {} 轮内没能通过检查。本班次不发布任何东西。".format(res["rounds"]))
        status("render-failed")
        return 1
    print("  {} 轮通过：{}".format(res["rounds"], png_path))

    # ---------------------------------------------------------- 三、产出
    print("\n[3/3] 产出")
    meta = {
        "no": brief["no"], "serial": brief["SERIAL"], "datetime": brief["datetime"],
        "S": brief["STYLE_NO"], "style": brief["STYLE_NAME"],
        "K": brief["K"], "topic": brief["TOPIC"],
        "L": brief["L"], "lang": brief["LANG"],
        "filename": brief["filename"],
        "quote": payload["quote"], "fact": payload["fact"],
        "source": payload["source"],
        # 服务端回声的具体版本优先；拿不到才退回请求时用的别名。
        "model": res.get("model") or config.MODEL,
        # ---- 过程记录
        "slot": brief["slot"],
        "rounds": res.get("rounds", ""),
        "research_attempts": report.get("attempts", ""),
        "sha256": publish.sha256_file(png_path),
        # duration_s 最后再算：要把 webp、文字副本、手稿都算进去。
    }
    webp_rel = brief["filename"].replace(".png", ".webp")
    md_rel = brief["filename"].replace(".png", ".md")
    code_rel = brief["filename"].replace(".png", ".py")

    publish.make_webp(png_path, os.path.join(pub_dir, "web", webp_rel))
    publish.make_text_md(meta, os.path.join(pub_dir, "text", md_rel))
    publish.make_code(res.get("code") or "", os.path.join(pub_dir, "code", code_rel))
    # 必须在写 row.json 之前定下来：CI 的 publish job 是拿 row.json 去追加台账的，
    # 这里漏了，台账那一列就永远是空的。
    meta["duration_s"] = int(round(time.time() - t0))

    io.open(os.path.join(pub_dir, "row.json"), "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1))
    io.open(os.path.join(pub_dir, "evidence.json"), "w", encoding="utf-8").write(
        json.dumps({"claims": report["claims"],
                    "unsupported_tokens": report.get("unsupported_tokens", [])},
                   ensure_ascii=False, indent=1))

    if a.dry_run:
        print("  --dry-run：产物已生成在 {}，未写台账。".format(pub_dir))
        status("dry-run")
        return 0

    # 原图先落袋：丢原图违反「原图必须在本地」这条第一约束，丢台账行不会。
    print("  原图 {}".format(png_path))
    print("  压缩 {}".format(webp_rel))
    print("  文字 {}".format(md_rel))
    print("  手稿 {}".format(code_rel))
    print("  台账 {}".format(publish.append_ledger(meta)))
    print("  过程 第 {} 轮通过 · 核实第 {} 次过 · 用时 {}s · {}".format(
        meta["rounds"], meta["research_attempts"],
        meta["duration_s"], meta["model"]))
    status("published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
