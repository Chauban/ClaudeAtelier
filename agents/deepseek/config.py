"""集中配置。凡是「换个环境要改」或「实测撞出来的数」都放这里。"""
import os
import re

# ---------------------------------------------------------------- 模型
API_BASE = "https://api.deepseek.com"
MODEL = os.environ.get("DS_MODEL", "deepseek-v4-flash")

# 实测：给 40000 烧满 40000，给 64000 烧满 64000 —— 复杂立体风格的首轮会把
# 预算全部用于推理、可见输出为零。也没有可用的开关：reasoning_effort=low 与
# enable_thinking=False 都被接受却被静默忽略。所以按上限给，并靠 compose 里的
# 「空输出识别 + 带具体反馈重试」兜底。
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "64000"))
HTTP_TIMEOUT = 1200          # 实测单次最长 573s，留足余量
HTTP_RETRIES = 3             # 撞到过 IncompleteRead，不重试就报废整张卡

# ---------------------------------------------------------------- 轮次上限
MAX_ROUNDS = int(os.environ.get("MAX_ROUNDS", "7"))        # 渲染返工
MAX_RESEARCH_ATTEMPTS = int(os.environ.get("MAX_RESEARCH_ATTEMPTS", "4"))
MAX_SEARCH_CALLS = int(os.environ.get("MAX_SEARCH_CALLS", "12"))   # 软上限
MAX_SEARCH_HARD = 20                                               # 硬上限
SEARCH_RESULTS = 8           # 每次搜索取几条（首条常是噪音，别只看一条）
SEARCH_SPACING = 2.0         # DDG 调用间隔秒数，避免被限流

# ---------------------------------------------------------------- 身份
AI_KEY = "deepseek"
AI_LABEL = "DeepSeek"

# 每家一个顶层目录，内部镜像根目录的 Cards/web/text 结构。
# Claude 是在位者，留在根目录不动（AI_DIR 相当于 ""）；新来的一律进自己的目录。
AI_DIR = "deepseekv4flash"

# 卡面用与 Claude 相同的书写格式，但**各家自己数自己的**，从 NO.0001 起。
# 发号不需要读别人的台账 —— 两家的编号在各自的收藏里有意义，
# 合并展示时由前端用 (ai, no) 作复合标识来区分。
SERIAL_PREFIX = "NO."
LEDGER_NAME = "cards-index.csv"

# 台账列。前 12 列与 Claude 台账完全一致，ai/model 追加在末尾 ——
# index.html 逐份台账从各自表头建列映射，多出来的列不会影响它。
COLUMNS = ["no", "datetime", "S", "style", "K", "topic", "L", "lang",
           "filename", "quote", "fact", "source", "ai", "model"]

# ---------------------------------------------------------------- 时间
# runner 跑在 UTC，但台账 datetime 必须写本地时间（UTC+8），
# 否则与 Claude 的行混排后按时间排序会错位。
TZ_OFFSET_HOURS = 8

# ---------------------------------------------------------------- 路径
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHARTER = os.path.join(ROOT, "prompts", "card-charter.md")

# 本 AI 自己的地盘
BASE = os.path.join(ROOT, AI_DIR)
CARDS_DIR = os.path.join(BASE, "Cards")
WEB_DIR = os.path.join(BASE, "web")
TEXT_DIR = os.path.join(BASE, "text")
LEDGER = os.path.join(CARDS_DIR, LEDGER_NAME)


# ---------------------------------------------------------------- 规则
STYLE_EXCLUDE_WINDOW = 15    # 排除最近 N 条用过的风格（章程第 1 节）
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
    r"|text/\d{{4}}-\d{{2}}/[^/]+\.md)$"
).format(d=re.escape(AI_DIR), l=re.escape(LEDGER_NAME))
