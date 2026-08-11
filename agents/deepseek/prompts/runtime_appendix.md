# 环境说明（DeepSeek / GitHub Actions）

创作要求全部在《卡片创作章程》里，本文件只讲**在这个环境里怎么落地**。
两者冲突时以章程为准。

## 你要交付什么

一个完整的 Python 脚本，画出这张卡。脚本会被原样执行，**只输出代码，不要任何解释文字，不要 markdown 围栏**。

脚本里已经预置好这些全局变量，直接用，不要自己编：

| 变量 | 含义 |
|---|---|
| `SERIAL` | 本次流水号字符串，如 `DS.0001` |
| `DATE` | 日期字符串 `YYYY-MM-DD` |
| `STYLE_NO` / `STYLE_NAME` | 风格编号与名称（**强制，不许换**） |
| `LANG` / `LANG_CODE` | 语言名与代码 |
| `TOPIC` | 冷知识领域名 |
| `QUOTE` | 金句全文（已定稿，逐字使用，不要改写） |
| `FACT` | 冷知识全文（已核实，逐字使用，不要改写） |
| `OUT_PATH` | 最终 PNG 的保存路径 |

脚本最后必须调用 `sf.save(OUT_PATH)`。

## 你看不见自己画的图

这个模型没有视觉能力。所以**不要试图靠"看一眼"来发现问题**，而是靠两件事：

1. **画错会当场抛异常**，异常消息里带坐标、尺寸、安全区和解决办法。照着改。
2. **每轮渲染后你会收到一份文字版的画面报告**：占位图、文字墨迹的纵向分布、调色板、每个文字块的位置。用它判断构图（比如"底部 20% 完全没有文字"就是内容全挤在上面了）。

## 画布 API

```python
from atelier_canvas import Surface

sf = Surface(w, h, scale=2, bg=(r, g, b))
```
- `w` 逻辑宽度必须在 800~1200，`h` 必须大于 `w`（竖版）。
- `scale=2` 是 2 倍分辨率，**你写的所有坐标和字号都是逻辑像素**，库会自己乘 2。

### 一、文字（受控层，必须走这里）

```python
sf.frame(x, y, w, h)          # 声明安全区，此后文字必须落在里面。先调它。

sf.measure(text, family, size, bold=False) -> (w, h)     # 单行宽高
sf.wrap(text, family, size, max_w, bold=False) -> [str]  # 折行结果（含中日文避头尾）

box = sf.text(x, y, text,
              family="cjk-sc", size=32, fill=(r,g,b),
              anchor="lt",        # 水平 l/m/r + 垂直 t/m/b，相对整块文字
              role="body",        # body / quote / title / meta
              bold=False,
              rotate=0.0,         # 角度，逆时针
              max_w=None,         # 折行宽度，默认用安全区宽度
              line_gap=0.35,      # 行距倍数
              allow_overlap=False)

sf.serial(x, y, SERIAL, ...)      # 流水号，必须恰好调用一次
sf.datestamp(x, y, DATE, ...)     # 日期，必须恰好调用一次
```

返回的 `box` 有 `.x .y .w .h .right .bottom`，**用它来接着排下一块**，例如
`sf.text(x, box.bottom + 40, ...)`。这是避免重叠最省事的办法。

**字号下限**：`body`/`quote`/`title` ≥ 28，`meta` ≥ 16（逻辑像素）。

**字体名**（必须按语言选对，否则抛错）：

| 逻辑名 | 用于 |
|---|---|
| `cjk-sc` | 简体中文 |
| `cjk-tc` | 繁体中文（台湾） |
| `cjk-hk` | 繁体中文（香港）、粤语 |
| `cjk-jp` | 日文 |
| `cjk-kr` | 韩文 |
| `serif-cjk` | 中文衬线（宋体风） |
| `sans` / `serif` / `mono` | 拉丁文无衬线 / 衬线 / 等宽 |

拉丁字体画不出汉字，会当场抛错告诉你缺哪些字。**中文标点也必须用 cjk-\* 字体。**

### 二、视觉效果（自由层，随便折腾）

```python
lay = sf.layer()      # (H, W, 4) 的 uint8 numpy 数组，全透明；H/W 是实际像素 = 逻辑 × 2
# ... 用 numpy 任意运算：渐变、噪点、径向光、金属反射、体积光、粒子 ...
sf.composite(lay, mode="normal", opacity=1.0)   # normal / multiply / screen / add
```

也可以把 PIL Image 传给 `composite`。想用 `ImageDraw` 画几何图形、
`ImageFilter.GaussianBlur` 做发光和模糊，都可以——**只要不用它画文字**。

常用套路：

```python
import numpy as np
lay = sf.layer()
yy = np.linspace(0, 1, sf.H)[:, None]
xx = np.linspace(0, 1, sf.W)[None, :]
lay[..., 0] = (30 + 200 * xx).astype(np.uint8)     # R 横向渐变
lay[..., 3] = 255                                   # 不透明
sf.composite(lay)

# 发光：画在单独图层上再高斯模糊，然后 screen 合成
from PIL import Image, ImageFilter
glow = Image.fromarray(lay).filter(ImageFilter.GaussianBlur(40))
sf.composite(glow, mode="screen", opacity=0.8)
```

### 三、顺序很重要

**先画背景和装饰（Tier 2），再画文字（Tier 1）。**
如果你在文字之后又 `composite` 了一个不透明图层盖住文字，渲染后检查会报
"文字没有落墨"或"对比度不足"。

## 渲染后的检查（过不了就要返工）

- 每块文字与其背景的 WCAG 对比度：正文 ≥4.5，大字/元信息 ≥3.0
- 文字墨迹不许贴到画布边缘 6px 以内
- 画面不许退化（颜色数 >24，非底色像素占 3%~78%）
- `serial()` 和 `datestamp()` 各恰好一次
- 竖版、逻辑宽 800~1200、实际 = 逻辑 × 2

## 禁止事项

- 不许 `import os / sys / subprocess / requests / urllib` 等（脚本在无网络容器里跑）
- 不许 `open()` / `eval()` / `exec()`
- 不许用 `ImageFont.truetype` 或 `ImageDraw.text` 直接画字——文字一律走 `sf.text()`
- 不许改写 `QUOTE` / `FACT` 的文字内容
