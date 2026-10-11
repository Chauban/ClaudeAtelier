# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 这是什么

内容生产项目，不是应用工程：没有 package.json、没有构建、没有单元测试框架。Codex 每天本地 12:00 一班（其余三条线目前暂停，见 `lines.json`），生成一张竖版卡片图（一句金句 + 一条核实过的冷知识），47 种设计风格 / 7 种语言 / 17 个冷知识领域轮换，产物汇入各自台账并发布成一个静态站。

看点是**同一道题，不同的手**：K（领域）和 L（语言）由 UTC 小时数推算，同一班次的各家拿到完全相同的题目，只有手不同。所以创作要求是一份、逐字相同（`prompts/card-charter.md`），运行环境各写各的。

三份本地文档，动手前按需读（都在仓库根目录，都被 .gitignore 排除）：

| 文件 | 内容 |
|---|---|
| `HANDOFF-项目交接.md` | 完整交接说明，含 Codex 生卡任务的逐字 prompt（第 5 节）和事故复盘 |
| `HANDOFF-接入新AI.md` | 再接一家 AI 要动哪些地方；`agents/` 那套代码的设计说明 |
| `prompts/card-charter.md` | **创作章程**，所有 AI 共用的题目本身。改它就是改产品 |

本文件是上面三份的索引和摘要。

## 这个文件夹是有人在住的

多条产线正在这个文件夹和这个仓库里运行。改动之前先确认自己没有踩到它们：

- **不碰生成端的产出面**：`README.md`（Codex 每次生卡整份重写，改了会被覆盖）、任何 `Cards/cards-index.csv`、根目录的 `Cards/` `web/` `text/`、以及各 AI 自己的顶层目录（`deepseekv4flash/` 等）。
- **不做写操作型 git**：不 `add`/`commit`/`pull`/`push`，也不跑 `git status`（它要刷索引、会留 `index.lock`）。锁落在生成窗口里会让那一班车的 commit 作废。
- **避开两个时间窗**：本地 12:00~12:20（Codex 生成）和 14:00（同步推送）期间不往仓库里写文件，也不要手动跑 `sync-to-github.bat`。
- **Codex 生卡任务只暂存自己的四样产出**（`Cards web text README.md`），2026-08-12 起不再 `git add -A`。改这条是因为当天 20:30 出了事故：本地有一份过时的 `deepseekv4flash/Cards/cards-index.csv`（4 行 19 列），被 `-A` 扫进 NO.0069 那条提交，而 Actions 已经把同一个文件写到 7 行 14 列 —— `pull --rebase` 冲突、`sync-to-github.bat` goto FAIL，两张卡卡在本地。**推论：你在这个文件夹里改的任何东西，现在都不会被生卡任务顺手提交了，要自己 commit。**
- **本地 HEAD 常常落后于 origin/main**：DeepSeek 各线直接从 Actions 推 main，本地要等 `sync-to-github.bat` 的 `pull --rebase` 才追上。看到本地缺文件先想到这一点，别当成事故。

## 两种产线形状

**Codex（在位者，跑在本机 + Cowork 沙箱）**

```
① 生成  Cowork 定时任务 verse-fact-card，每天本地 12:00 一班，约 :09 触发、:13~:17 完成
        跑在 Linux 沙箱里，写文件到挂载的 Windows 文件夹，只做本地 git commit
        （原来是 cron 0 */4 * * *，一天六班；2026-09 起降到一天一班，为省开销）
② 推送  Windows 计划任务 ClaudeAtelier-Sync，每天 14:00 跑 sync-to-github.bat auto
        另有 ClaudeAtelier-Sync-OnLogon（登录后 5 分钟）兜底
```

生成端没有 GitHub 凭据，push 必然失败，**所以 Codex 生卡任务只 commit 不 push**。改完文件要等 14:00 那次同步才上线。

**Actions 各线（DeepSeek flash / DeepSeek Pro / Kimi K3）**

```
① 触发  Windows 计划任务 ClaudeAtelier-Trigger-Flash / -Pro / -Kimi 跑 trigger-cards.bat，
        发 workflow_dispatch。workflow 里的 cron 是兜底，不是主触发器
② 生成  job generate：无任何凭据，跑模型现写的渲染代码，产物传成 artifact
③ 发布  job publish：只跑仓库自有代码，拿 contents:write，直接 push main
④ 取回  Windows 计划任务 ClaudeAtelier-FetchDS 每小时把原图 PNG 从 artifact 拉回本地
        （tools/fetch_ds_originals.py 按注册表遍历**全部**产线，不是只取 flash）
```

**一条分岔：看不看得见自己画的图。** 这决定走哪条渲染路径，由 `config.AI_REGISTRY`
的 `vision` 字段给出，**与产线无关**：

```
vision=False  DeepSeek 各线   compose.py        受控画布当场抛错 + 文字版画面报告 + lint 十几项硬检查
vision=True   Kimi K3         compose_vision.py 裸 Pillow，画完把图发回去让它自己看、自己改，
                                                没有画布约束、没有 lint、没有任何替它看的东西
```

原则是 2026-08-12 定的：**脚手架按能力缺口配发，不按产线配发。** 代眼睛的那套是给
看不见图的模型的补偿；发给看得见的就成了代它答题，而「它看不看得懂自己画的图」
恰恰是这个博物馆要展出的东西。所以 Kimi 那条线和 Codex 那条线的过程是对齐的。

**两条共同的下游**：③ 托管 `github.com/Chauban/ClaudeAtelier` main → ④ 上线 Cloudflare Worker「claudeatelier」，纯静态站，main 一更新自动重建，约一分钟。

诊断「网站没更新」的顺序：先跑 `python tools/watchdog.py` 看是哪条线停了 → Codex 线读 `sync.log`、比 `git log -1 HEAD` 与 `git log -1 origin/main`；DeepSeek 线看 Actions 页面和告警 issue → 再怀疑 Cloudflare 构建或浏览器缓存。多数是用户标签页没重取，但 2026-08-08 出过真分叉，别默认是假警报。

## 本机计划任务全景

| 任务名 | 时刻 | 干什么 | 注册脚本 |
|---|---|---|---|
| `ClaudeAtelier-Sync` | 每天 14:00 | `sync-to-github.bat auto`，推 Codex 的提交 | `install-scheduled-sync.bat` |
| `ClaudeAtelier-Sync-OnLogon` | 登录后 5 分钟 | 同上，兜底 | 同上 |
| `ClaudeAtelier-Trigger-Flash` | **已禁用**（2026-09-09） | 发 `deepseek-card.yml` 的 dispatch | `install-scheduled-trigger.bat` |
| `ClaudeAtelier-Trigger-Pro` | **已禁用**（2026-09-09） | 发 `deepseek-pro-card.yml` 的 dispatch | 同上 |
| `ClaudeAtelier-Trigger-Kimi` | **已删除**（2026-08-14） | 发 `kimi-card.yml` 的 dispatch | 同上 |
| `ClaudeAtelier-FetchDS` | 每小时 | 取回 Actions 里的原图 PNG | `install-ds-fetch.bat` |

**目前只有 Codex 那条线在出卡**，每天本地 12:00 一班；DeepSeek 两条线和 Kimi 都停了（省 API 开销），Kimi 还在 GitHub 上把 `kimi-card.yml` 手动 disable 了。**停一条线之后必须去 `lines.json` 登记**，否则 watchdog 会一直为它告警 —— 08-14 停 Kimi 时漏了这步，issue #9 连报一个月 81 条评论，等于把告警机制废掉。

注册脚本都要**以管理员身份运行一次**。触发任务靠 `gh auth login` 存在 Windows 凭据管理器里的 token，因此必须以当前用户身份、「仅在用户登录时运行」跑，**别改成 `/RU SYSTEM`**（读不到 token，每次静默失败）。

为什么不直接用 workflow 的 cron：2026-08-12 抽查 7 次 schedule 触发，全部迟到，47 分钟到 2h33m。**本机管时钟，GitHub 管算力。** 触发失败不停线——cron 兜底照样出卡，只是迟到。

## 常用命令

只读诊断（不会在 `.git` 里留锁）：

```bash
python tools/watchdog.py                 # 各产线最新卡有多旧；退出码 1 = 有线卡住了
python tools/watchdog.py --all           # 连暂停的线也查一遍（看它们停了之后有没有偷偷出卡）
python tools/check_originals.py          # 台账与本地原图对账；artifact 90 天过期预警
python tools/verify_charter.py           # 章程是否仍逐字忠于 SKILL.md
python tools/check_ledger_append_only.py # 台账有没有被改写（CI 里也跑，见 ledger-guard.yml）
python tools/backfill_ledger.py          # 末尾加列后回填旧行；默认预演，--apply 才写
python tools/build_shells.py --check     # 壳页要生成哪些（去掉 --check 才写 c/）
tail -20 sync.log                        # Codex 线最近几次推送结果
tail -20 trigger.log fetch-ds.log        # 触发与取回
git log -3 --format='%h %ad %s' --date=short
git log -1 --format='%h %s' origin/main  # 与上面一致 = 已同步
python3 -c "import csv,io;r=list(csv.DictReader(io.open('Cards/cards-index.csv',encoding='utf-8-sig')));print(len(r),r[-1]['no'],r[-1]['style'])"
find .git -name '*.lock'                 # 必须为空
git diff --stat HEAD                     # 看改动（别用 git status，见上）
git diff --ignore-cr-at-eol              # 行尾差异会让 diff 严重虚高
```

跑 DeepSeek 那套代码（依赖 `pillow numpy fonttools ddgs trafilatura zhconv`，密钥读环境变量 `DEEPSEEK_API_KEY`）：

```bash
python agents/deepseek/smoke_test.py                   # 最接近「测试」的东西：画一张真卡 + 逐个触发守卫
python agents/deepseek/fonts.py                        # 字体自检，断言字形覆盖。TTC 索引不许硬编码
ATELIER_AI=flash python agents/deepseek/run.py --out out --dry-run --skip-freshness
ATELIER_AI=pro   python agents/deepseek/run.py --out out --dry-run --force-style 24
```

`--dry-run` 照样产出 `out/publish/`（webp、文字副本、row.json），只是不写台账。`ATELIER_AI` 选租户，默认 `flash`。

本地预览站点必须走 http，`index.html` 用 fetch 读 CSV，`file://` 会被浏览器拦截：

```bash
python -m http.server 8000   # 然后开 http://localhost:8000/
```

手动推送 Codex 那条线：双击 `sync-to-github.bat`（成功自动关窗，失败留窗并打印 git 错误，日志写 `sync-last-run.log`）。手动催一张 DeepSeek 卡：`gh workflow run deepseek-card.yml --repo Chauban/ClaudeAtelier`。部署不需要 wrangler 命令，push 到 main 即可。

## 目录布局：一家 AI 一块地盘

Codex 是在位者，留在根目录；后来的每家占一个顶层目录，内部镜像同样的 `Cards/web/text` 结构（会写代码的那几家多一个 `code/`）。

```
Cards/ web/ text/ README.md         ← Codex（根目录）
deepseekv4flash/Cards|web|text|code ← DeepSeek flash
deepseekv4pro/Cards|web|text|code   ← DeepSeek Pro
kimik3/Cards|web|text|code          ← Kimi K3
agents/deepseek/                 ← 编排代码，多租户共用一套
agents/deepseek/clients/         ← 一家厂商一个文件，由注册表的 provider 选
prompts/card-charter.md          ← 创作章程，所有 AI 共用
lines.json                          ← 产线状态登记表：哪条在跑、哪条停了、停摆阈值多少
c/{ai}/{编号}.html                  ← 壳页，由 shells.yml 独占生成，各家都不许碰
tools/                              ← 巡检、对账、取原图、章程校验、台账守卫、壳页
.github/workflows/                  ← 各线生卡 + watchdog + ledger-guard + shells
```

`Cards/` 下两个下划线目录不参与对账，也不在编号序列里（都被 `.gitignore` 排除，只在本地）：`_retired/` 是刻意退休、被取代的稿子；`_orphans/` 是画成功了但没进台账的（发布那步没跑成）。**别留在 `{YYYY-MM}/` 里** —— `next_no()` 只数台账，那个序号迟早会被下一张卡用掉，届时同一编号会有两张不同的画挨在一起。

**各家只准碰自己的目录。** `config.COMMIT_ALLOW` 从 `AI_DIR` 自动推导出提交路径白名单，pro 会拦下 flash 的台账，反之亦然。多方同时写同一个文件，就是 2026-08-05 和 08-08 两次卡片积压事故的形状。

**根目录里「大家共用」的可写目录一律不要建**，那等于把上面这条作废。已经有共用产物的（`c/` 壳页），做法是**指定一个独占的写入方**：`shells.yml` 只读各家台账、只写 `c/`，不进任何一家的生成路径，和 `watchdog` 一样是旁观者。

**按 N 家设计，不要按两家。** 注册表、`COMMIT_ALLOW` 推导、`watchdog` 的 glob 发现、`index.html` 的 `LEDGERS` 驱动列数 —— 接第三第四家的成本已经预付过了。跨 AI 的取值一律「各方从共享输入（班次号 N）独立算出同一个结果」，**绝不是「读另一家的台账」**。

## 数据流与派生关系

每家的 `Cards/cards-index.csv` 是**那一家的唯一真相来源**，其余全部由它派生，一次生卡必须同时更新：

| 产物 | 说明 |
|---|---|
| `{AI目录/}Cards/{YYYY-MM}/*.png` | 原图，2 倍分辨率。`.gitignore` 排除 `Cards/*/` 和 `*/Cards/*/`，400MB+ 只留本地 |
| `{AI目录/}web/{YYYY-MM}/*.webp` | 宽 1200、quality 82，**只有这个进仓库和网站** |
| `{AI目录/}text/{YYYY-MM}/*.md` | 纯文字副本 |
| `{AI目录/}code/{YYYY-MM}/*.py` | **手稿**：模型为这张卡现写的渲染脚本，原样存档，不整理不格式化 |
| `README.md` | Codex 每次生卡整份重写的画廊页，按编号倒序。DeepSeek 各线不碰它 |
| `index.html` | 单文件静态站，前端 fetch **各份**台账 CSV 合并渲染 |
| `c/{ai}/{编号}.html` | **壳页**：每张卡一个静态展签，OG 标签写死在源码里。纯前端站没有它就分享无预览图、搜索引擎收录不到。由 `tools/build_shells.py` 全量生成，**可再生**（改模板就重跑），所以是短缓存不是 immutable |

台账 schema（UTF-8 **BOM**，读时用 `utf-8-sig`）。Codex 那份是最早的 12 列；DeepSeek 各线在末尾追加了 9 列，前 12 列逐字一致：

```
no,datetime,S,style,K,topic,L,lang,filename,quote,fact,source
                        [,ai,model,slot,rounds,research_attempts,duration_s,sha256,flags
                         ,fingerprint]
```

字段里有逗号、引号、换行，**必须用 Python `csv` 模块读写，绝不能 split 手撸**。`filename` 存相对路径 `{YYYY-MM}/文件名.png`（不含 AI 目录前缀，前端拼 `base`）。

末尾那批是**过程记录**（provenance），画廊不需要、档案馆需要：

- `datetime` 是**开工**时刻（`build_brief()` 在核实和渲染之前就取好了），**不是完工时刻**。完工 = `datetime + duration_s`。
- `slot` 是**出题用的那个 N**（UTC 纪元小时数）。同一个 N = 同一道题，这是对照展墙的配对依据。新卡由 `ledger.slot_now()` 写，一律落在 4 小时边界上；**非边界值不是错误**，它是 2026-08-12 班次漂移事故的物证（NO.0004，flash，N=496250）。
- `rounds` / `research_attempts` 空着表示「不知道」，不是 0 —— 08-12 之前的行没记过。
- `sha256` 是原图指纹。原图不进仓库，这一列是它唯一进得了 git 的部分。
- `fingerprint` 是**后端配置指纹**（响应里的 `system_fingerprint`，2026-08-17 加）。它补的是 `model` 列补不上的那一半：同一个别名、同一个回声版本串，底下的权重可以已经换过一轮，那种替换从 `model` 上完全看不出来。取值口径与 `model` 一致（最后一次回声）。**只进档案不进画廊**——`index.html` 按表头名取列，不认识的列它根本不看，所以加这一列前端一行都不用改。空 = 拿不到，读作「不知道」，不是「没变过」；**永远不可回填**（响应没留，重新问拿到的是今天的后端，正好是它要区分的那个东西）。Codex 那条线这一列恒为空——沙箱里画卡，没有 HTTP 响应可读。

**加列只能加在末尾**，`ledger.ensure_header()` 会把落后的表头就地补齐并给旧行补空。它拒绝改名和插列 —— 那种迁移要人来做。

文件命名：`NO.{四位补零}_{YYYY-MM-DD}_S{S}-{风格简名}_{语言代码}.png`，语言代码 `ZH / ZH-TW / ZH-HK / YUE / EN / JA / FR / DE / ES / KO / IT`。**各家自己数自己的，都从 NO.0001 起**；合并展示时前端用 `(ai, no)` 作复合标识。

**编号规则**：`NO = max(台账最大 no, 磁盘上 NO.(\d+)_ 解析出的最大编号) + 1`。只看台账会重复发号（渲染完就崩、没写台账的编号其实已被占用），2026-08-06 因此出过两张 NO.0032。推论：**PNG 一落地立刻写台账那行，别拖到最后**。

## agents/ 那套代码的形状

`agents/deepseek/` 是「模型看不见图」这条路的完整实现，也是多租户编排器。目录叫 deepseek，但除 `client.py` 和 `config.py` 外**代码里没有一处提到 DeepSeek**。分三层看：

- **主干（与模型无关）**：`run.py` 派活（编号/K/L/S/文件名全由代码定死，模型无权选）、`ledger.py` 发号与抽风格、`tables.py` 从章程解析三张对照表、`research.py` 选题核实编排、`search.py`+`fetch.py` 取证、`verify.py` **证据闸门**、`publish.py`/`commit_publish.py` 落地与路径白名单。
- **代眼睛（只有看不见图的模型需要）**：`atelier_canvas.py` 受控画布——文字必须走 `.text()`，越界/字号过小/缺字/压字**当场抛错**；`preview.py` 把渲染结果压成模型读得懂的占位图与直方图（纯数组运算，不调模型）；`compose.py` 写→检查→执行→报错回灌，最多 7 轮；`lint.py` 在最终像素上复查白底白字、图层盖字、画布空。
- **安全底线（只要「模型写代码、我们执行」就必须有，与视力无关）**：`guard.py` AST 静态检查、`runner.py` 子进程隔离，加上 workflow 层面 `generate` 步骤 `permissions: {}` + `persist-credentials: false`。

`verify.py` **的证据闸门 2026-08-12 下线了，代码保留**。它原来把模型声称的 evidence 拿去和抓回来的网页原文逐字比对，让「核不实就换题」从叮嘱变成程序事实。下线的理由不是它没用，而是它只装在走 `agents/` 的那几方身上，而 Codex 那条线的核实一直是自我声明——**同一条章程条款在两侧强制力不同，本身就是一种不公平，会污染对照**。核实改由事后进行：另一个 AI 在页面上对已发布的卡逐条核实点评。所以 `claims[]` 照旧收集、照旧存档（写进 `text/*.md` 的「## 引用」一节），只是不再拦人；真要核的时候 `verify.check()` 原地就能用。

**仍在跑的是 `verify.sanitize()`**，它和核实无关、别跟着一起撤：`source` 必须是 http(s)（挡 `javascript:`）、卡面文字不许夹代码围栏/链接/控制字符（那两个字符串来自读过网页的会话，会印上卡面、写进 CSV、显示在网站上）、以及章程第 6 节改动 ④ 的繁简字形判定。

**加一家 AI 的完整清单在 `HANDOFF-接入新AI.md` 第 5 节。** 同厂另一个模型只需在 `config.AI_REGISTRY` 加一行 + 复制一份 workflow；别家厂商多写一个 `client.py`。漏掉 `_headers`、`index.html` 的 `LEDGERS`、`watchdog.yml` 的标题循环**不会报错，只会安静地坏掉**。

## 硬约束（都是事故换来的，不是风格偏好）

**共用**

- `_headers` 里各家 `web/*` 都是一年 immutable，靠「文件名带编号所以内容永不变」这个假设成立——**不要原地覆盖已发布的图**。CSV 是 5 分钟缓存，**每加一份台账都要在 `_headers` 单列一条**，漏了那份就落到默认策略、新卡迟迟不出现在站上。
- **台账只许追加，不许改写既有行。** 档案馆和画廊的区别就在这里。允许新增行、末尾加列、把空字段回填上；不允许改已有值、删行、插列或改列名。`ledger-guard.yml` 在每次涉及台账的 push 上机械执行，本地用 `tools/check_ledger_append_only.py` 复现。
- **台账 `ai` 列的 key 定了就不能改**。已发布的行里存着它，改了前端认不出历史卡片，而 `web/*` 一年 immutable，改不回来。
- **`model` 列写解析后的版本串，不写别名。** `client.py` 记的是响应回声的 `data["model"]`，拿不到才退回请求用的别名。`deepseek-v4-flash` 总有一天会下线或被换掉权重，那时「这只手 2026 年是这样画画的」还站不站得住，全看这一列。别名会漂，档案不能漂。
- **`prompts/card-charter.md` 是创作要求的唯一真相源**，任何一方不得在自己的环境说明里另写一份，`tools/verify_charter.py` 把关。
- **`.bat` 必须是 CRLF 行尾且纯 ASCII。** LF-only 的 .bat 双击后静默什么都不做；UTF-8 中文会让 cmd.exe 按 OEM 代码页逐字节读时移位撑爆解析器。要中文 commit message 就另写 UTF-8 文件用 `git commit -F`，并在 `git add -A` 之前把它 move 出仓库。
- `.assetsignore`：Workers 不像 Pages 会自动排除 `.git`/`node_modules`，必须手写；`_headers` 和 `_redirects` **不能**写进去，写了反而失效。
- `wrangler.jsonc` 的 `name` 必须是 `claudeatelier`，与 Cloudflare 上的 Worker 名一致，改了直接构建失败。
- 绝不向用户索要 token / 密码 / 凭据，也不把凭据写进任何文件。

**Codex 那条线（Cowork 沙箱）**

- **不要从 Linux 沙箱跑写操作型 git。** 挂载没给 `.git` 的删除权限，`commit` 会成功但删不掉自己的锁文件，之后每次 git 都死在 `Unable to create index.lock`。2026-08-05 因此积压 4 张卡近 20 小时。提交后必须 `find .git -name '*.lock'` 自检清干净；删不掉就调 `mcp__cowork__allow_cowork_file_delete`。
- **沙箱不能删这个文件夹里的任何东西**，连普通文件 `rm` 都返回 `Operation not permitted`。
- **沙箱里没有浏览器**，Chromium 下不下来，别试 `playwright install`。渲染只能 Python + Pillow + numpy，2 倍分辨率程序化绘制；CJK 用 `/usr/share/fonts/opentype/noto/NotoSansCJK-*.ttc`（index 2=SC，3=TC，4=HK，0=JP，1=KR）。渲染完必须用 Read 工具把 PNG 看一遍，查溢出、重叠、方框字、字号过小——**「看得见」是能力，不是习惯**。
- **成品必须落到 `$ATELIER/Cards/{YYYY-MM}/` 并 `ls` 确认。** outputs / 会话临时目录是每次运行独立的缓存，用户找不到，早期因此丢过卡。挂载失败就跳过本次并明说。
- 沙箱里仓库挂在 `/sessions/<session>/mnt/ClaudeAtelier`，**session 名每次不同，必须实时 ls 出来，不要硬编码**。

**Actions 那几条线**

- **K/L 必须用 `ledger.kl_from_clock()`（向下取整到 4 小时班次边界），不要自己另算。** cron 迟到就会算出「迟到那一刻」的题目，和同班的其他 AI 对不上——「同一道题，不同的手」这个前提当场就断。2026-08-12 因此缺了一班、多了一张孤卡。
- **别信定时器准点**：该不该跑由 `run.py` 的 `freshness_ok()`（上一张卡多久以前）判定，cron 会迟到、会重复触发、偶尔整班不触发。
- **「本班不该出卡」≠「本班出卡失败」**，靠 `out/status.txt` 区分。不区分的话，新鲜度跳过时 `out/publish/` 是空的，会被 `if-no-files-found: error` 误判成失败——2026-08-11 因此连挂两次。
- **原图只在 artifact 里活 90 天**，`ClaudeAtelier-FetchDS` 没跑到就是永久丢失，而且无声。用 `python tools/check_originals.py` 对账。
- **失败必须有声**：每条产线的 workflow 都要有 `notify` job（失败开/更新 issue），`watchdog.yml` 每 8 小时巡检。这个项目两次积压事故都是等人发现网站不更新才知道的。
- **停线必须登记**：刻意停掉一条线（禁用 workflow、删掉本机触发任务）之后，去 `lines.json` 写上 `paused` 和原因。2026-08-14 停 Kimi 时没有这一步，watchdog 为它连报一个月、81 条评论；09-09 再停 DeepSeek 两条线后，4 条里 3 条常年红着。**告警机制的死法不是不响，是一直响。** 顺带一提，登记这件事也让「这条线什么时候为什么停的」在 git 里留下痕迹 —— Kimi 那次只在 GitHub 后台看得出来。
- **画得不好照发，画不出来才空班**（2026-08-12 改，此前是「渲染失败一律 fail closed」）。
  轮次耗尽但磁盘上有图 → 照发，台账 `flags` 记 `render-degraded`（盲线，lint 没过）
  或 `self-unsatisfied`（明线，它自己看图说还有毛病），未解决的问题写进 `text/*.md`。
  只有**连一张图都没画出来**才空班（`status=no-image`）。
  理由：空卡在展墙上只是一个格子，什么都说明不了；一张有毛病的卡是实打实的证物，
  而且毛病是看得见的，读者不会被误导。**发出去的图仍然永久不可覆盖**，所以标记
  必须和图同时落地，事后补不上。
- **加了新的 status 就要同步改 workflow 的 `if`。** `published-degraded` 是 2026-08-12
  新增的，三个 workflow 的「上传发布物」和 publish job 都补了这个分支——漏一个，
  降级的卡会被静默丢掉，而那正好是最值得展出的一批。

## 改生卡逻辑时的设计取舍

创作要求改 `prompts/card-charter.md`；Codex 的运行环境说明在 `C:\Users\human\Codex\Scheduled\verse-fact-card\SKILL.md`（全文抄录在 HANDOFF 第 5 节）。几处看似武断的规定是刻意的：

- **抽到的风格 S 是强制的**，因为模型有强烈的退回舒适区倾向，早期出现过反复只在孟菲斯和瑞士国际主义之间打转。`run.py` 把这条从祈使句变成了程序事实：模型只被告知 S，从头到尾看不到其他选项。
- **共享风格班**（章程改动 ⑤）：每天本地 12:00 那一班，S 由班次号直接算出（`S = (N/24*17) % 47 + 1`），各产出方拿到同一个。平时各方同领域、同语言、风格各自随机，「执笔者」和「风格」两个变量混在一起；这一班按住风格，唯一变量只剩执笔者本身。**跳步取 17 不取 1**：风格表按类聚集（38~47 全是立体类），顺着走会连着一周都是 3D。**各方必须从 N 独立算出，绝不能读别人的台账** —— 读别人在两方时勉强能用，方数一多就散架，还破坏隔离。
- **K、L 用时间戳算（长期均匀可复现），S 用「排除最近 15 条后随机」（短期不重复）**——两种机制，别统一成一种。
- **查重时「换个说法讲同一件事」也算重复**：冷知识重复比风格重复更伤。目前靠通读全部 quote/fact 列，几百条以后会撑不住。
- **核实环节不许跳过，核不实就换题**——最贵也最容易被「优化」掉的一步。章程照旧要求它；变的只是**谁来判**：2026-08-12 起不再由程序当场拦截，改由事后另一个 AI 在页面上逐条核实点评。所以 `claims[]`（断言 + 来源 + 逐字原句）必须一直收集并存档，那是事后核实唯一的输入。
- **`context` 字段**：research 除了 quote/fact 还交一段 2~3 句的背景，跟着 brief 进渲染会话、写进 `text/*.md`，**不上卡、不进台账、不进渲染脚本的全局命名空间**（引用不到就画不上去，比叮嘱可靠）。它补的是「Codex 单会话记得刚读过的原文语感、而 agents/ 这边 research 与 compose 彻底分开」这处不对等——而且没有把网页原文放进写代码的上下文，注入面一点没变。
- **受控画布只管文字（Tier 1），视觉效果完全自由（Tier 2）**。全都受控的话 S38~47 那批立体风格就废了，而那恰恰是项目说「值得多花心思」的部分。
- 汇报给用户时**不复述卡片内容，一行，不展开介绍**。

设计意图是产出「作品」而非「内容」：每张卡要在视觉上真的像那个风格，冷知识要真的少有人知且经过核实。宁可慢，不要敷衍。
