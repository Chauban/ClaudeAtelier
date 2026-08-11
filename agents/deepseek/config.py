"""集中配置。凡是「换个环境要改」或「实测撞出来的数」都放这里。"""
import os

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
SERIAL_PREFIX = "NO."     # 全站统一连号：卡面上看不出是哪家做的，「谁做的」只在背面和筛选里
LEDGER_NAME = "cards-index-deepseek.csv"

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
CARDS_DIR = os.path.join(ROOT, "Cards")
WEB_DIR = os.path.join(ROOT, "web")
TEXT_DIR = os.path.join(ROOT, "text")
LEDGER = os.path.join(CARDS_DIR, LEDGER_NAME)

# ---------------------------------------------------------------- 规则
STYLE_EXCLUDE_WINDOW = 15    # 排除最近 N 条用过的风格（章程第 1 节）
WEBP_WIDTH = 1200
WEBP_QUALITY = 82

# 只允许提交这些路径。Claude 的 README.md / cards-index.csv / NO.* 一律不许碰 ——
# 两边同时写同一个文件会让 sync-to-github.bat 的 pull --rebase 冲突并 goto FAIL，
# 那正是 2026-08-05 与 08-08 卡片积压事故的形状。
COMMIT_ALLOW = r"^(Cards/cards-index-deepseek\.csv|web/\d{4}-\d{2}/DS\.[^/]+\.webp|text/\d{4}-\d{2}/DS\.[^/]+\.md)$"
