"""集中配置。凡是「换个环境要改」或「实测撞出来的数」都放这里。"""
import os
import re

# ---------------------------------------------------------------- 身份注册表
# 这一套代码同时供多家 DeepSeek 模型使用，跑哪一家由环境变量 ATELIER_AI 选，
# 每家在这里占一行。**再加一家就只加一行**，代码一个字都不用动。
#
# 一套代码带多租户，而不是一家拷一份目录：拷贝会让「修一个 bug 要改 N 处」，
# 两份代码慢慢跑偏，而它们本该逐字相同（正如章程对创作要求的规定）。
#
# key   —— 写进台账 ai 列、也是 index.html 里的 LEDGERS.ai。**定了就不能改**，
#          已发布的行里存着它，改了前端就认不出历史卡片。
# label —— 展示名，可以改。
# dir   —— 顶层目录，各家完全自理。Claude 是在位者，留在根目录不进这张表。
# provider —— 走哪个 clients/*.py。同厂商的多个模型共用一个。
# vision  —— **这只手看不看得见自己画的图**。它决定的不是「能力」而是「发什么脚手架」：
#            看不见的那几家配一整套代眼睛的东西（受控画布当场抛错、文字版画面报告、
#            报错回灌循环、渲染后 lint）；看得见的一样都不发 —— 那些东西是在替它看，
#            而「它看不看得懂自己画的图」恰恰是这个博物馆要展出的东西。
#            2026-08-12 由项目所有者定的原则：**脚手架按能力缺口配发，不按产线配发。**
AI_REGISTRY = {
    "flash": {
        "key": "deepseek", "label": "DeepSeek",
        "dir": "deepseekv4flash", "model": "deepseek-v4-flash",
        "workflow": "deepseek-card.yml",
        "provider": "deepseek", "vision": False,
    },
    "pro": {
        "key": "deepseek-pro", "label": "DeepSeek Pro",
        "dir": "deepseekv4pro", "model": "deepseek-v4-pro",
        "workflow": "deepseek-pro-card.yml",
        "provider": "deepseek", "vision": False,
    },
    "kimi": {
        # key 带版本号是刻意的：key 写进台账、定了不能改，而模型会换代。
        # K4 上线时它是另一只手，另开一行 —— "deepseek" 那行没带版本是先来者
        # 的历史遗留，别照抄。
        "key": "kimi-k3", "label": "Kimi K3",
        "dir": "kimik3", "model": "kimi-k3",
        "workflow": "kimi-card.yml",
        "provider": "kimi", "vision": True,
    },
}

# 厂商差异。**只有接口形状写在这里，创作要求一个字都不许进来。**
PROVIDERS = {
    "deepseek": {
        "api_base": "https://api.deepseek.com",
        "key_envs": ("DEEPSEEK_API_KEY",),
        "token_param": "max_tokens",
        # 实测：给 40000 烧满 40000，给 64000 烧满 64000 —— 复杂立体风格的首轮
        # 会把预算全部用于推理、可见输出为零。也没有可用的开关：reasoning_effort
        # 与 enable_thinking 都被接受却被静默忽略。所以按上限给。
        "max_tokens": 64000,
        "reasoning_param": None,        # 给了也没用，别发
    },
    "kimi": {
        # 注意：这个 base 自带 /v1，client 只补 /chat/completions，别再拼一次。
        "api_base": "https://api.moonshot.cn/v1",
        # 官方文档用 MOONSHOT_API_KEY；本项目统一叫 KIMI_API_KEY，两个都认。
        "key_envs": ("KIMI_API_KEY", "MOONSHOT_API_KEY"),
        # max_tokens 已弃用，K3 用 max_completion_tokens（默认 131072，上限 1048576）
        "token_param": "max_completion_tokens",
        "max_tokens": 131072,
        # K3 常开思考，但**它真的认这个参数**（DeepSeek 是接受了静默忽略）。
        # 2026-08-12 实测：渲染轮给 low，每轮推理只烧 30~322 token —— 与
        # DeepSeek 那边「给 64000 烧满 64000」形成鲜明对比。这个参数是真的。
        "reasoning_param": "reasoning_effort",
        # 元 / 百万 token。**输出比未命中输入贵 5 倍，未命中比命中贵 10 倍** ——
        # 所以省钱的第一顺位不是少说话，是让前缀能被缓存命中。
        "price": {"in_miss": 20.0, "in_hit": 2.0, "out": 100.0, "unit": "元"},
    },
}
AI = os.environ.get("ATELIER_AI", "flash")
if AI not in AI_REGISTRY:
    raise SystemExit(
        "ATELIER_AI={!r} 不认识。可选：{}".format(AI, "、".join(sorted(AI_REGISTRY))))
_ME = AI_REGISTRY[AI]

# ---------------------------------------------------------------- 模型
PROVIDER = _ME["provider"]
if PROVIDER not in PROVIDERS:
    raise SystemExit("provider={!r} 没有对应的 clients 实现".format(PROVIDER))
_P = PROVIDERS[PROVIDER]

# 这只手看不看得见自己画的图。下游据此选走哪条渲染路径。
VISION = bool(_ME.get("vision"))

API_BASE = os.environ.get("ATELIER_API_BASE", _P["api_base"])
KEY_ENVS = _P["key_envs"]
TOKEN_PARAM = _P["token_param"]
REASONING_PARAM = _P["reasoning_param"]
# DS_MODEL 仍可覆盖，用于临时试新模型号而不动注册表。
MODEL = os.environ.get("DS_MODEL", _ME["model"])

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", str(_P["max_tokens"])))
HTTP_TIMEOUT = 1200          # 实测单次最长 573s，留足余量
HTTP_RETRIES = 3             # 撞到过 IncompleteRead，不重试就报废整张卡

# ---------------------------------------------------------------- 轮次上限
# 盲模型 7 轮：它每一轮都在靠报错摸索，轮数是实打实的成本。
# 有视力的 12 轮：Claude 那条线的规矩是「有问题改脚本重渲染，直到画面干净」，
# 根本没有显式上限。卡在 7 轮就是规则不对等 —— 上限要宽到实际咬不到，
# 只当跑飞了的刹车用。真实轮数照旧写进台账 rounds 列，谁改了几轮看得见。
MAX_ROUNDS = int(os.environ.get("MAX_ROUNDS", "12" if VISION else "7"))

MAX_RESEARCH_ATTEMPTS = int(os.environ.get("MAX_RESEARCH_ATTEMPTS", "4"))
MAX_SEARCH_CALLS = int(os.environ.get("MAX_SEARCH_CALLS", "12"))   # 软上限
MAX_SEARCH_HARD = 20                                               # 硬上限
SEARCH_RESULTS = 8           # 每次搜索取几条（首条常是噪音，别只看一条）
SEARCH_SPACING = 2.0         # DDG 调用间隔秒数，避免被限流

# ---------------------------------------------------------------- 看图自检
# 只有 VISION 那几家用得上。回灌给模型的图要缩到这个宽度：原图是 scale=2 的
# 2000×3000+，直接发既贵又没必要（K3 收到 4K，但一张卡的毛病在 1024 宽上全看得见）。
VISION_FEEDBACK_WIDTH = int(os.environ.get("VISION_FEEDBACK_WIDTH", "1024"))
# JPEG 质量。**不敢再压**：压糊了细字，模型会把我们的压缩失真当成自己画的毛病，
# 那等于伪造证据 —— 而这条线的全部意义就是看它能不能看出真毛病。
VISION_FEEDBACK_QUALITY = 88

# ---------------------------------------------------------------- 身份
# 全部取自上面的注册表。下游代码照旧读 config.AI_KEY / AI_DIR，一处没改。
AI_KEY = _ME["key"]
AI_LABEL = _ME["label"]

# 每家一个顶层目录，内部镜像根目录的 Cards/web/text 结构。
# Claude 是在位者，留在根目录不动（AI_DIR 相当于 ""）；新来的一律进自己的目录。
AI_DIR = _ME["dir"]

# 卡面用与 Claude 相同的书写格式，但**各家自己数自己的**，从 NO.0001 起。
# 发号不需要读别人的台账 —— 两家的编号在各自的收藏里有意义，
# 合并展示时由前端用 (ai, no) 作复合标识来区分。
SERIAL_PREFIX = "NO."
LEDGER_NAME = "cards-index.csv"

# 台账列。前 12 列与 Claude 台账完全一致，其余追加在末尾 ——
# index.html 逐份台账从各自表头建列映射，多出来的列不会影响它。
#
# 末尾这批是**过程记录**，不是产物。画廊只需要产物，档案馆需要 provenance：
# 这张卡属于哪一班、返工了几轮、核实换了几次题、花了多久、原图的指纹是什么。
# 「NO.0003 返工 6 轮才过自检」本身就是展签说明。
#
#   slot              班次 N（UTC 纪元小时数，向下取整到 4 小时边界）。
#                     同一个 N = 同一道题，这是对照展墙的配对依据。前端本来
#                     靠 datetime+K+L 反解，但那只容许 ±2 小时漂移，而 Actions
#                     实测迟到过 2h33m —— 再迟一点就解不出来、悄悄从展墙消失。
#                     写进台账就没有这个失效模式了。
#   rounds            渲染返工轮数（1..MAX_ROUNDS）
#   research_attempts 选题核实尝试次数（1..MAX_RESEARCH_ATTEMPTS）
#   duration_s        整次运行秒数。datetime 是**开工**时刻（build_brief 在
#                     核实和渲染之前就取好了），所以完工时刻 = 两者相加。
#   sha256            原图 PNG 的指纹。原图不进仓库、只在本地和 artifact 里，
#                     指纹是它唯一进得了 git 的部分 —— 日后校验副本靠它。
#   flags             这张卡是不是降级发布的，空 = 正常。多个用 | 分隔。
#                     2026-08-12 起「渲染过不了检查也照发」（宁可展出一张有毛病的
#                     卡，也不空一班：空卡在展墙上只是个格子，什么都说明不了），
#                     所以必须有个地方说出来它过没过 —— 否则展墙分不出
#                     「没出问题」和「没被检查」。
#                     render-degraded  盲线：轮次耗尽，lint 仍有未解决的问题
#                     self-unsatisfied 明线：它自己看过图，说还有毛病
#   fingerprint       服务端回声的 system_fingerprint，即后端配置指纹。
#                     2026-08-17 加的，补的是 model 列补不上的那一半：**同一个
#                     别名、同一个回声版本串，底下的权重可以已经换过一轮**
#                     （deepseek-v4 相同 id、不同日期后缀就是这个形状）。
#                     那种替换从 model 列上完全看不出来，指纹是唯一看得出的。
#
#                     取**最后一次回声**，与 model 列同口径（见 compose*.py）。
#                     只记录，不展出：index.html 按表头名取列，不认识的列它根本
#                     不看 —— 这一列进档案、不进画廊，正是想要的效果。
#
#                     空 = 拿不到，读作「不知道」，**不是「没变过」**。各家填不填
#                     由厂商定：DeepSeek 文档标 required string（未实测取值是否
#                     真的随后端变化）；Kimi 待测；Claude 那条线永远为空 ——
#                     它在沙箱里画卡，根本没有 chat/completions 响应可读。
#
# 加列只能加在末尾，且 ledger.ensure_header() 会把已有台账的表头就地补齐。
COLUMNS = ["no", "datetime", "S", "style", "K", "topic", "L", "lang",
           "filename", "quote", "fact", "source", "ai", "model",
           "slot", "rounds", "research_attempts", "duration_s", "sha256",
           "flags", "fingerprint"]

# ---------------------------------------------------------------- 时间
# runner 跑在 UTC，但台账 datetime 必须写本地时间（UTC+8），
# 否则与 Claude 的行混排后按时间排序会错位。
TZ_OFFSET_HOURS = 8

# 出卡节拍：每 4 小时一班。K/L 按班次边界算而不是按当前小时算，
# 迟到的定时任务才不会拿到别的班次的题目（见 ledger.slot_now 的说明）。
SLOT_HOURS = 4

# ---------------------------------------------------------------- 路径
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHARTER = os.path.join(ROOT, "prompts", "card-charter.md")

# 本 AI 自己的地盘
BASE = os.path.join(ROOT, AI_DIR)
CARDS_DIR = os.path.join(BASE, "Cards")
WEB_DIR = os.path.join(BASE, "web")
TEXT_DIR = os.path.join(BASE, "text")
# 手稿：模型为这张卡现写的那份渲染脚本。compose 每轮都把脚本落在 out/work/，
# 但通过的那一版此前用完即弃（只有失败时才作为排障 artifact 上传）。
# 对一个档案馆来说那就是手稿 —— 别的 AI 艺术项目没有的展品，而成本是零：
# 文件本来就已经在磁盘上了。
CODE_DIR = os.path.join(BASE, "code")
LEDGER = os.path.join(CARDS_DIR, LEDGER_NAME)


# ---------------------------------------------------------------- 规则
STYLE_EXCLUDE_WINDOW = 15    # 排除最近 N 条用过的风格（章程第 1 节）
STYLE_COUNT = 47             # 风格总数（章程第 4 节的对照表长度）

# ---- 共享风格班（章程第 1 节，改动 ⑤）
# 每天挑一班，所有产出方用同一个风格。平时各方同领域、同语言、风格各自随机，
# 「执笔者」和「风格」两个变量混在一起；这一班把风格按住，唯一的变量就只剩
# 执笔者本身。每天一组，47 天走遍全部风格。
#
# **这个值必须各方从 N 独立算出，绝不能去读别人的台账。** 读别人在只有两方时
# 勉强能用，方数一多就散架（谁是权威？谁等谁？），而且破坏了各自不读别人台账
# 的隔离 —— 那正是 08-05 / 08-08 两次事故的形状。同一个 N 算出同一个 S，
# 无论有多少方参与都成立，也不需要任何一方知道别人的存在。
SHARED_STYLE_UTC_HOUR = 4    # None = 关闭。4 = UTC 04:00 = 本地 12:00 那一班

# 风格在 47 种里的跳步。**不能用 1**：那样共享班会顺着对照表往下走，而表是
# 按类聚在一起的（38~47 全是立体类），连着一周都是 3D，正好犯了排除机制要防
# 的那个毛病。47 是质数，任何 1~46 的跳步都能不重不漏地走遍全部 47 种，
# 取 17 只是让相邻两天跳到表的另一头去。
SHARED_STYLE_STRIDE = 17
WEBP_WIDTH = 1200
WEBP_QUALITY = 82

# 只允许提交自己地盘（AI_DIR）下的这三类文件。别人的 README.md / 台账 / 图片
# 一律不许碰 —— 两边同时写同一个文件会让 sync-to-github.bat 的 pull --rebase
# 冲突并 goto FAIL，那正是 2026-08-05 与 08-08 卡片积压事故的形状。
#
# **从 AI_DIR 推导，不要写死。**新来的 AI 复制这份 config、只改 AI_DIR，
# 白名单就自动跟着对。写死过一次就出过事：目录布局从
# 「Cards/cards-index-deepseek.csv + web/*/DS.*.webp」改成「各家一个顶层目录」
# 之后，这个常量没跟着改，变成一条会拒绝掉全部合法路径的死规则。当时没炸，
# 只因为唯一的调用方恰好都走了 expected 分支 —— 那是运气，不是设计。
COMMIT_ALLOW = (
    r"^{d}/(Cards/{l}"
    r"|web/\d{{4}}-\d{{2}}/[^/]+\.webp"
    r"|text/\d{{4}}-\d{{2}}/[^/]+\.md"
    r"|code/\d{{4}}-\d{{2}}/[^/]+\.py)$"
).format(d=re.escape(AI_DIR), l=re.escape(LEDGER_NAME))
