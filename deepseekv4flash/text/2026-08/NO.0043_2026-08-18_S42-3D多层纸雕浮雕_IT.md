# NO.0043

- 日期：2026-08-18 21:00
- 风格：3D 多层纸雕浮雕（多层纸片叠加，每层柔和投影形成真实深度，剪影式山峦或波纹层次）（S=42）
- 语言：意大利文
- 冷知识领域：数学与数字
- 生成：DeepSeek（deepseek-v4-flash）

## 金句

> Basta un punto in più perché l'ordine perfetto si rompa: è lì che comincia la vera matematica. （中文翻译：只要再多一个点，完美的秩序就会破裂——真正的数学正是从那里开始的。）

## 冷知识

Metti n punti su una circonferenza e unisci ogni coppia di punti con una corda: il numero massimo di regioni in cui il cerchio viene diviso è 1, 2, 4, 8, 16, 31… All'inizio la sequenza raddoppia come le potenze di 2, ma al sesto punto la regola si spezza: 31, non 32. （中文翻译：在圆周上取 n 个点，把每两个点连成一条弦，圆最多被分成 1、2、4、8、16、31……块。开头数列像 2 的幂一样翻倍，可到第 6 个点时规律破裂——是 31，不是 32。）

来源：https://en.wikipedia.org/wiki/Moser%27s_circle_problem

## 背景

*（不印在卡面上，只用来帮渲染决定构图与意象。）*

画面：圆上从 1 到 5 个点两两连线，区域数 1→2→4→8→16，每步都正好翻倍，像极了 2 的幂；可第 6 个点一加入，15 条弦织成一张网，得到的却是 31 块而非 32——规律在最后一步破功。秘密在弦的交点：每 4 个点产生一个交点、每个交点多切出一块，公式是 C(n,4)+C(n,2)+1。1949 年 Leo Moser 用这个例子警告「别从少量观察就归纳」；同一串数 1、2、4、8、16、31 也恰好是 4 维空间被超平面切分的最大块数，画卡时可在圆外留一条「更高维」的暗示。

## 引用

*（模型选题时声称的证据，**未经程序校验**，留作事后核实。）*

1. 在圆周上取 n 个点两两连线，圆最多被分成的区域数为 1、2、4、8、16、31、57、99、163、256……（OEIS A000127）
   - 来源：<https://en.wikipedia.org/wiki/Moser%27s_circle_problem>
   - 原句：resulting in the sequence 1, 2, 4, 8, 16, 31, 57, 99, 163, 256, ... (sequence A000127 in the OEIS).
2. 数列前五项与 2 的幂完全一致（2 的 0 到 4 次方），从第 6 项起分道扬镳：第 6 项是 2^5−1=31，而非 32
   - 来源：<https://oeis.org/A000127>
   - 原句：As a(n) = 2^(n-1) for n = 1..5, it is misleading to believe that a(n) = 2^(n-1) for n > 5 (see Patrick Popescu-Pampu link); other curiosities: a(6) = 2^5 - 1 and a(10) = 2^8.
3. （交叉印证，独立来源）同一数列 1、2、4、8、16、31……是 Moser 圆分割问题的答案
   - 来源：<https://mathworld.wolfram.com/CircleDivisionbyChords.html>
   - 原句：The first few values are 1, 2, 4, 8, 16, 31, 57, 99, 163, 256, ... (OEIS A000127).
4. 1949 年 Leo Moser 用这个数列警示：仅凭少数观察就做归纳是有风险的
   - 来源：<https://en.wikipedia.org/wiki/Moser%27s_circle_problem>
   - 原句：As Leo Moser noted in 1949, this sequence demonstrates the risk of generalising from only a few observations.

---
图片：[原图](../../Cards/2026-08/NO.0043_2026-08-18_S42-3D多层纸雕浮雕_IT.png) ｜ [压缩版](../../web/2026-08/NO.0043_2026-08-18_S42-3D多层纸雕浮雕_IT.webp)
