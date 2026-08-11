"""把 Actions 生成的原图 PNG 取回本地 Cards/。

为什么需要它：卡片生成在一次性容器里，原图随容器消失。而「原图必须留在
本地电脑」是这个项目的第一约束，所以 runner 把 PNG 传成 artifact，由这边
定时拉回来。artifact 保留 90 天 —— **电脑关机超过 90 天，原图就永久没了**。

为什么用 Python 而不是纯 .bat：要解析 gh 的 JSON 输出。批处理里做这件事
既难写又易错，而这台机器上有 Python 3.12。.bat 只当一层壳。

今天踩到并写进代码的教训：
    第一次手工拉取时，下载被 Azure blob 的 EOF 中断、目录是空的，
    而 `for f in dir/*.png` 在没匹配时把字面量当文件名，照样打印了
    「已取回」。**下载失败必须能被识别**，不能靠「循环没报错」当成功。
    所以这里每一步都数文件、核大小，拿不到就明说拿不到。
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DIR = "deepseekv4flash"     # 与 agents/deepseek/config.py 的 AI_DIR 一致
REPO = "Chauban/ClaudeAtelier"
WORKFLOW = "deepseek-card.yml"
STATE = os.path.join(ROOT, ".ds-fetch-state.json")
LOG = os.path.join(ROOT, "fetch-ds.log")
MAX_ATTEMPTS = 3          # 同一个 run 累计失败这么多次就放弃，并明确报出来
DOWNLOAD_RETRIES = 3      # 单次调用内的重试


def log(msg):
    line = "[{}] {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    try:
        with io.open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(io.open(STATE, encoding="utf-8"))
        except Exception:
            log("状态文件读不了，当作空的重新开始")
    return {"done": {}, "attempts": {}, "failed": {}}


def save_state(s):
    io.open(STATE, "w", encoding="utf-8").write(
        json.dumps(s, ensure_ascii=False, indent=1))


def gh(args, capture=True):
    return subprocess.run(["gh"] + args, cwd=ROOT, capture_output=capture,
                          text=True, encoding="utf-8", errors="replace")


def check_gh():
    r = gh(["auth", "status"])
    if r.returncode != 0:
        log("gh 未登录或不可用。注意：gh 的凭据按 Windows 用户存 —— "
            "如果这个计划任务以 SYSTEM 身份运行，它永远找不到 token，"
            "会静默什么都不做。请确认任务是以你本人的账户运行的。")
        log((r.stderr or r.stdout or "").strip()[:300])
        return False
    return True


def list_runs(limit=20):
    r = gh(["run", "list", "--repo", REPO, "--workflow", WORKFLOW,
            "--status", "success", "--limit", str(limit),
            "--json", "databaseId,createdAt"])
    if r.returncode != 0:
        log("列出运行失败：{}".format((r.stderr or "").strip()[:200]))
        return []
    try:
        return json.loads(r.stdout or "[]")
    except Exception as e:
        log("解析运行列表失败：{}".format(e))
        return []


def was_published(run_id):
    """这次运行是否真的发布了卡片。

    必须查，不能只看整体 conclusion：dry_run 触发时 publish job 是 skipped，
    整个 run 照样报 success，而「上传原图」那步是 if: always()，所以演习也会
    留下 artifact。不过滤的话，本地 Cards/ 会堆满从未发布、台账里也查不到的
    孤儿原图 —— 正是要避免的那种对不上。
    """
    r = gh(["run", "view", str(run_id), "--repo", REPO, "--json", "jobs"])
    if r.returncode != 0:
        return None                      # 查不到就先别下结论，下次再说
    try:
        jobs = json.loads(r.stdout or "{}").get("jobs", [])
    except Exception:
        return None
    for j in jobs:
        if j.get("name") == "publish":
            return j.get("conclusion") == "success"
    return False


def download(run_id, dest):
    """返回取回的 png 路径列表。失败返回 []（并已记日志）。"""
    name = "original-{}".format(run_id)
    for i in range(1, DOWNLOAD_RETRIES + 1):
        r = gh(["run", "download", str(run_id), "--repo", REPO,
                "--name", name, "--dir", dest])
        if r.returncode == 0:
            break
        err = ((r.stderr or "") + (r.stdout or "")).strip()
        if "no valid artifacts" in err.lower() or "not found" in err.lower():
            log("  run {} 的 artifact 不存在或已过期（{}）".format(run_id, err[:110]))
            return []
        log("  第 {}/{} 次下载失败：{}".format(i, DOWNLOAD_RETRIES, err[:140]))
        if i < DOWNLOAD_RETRIES:
            time.sleep(5 * i)
    else:
        return []

    # 关键：真去数文件。gh 返回 0 不等于文件到手（今天就撞到过空目录）。
    pngs = []
    for dirpath, _, files in os.walk(dest):
        for fn in files:
            if fn.lower().endswith(".png"):
                p = os.path.join(dirpath, fn)
                if os.path.getsize(p) > 1024:
                    pngs.append(p)
    if not pngs:
        log("  下载报成功但没拿到 png —— 当作失败处理")
    return pngs


def place(src):
    """按文件名里的日期归到 Cards/{YYYY-MM}/。绝不覆盖。"""
    base = os.path.basename(src)
    m = re.search(r"_(\d{4})-(\d{2})-\d{2}_", base)
    ym = "{}-{}".format(m.group(1), m.group(2)) if m else time.strftime("%Y-%m")
    outdir = os.path.join(ROOT, AI_DIR, "Cards", ym)
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, base)
    if os.path.exists(dst):
        # 同名说明发号逻辑出过问题（比如推送失败后重算了同一个编号）。
        # 保留两份并明确报出来，让人去查，而不是悄悄覆盖。
        stem, ext = os.path.splitext(base)
        n = 2
        while os.path.exists(os.path.join(outdir, "{}_dup{}{}".format(stem, n, ext))):
            n += 1
        dst = os.path.join(outdir, "{}_dup{}{}".format(stem, n, ext))
        log("  ! 同名已存在，另存为 {} —— 请查一下发号逻辑".format(os.path.basename(dst)))
    shutil.copy2(src, dst)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not check_gh():
        return 2

    state = load_state()
    runs = list_runs(a.limit)
    if not runs:
        log("没有可取的成功运行")
        return 0

    state.setdefault("skipped", {})
    candidates = [r for r in runs
                  if str(r["databaseId"]) not in state["done"]
                  and str(r["databaseId"]) not in state["failed"]
                  and str(r["databaseId"]) not in state["skipped"]]

    pending = []
    for r in candidates:
        rid = str(r["databaseId"])
        pub = was_published(rid)
        if pub is True:
            pending.append(r)
        elif pub is False:
            state["skipped"][rid] = r["createdAt"]
            log("  run {} 没有发布（dry_run 演习），跳过".format(rid))
        # None = 查不出来，这次先放着，下次再判

    log("成功运行 {} 条，其中真正发布过、待取 {} 条".format(len(runs), len(pending)))
    if a.dry_run:
        for r in pending:
            log("  [dry-run] 会取 run {} ({})".format(r["databaseId"], r["createdAt"]))
        save_state(state)
        return 0

    got = 0
    for r in pending:
        rid = str(r["databaseId"])
        tmp = tempfile.mkdtemp(prefix="dsfetch_")
        try:
            pngs = download(rid, tmp)
            if not pngs:
                n = state["attempts"].get(rid, 0) + 1
                state["attempts"][rid] = n
                if n >= MAX_ATTEMPTS:
                    state["failed"][rid] = r["createdAt"]
                    log("  run {} 连续 {} 次拿不到，放弃。"
                        "**这张卡的原图可能已经永久丢失** —— artifact 只保留 90 天。"
                        .format(rid, n))
                continue
            for p in pngs:
                dst = place(p)
                got += 1
                log("  取回 {}  ({:.1f} MB)".format(
                    os.path.relpath(dst, ROOT), os.path.getsize(dst) / 1048576.0))
            state["done"][rid] = r["createdAt"]
            state["attempts"].pop(rid, None)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        save_state(state)

    save_state(state)
    log("本次取回 {} 张原图".format(got))
    if state["failed"]:
        log("累计放弃 {} 条运行：{}".format(
            len(state["failed"]), ", ".join(sorted(state["failed"]))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
