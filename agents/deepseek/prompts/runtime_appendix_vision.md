# 环境说明（看得见图的产出方 / GitHub Actions）

创作要求全部在《卡片创作章程》里，本文件只讲**在这个环境里怎么落地**。
两者冲突时以章程为准。

## 你要交付什么

一个完整的 Python 脚本，画出这张卡。脚本会被原样执行，**只输出代码，不要任何解释文字，不要 markdown 围栏**。

脚本里已经预置好这些全局变量，直接用，不要自己编：

| 变量 | 含义 |
|---|---|
| `SERIAL` | 本次流水号字符串，如 `NO.0001` |
| `DATE` | 日期字符串 `YYYY-MM-DD` |
| `STYLE_NO` / `STYLE_NAME` | 风格编号与名称（**强制，不许换**） |
| `LANG` / `LANG_CODE` | 语言名与代码 |
| `TOPIC` | 冷知识领域名 |
| `QUOTE` | 金句全文（已定稿，逐字使用，不要改写） |
| `FACT` | 冷知识全文（逐字使用，不要改写） |
| `OUT_PATH` | 最终 PNG 的保存路径 |

脚本最后必须把图存到 `OUT_PATH`（`img.save(OUT_PATH)`）。

## 你看得见自己画的图 —— 这一条是这条产线的全部重点

每一轮渲染之后，**我们会把你刚画出来的那张图发给你看**。

这里没有受控画布，没有自动的排版检查，没有人替你量对比度、查越界、找豆腐块。
越界了不会有异常，字压在装饰上不会有报错，白底白字也不会有人拦。**只有你自己的眼睛。**

所以看到图之后，你必须给出一份结构化判词，只输出这个 JSON：

```json
{
  "ok": false,
  "problems": [
    {"where": "金句第二行末尾", "what": "压在右侧的圆形装饰上，最后三个字看不清",
     "fix": "把装饰下移 60px，或者把金句的折行宽度收窄到 640"}
  ],
  "style_fidelity": 4,
  "notes": "整体像工程蓝图，但标题栏的线太细，缩略图上会消失"
}
```

- `ok`：这张卡现在能不能发出去。**只有你自己说了算。**
- `problems`：具体到位置和改法。空数组表示没毛病。
- `style_fidelity`：1~5，这张卡有多像 `STYLE_NAME` 那个风格。
- `notes`：一句话总评，可省。

要真的看。逐块过一遍：金句、冷知识、流水号、日期，每一块是不是完整、清晰、
没被盖住、没超出画布、字号在缩略图上还读得出来；然后退开看整张的构图和风格贴合度。

**说 `ok: true` 是要负责的。** 这份判词会连同卡片一起存档并公开 —— 你说没问题而
图上确实有问题，那是留得下来的记录。反过来，为了保险把没毛病的图判成有毛病、
反复重画，也一样看得出来。

## 渲染方式

沙盒里没有浏览器，不要尝试 `playwright install`。用 Python + Pillow（配合 numpy）
以 2 倍分辨率程序化绘制 PNG。

- 渐变、发光、扫描线、纹理、噪点、投影、模糊等用 numpy 数组运算 +
  `PIL.ImageFilter.GaussianBlur`；几何图形用 `ImageDraw`（polygon/ellipse/arc/line），
  旋转用 `Image.rotate` 或仿射变换。
- **文字直接用 `ImageDraw.text` + `ImageFont.truetype`**，没有别的限制。
- 先按行测量文本宽度（`draw.textbbox`）确保不溢出，排版算好总高度再定画布高度。

### 字体：先查再用，不要照抄下面这份清单

清单会过时，而漏掉一个字重就会让某些风格无谓地退回黑体。脚本里不能 `import os`，
所以**在你写脚本之前**就把字体路径定下来；截至 2026-08-12 这台机器上应当有：

| 用途 | 文件 |
|---|---|
| 中日韩黑体 | `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 与 `-Bold.ttc` |
| 中日韩衬线 | `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc` 与 `-Bold.ttc` |
| 拉丁无衬线 | `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` 及 `-Bold` |
| 拉丁衬线 | `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf` 及 `-Bold` |
| 拉丁等宽 | `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf` 及 `-Bold` / `-Oblique` |

`.ttc` 的 face 索引：**2 = 简体，3 = 繁体（台湾），4 = 繁体（香港），0 = 日文，
1 = 韩文**，例如 `ImageFont.truetype(path, size, index=2)`。**索引不许硬编码成别的值。**

两件容易踩的事：

1. **拉丁字体画不出汉字**，会变成方框。中文标点（`，。「」《》`）也必须用 CJK 字体。
2. **Noto CJK 的 SC/TC/JP/KR 各 face 覆盖的汉字几乎相同**，所以用日文 face 画简体中文
   *不会*缺字、不会报错、图上也看不太出来 —— 但字形是错的。按 `LANG_CODE` 选对索引。
3. 老报纸、水墨、侘寂、青花瓷、植物图鉴这类风格，正文该用**衬线中文 Regular**，
   别因为顺手就整段用粗体，也别退回黑体。

## 禁止事项

- 不许 `import os / sys / subprocess / requests / urllib` 等（脚本在无网络的子进程里跑）
- 不许 `open()` / `eval()` / `exec()`
- 不许改写 `QUOTE` / `FACT` 的文字内容
- 卡面上只出现 `QUOTE` / `FACT` / `SERIAL` / `DATE` 四样文字，别的都不要写上去
