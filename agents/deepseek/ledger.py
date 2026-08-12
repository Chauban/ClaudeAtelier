"""台账：发号、抽风格、算 K/L、查重、追加行。

**每家 AI 完全自理：发号、查重、风格轮换，一律只读自己那份台账。**

谁也不用知道谁 —— 让在位的 Claude 去依赖新来者的文件，是拿它的稳定
换整洁，不划算；反过来让新来的去读别人的，也只是把耦合换个方向。
每个模型是一个独立的展区，各自从 NO.0001 起号、各自保证自己不重复。

由此接受的代价（项目所有者已确认）：合并展示的那面墙上，偶尔可能
连着出现同一种风格，或同一条冷知识被两家分别讲过。
"""
import csv
import io
import os
import random
import re
import time

import config


def local_now():
    """本地时间（UTC+8）。runner 跑在 UTC，写错会让合并排序错位。"""
    t = time.gmtime(time.time() + config.TZ_OFFSET_HOURS * 3600)
    return time.strftime("%Y-%m-%d %H:%M", t), time.strftime("%Y-%m", t), \
        time.strftime("%Y-%m-%d", t)


def slot_now():
    """本班次的 N（UTC 纪元小时数，向下取整到 4 小时班次边界）。

    **不能直接用「现在是第几个小时」。**GitHub Actions 的定时任务经常迟到，
    2026-08-12 实测迟了 2 小时 33 分：那一班算出的是「迟到那一刻」的题目
    （K=4 L=7），而同一班的 Claude 拿到的是 K=2 L=5。结果 08:00 班 DeepSeek
    缺席，另外多出一张谁也对不上的孤卡 —— 「同一道题，不同的手」这个前提
    当场就断了，而这正是这个项目的题眼。

    向下取整到班次边界，迟到多久都落回同一个 N。

    对 Claude 是零影响：它跑在北京 00/04/08/12/16/20 点，换算成 UTC 是
    16/20/00/04/08/12，全部 ≡ 0 (mod 4)，取整前后完全相同。也就是说这个
    修正只把迟到者拉回队列，不动准点者。
    """
    h = config.SLOT_HOURS
    return int(time.time()) // 3600 // h * h


def kl_from_clock(n=None):
    """K、L 由班次 N 推出（章程第 1 节）。"""
    n = slot_now() if n is None else n
    return n % 17 + 1, n % 7 + 1


def shared_style_for(n):
    """共享风格班的 S；本班不是共享班就返回 None（章程第 1 节，改动 ⑤）。

    纯函数，只依赖 N —— 这是它的全部要点：**每一方各自算，谁也不问谁**。
    同一个 N 必然得到同一个 S，参与方是两家还是十家都不影响，新来的一方
    什么都不用注册、不用通知任何人，算出来就自动对上。

    反面做法（读别人的台账看它抽了什么）在只有两方时勉强能用，方数一多
    立刻散架：谁是权威？谁等谁先出卡？某一方那一班没出卡怎么办？而且它
    要求跨目录读别人的文件，破坏隔离。所以这里一行 I/O 都没有。
    """
    if config.SHARED_STYLE_UTC_HOUR is None:
        return None
    if n % 24 != config.SHARED_STYLE_UTC_HOUR:
        return None
    return (n // 24 * config.SHARED_STYLE_STRIDE) % config.STYLE_COUNT + 1


def _read(path):
    if not os.path.exists(path):
        return []
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if (r.get("no") or "").strip()]


def load_all():
    """本 AI 自己台账的全部行，按 datetime 升序。

    名字里的 all 指「这个展区的全部卡片」，不是「全站」——
    各家自理，谁也不读谁的。
    """
    rows = _read(config.LEDGER)
    for r in rows:
        r["_ledger"] = config.AI_KEY
    rows.sort(key=lambda r: (r.get("datetime") or ""))
    return rows


def load_own():
    return _read(config.LEDGER)


def next_no():
    """各家自己从 NO.0001 数起。

    不读别人的台账：两家的编号在各自的展区里各有意义，
    合并展示时由前端用 (ai, no) 作复合标识来区分。

    也不扫磁盘（Claude 那条 max(台账, 磁盘)+1 是为了接住「渲染完就崩、
    没来得及写台账」的孤儿编号）：runner 无状态，崩了什么都不留，
    原图只在 lint 通过后才作为 artifact 上传，那个危险这里不存在。
    """
    own = load_own()
    return max([int(r["no"]) for r in own if str(r["no"]).isdigit()], default=0) + 1


def serial(no):
    return "{}{:04d}".format(config.SERIAL_PREFIX, no)


def pick_style(rng=None, n=None):
    """定本班的风格（章程第 1 节）。返回 (S, 名称, 候选数)。

    共享风格班优先：那一班的 S 由 N 直接算出，**压过排除规则** ——
    哪怕这个风格最近刚做过也照做，否则各方就不可能落在同一个 S 上。
    候选数返回 1，表示「没得选」。
    """
    import tables
    n = slot_now() if n is None else n
    shared = shared_style_for(n)
    if shared is not None:
        return shared, tables.style(shared), 1

    rng = rng or random.Random()
    recent = [r.get("S") for r in load_all()[-config.STYLE_EXCLUDE_WINDOW:]]
    used = {int(s) for s in recent if str(s).strip().isdigit()}
    pool = [s for s in range(1, config.STYLE_COUNT + 1) if s not in used]
    if not pool:                       # 理论上不可能（47 > 15），兜底
        pool = list(range(1, config.STYLE_COUNT + 1))
    s = rng.choice(pool)
    return s, tables.style(s), len(pool)


def pick_lang7(rng=None):
    """L=7 时从五种外语里挑，避开台账里最近用过的（章程第 6 节）。"""
    import tables
    rng = rng or random.Random()
    recent = [(r.get("lang") or "") for r in load_all()[-12:]]
    pool = [x for x in tables.LANG7_CHOICES if x[0] not in recent] or tables.LANG7_CHOICES
    return rng.choice(pool)


# ------------------------------------------------------------------ 查重
def _trigrams(s):
    s = re.sub(r"\s+", "", s or "")
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


def similar_facts(candidate, rows=None, k=15, thresh=0.18):
    """与候选冷知识最相近的若干条既有内容。

    章程要求「换个说法讲同一件事也算重复」。目前 60 条时把全部 fact 塞进
    提示词还行，几百条以后就撑不住了 —— 所以这里先做字符三元组 Jaccard
    粗筛，只把最像的几条交给模型判断，提示词长度不随archive增长。
    """
    rows = load_all() if rows is None else rows
    cg = _trigrams(candidate)
    if not cg:
        return []
    scored = []
    for r in rows:
        for field in ("fact", "quote"):
            g = _trigrams(r.get(field) or "")
            if not g:
                continue
            j = len(cg & g) / float(len(cg | g))
            if j >= thresh:
                scored.append((j, field, r))
    scored.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for j, field, r in scored:
        key = (r.get("_ledger"), r.get("no"))
        if key in seen:
            continue
        seen.add(key)
        out.append({"score": round(j, 3), "field": field,
                    "no": r.get("no"), "ledger": r.get("_ledger"),
                    "quote": r.get("quote"), "fact": r.get("fact")})
        if len(out) >= k:
            break
    return out


def all_quotes_and_facts(rows=None):
    rows = load_all() if rows is None else rows
    return [{"no": r.get("no"), "topic": r.get("topic"),
             "quote": r.get("quote"), "fact": r.get("fact")} for r in rows]


# ------------------------------------------------------------------ 写入
def read_header(path=None):
    """台账现有表头；文件不存在或为空返回 None。"""
    path = path or config.LEDGER
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            return [c.strip() for c in row]
    return None


def ensure_header(path=None):
    """表头落后于 COLUMNS 时就地补齐，已有行末尾补空。

    为什么必须有这一步：append 原本只在**文件不存在**时写表头，之后一律按
    config.COLUMNS 追加。所以往 COLUMNS 末尾加一列，会让旧表头（14 列）配上
    新行（19 个字段）—— DictWriter 照写不误，DictReader 却按旧表头读，
    多出来的值全落进 None 键里静默丢失。台账是唯一真相源，静默丢字段是
    最坏的一种坏法：不报错，等发现时已经写坏了好几班。

    只允许**在末尾追加**。表头若不是 COLUMNS 的前缀，说明有人改名或插入了列，
    那不是这里能安全处理的事，宁可停下来 —— 档案不猜。
    """
    path = path or config.LEDGER
    head = read_header(path)
    if head is None or head == config.COLUMNS:
        return False
    if head != config.COLUMNS[:len(head)]:
        raise RuntimeError(
            "台账表头与 config.COLUMNS 对不上，且不是「末尾加列」这种情况，已中止。\n"
            "  现有：{}\n  期望：{}\n"
            "加列只能加在末尾。改名或插列需要人工迁移。".format(head, config.COLUMNS))

    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    rows = rows[1:]                     # 丢掉旧表头
    pad = len(config.COLUMNS)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(config.COLUMNS)
        for r in rows:
            w.writerow(list(r) + [""] * (pad - len(r)))
    os.replace(tmp, path)               # 原子替换，中途断电不会留半个台账
    return True


def append(row):
    """往自己的台账追加一行。文件不存在就带 BOM 新建（前端按 utf-8-sig 读）。"""
    exists = os.path.exists(config.LEDGER)
    os.makedirs(os.path.dirname(config.LEDGER), exist_ok=True)
    if not exists:
        with io.open(config.LEDGER, "w", encoding="utf-8-sig", newline="") as f:
            csv.DictWriter(f, fieldnames=config.COLUMNS).writeheader()
    else:
        ensure_header()                 # 表头落后就先补齐，见上
    with io.open(config.LEDGER, "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=config.COLUMNS).writerow(
            {k: row.get(k, "") for k in config.COLUMNS})
    return config.LEDGER


def last_datetime():
    own = load_own()
    return own[-1]["datetime"] if own else None
