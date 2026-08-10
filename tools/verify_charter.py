"""校验 prompts/card-charter.md 是否仍逐字忠于 SKILL.md。

为什么需要这个脚本：
    博物馆的前提是「同一道题，不同的手」。章程一旦悄悄漂移，展品的
    可比性就没了，而漂移是无声的——没人会注意到某一节被改了两个字。
    所以把这件事变成可执行的检查，而不是靠记性。

用法：
    python tools/verify_charter.py
    退出码 0 = 通过；1 = 有未标注的差异

规则：
    章程里以 '> ' 开头的行 = 声称原封不动来自 SKILL.md。
    每一行都必须能在 SKILL.md 里找到（规范化后比对）。
    确有必要的改动，必须在该行内用〔〕就地标注理由——本脚本据此放行，
    并把它计入「已标注改动」，让每一次偏离都留下痕迹。

    第 6 阶段（SKILL.md 改为引用章程）之后，本脚本会失去比对基准；
    届时应改为对着 git 历史里最后一版完整 SKILL.md 校验，或直接退役。
"""
import io
import os
import re
import sys
import unicodedata

SKILL = os.environ.get(
    "SKILL_MD", r"C:\Users\human\Claude\Scheduled\verse-fact-card\SKILL.md")
CHARTER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "prompts", "card-charter.md")

# SKILL.md 里必须出现在章程中的关键创作条款。漏掉任何一条都说明抽取不完整。
MUST_CARRY = {
    "风格表 47 项结尾": "47 3D 体积光与景深",
    "3D 类补充说明": "这类风格值得多花心思",
    "领域表 17 项结尾": "17 体育与游戏",
    "避开烂大街的冷知识": "蜂蜜不会变质",
    "语言表第 7 槽": "法文/德文/西班牙文/韩文/意大利文",
    "非中文须附中文翻译": "翻译字号略小放在原文下方",
    "金句调性要求": "冷幽默或让人释然",
    "编号须四位补零": "四位补零",
    "编号要融入风格而非水印": "而不是硬贴上去的水印",
    "设计执行举例": "构成主义用红黑斜切构图",
    "竖版与逻辑宽度": "逻辑宽度 800~1200px 自选",
    "2 倍分辨率": "deviceScaleFactor=2",
    "正文字号下限": "不小于 28px",
    "中文不能出现方框": "不能出现方框",
    "先测量再排版": "绝不能让内容超出画布或互相重叠",
    "S 强制不许换": "绝对不许自行更换",
    "S 排除最近 15 条": "最近 15 条用过的 S",
    "查重含改述": "换个说法讲同一件事",
    "核不实就换题": "不要硬着头皮上",
    "数字宁可写约": '宁可写"约"也不要写错',
    "成品自检清单": "检查溢出、重叠、方框字",
    "语言代码表": "ZH / ZH-TW / ZH-HK / YUE",
    "风格简名长度": "风格简名取 4~8 字",
}


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"^\s*[-*]\s*", "", s)
    return re.sub(r"\s+", "", s)


def main():
    for p in (SKILL, CHARTER):
        if not os.path.exists(p):
            print("找不到文件：{}".format(p))
            return 1

    skill = io.open(SKILL, encoding="utf-8").read()
    charter = io.open(CHARTER, encoding="utf-8").read()
    skill_n = norm(skill)

    # 导言（第一个 --- 之前）是章程自己的框架说明，不是声称的引用
    parts = charter.split("\n---\n", 1)
    body = parts[1] if len(parts) > 1 else charter
    offset = parts[0].count("\n") + 2 if len(parts) > 1 else 1

    ok = amended = 0
    problems = []
    for ln, line in enumerate(body.splitlines(), offset):
        if not line.startswith(">") or line.startswith(">>"):
            continue
        text = line[1:].strip()
        if not text:
            continue
        declared = "〔" in text
        text = re.sub(r"〔[^〕]*〕", "", text).strip()
        if not norm(text):
            continue
        if norm(text) in skill_n:
            ok += 1
        elif declared:
            amended += 1
            print("  [已标注改动] L{:<4} {}".format(ln, text[:70]))
        else:
            problems.append((ln, text))

    print("\n逐字命中 {} · 已标注改动 {} · 未标注差异 {}".format(
        ok, amended, len(problems)))

    for ln, t in problems:
        print("  ! L{:<4} 在 SKILL.md 中找不到：{}".format(ln, t[:120]))

    missing = [k for k, v in MUST_CARRY.items()
               if norm(v) in skill_n and norm(v) not in norm(charter)]
    for k in missing:
        print("  ! 关键条款未收入章程：{}".format(k))

    if problems or missing:
        print("\n失败：章程与 SKILL.md 已出现未声明的分歧。")
        return 1
    print("通过：章程忠于 SKILL.md，{} 项关键条款齐备。".format(len(MUST_CARRY)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
