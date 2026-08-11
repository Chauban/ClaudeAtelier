"""受控画布：把「看图找毛病」换成「画的时候就报错」。

设计要点
--------
盲模型不会看图，但极擅长修带行号和坐标的报错。所以文字绘制统一走
Surface.text()，越界／字号过小／缺字／压字当场抛 DrawError，消息里带上
肇事字符串、两个 bbox、画布尺寸和安全区 —— 正是它需要的全部信息。

两层，故意的
------------
Tier 1（受控）：文字与编号日期。必须走 .text()/.serial()/.datestamp()。
Tier 2（自由）：一切视觉效果。.layer() 拿到裸 numpy RGBA 数组，随便做
    渐变、噪点、模糊、金属流体、体积光，然后 .composite() 合上去。
    完全不受限 —— 否则 S38~47 那批立体风格就废了，而那恰恰是项目说
    「值得多花心思」的部分。

模型付出的全部代价：文字用 .text() 而不是 draw.text()，且文字画在背景之后。
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import fonts as _fonts

# 逻辑像素下的字号下限。正文 28 来自章程，元信息（编号/日期）放宽到 16。
MIN_SIZE = {"body": 28, "quote": 28, "title": 28, "meta": 16}
# 只有这几类彼此不许重叠；meta 可以贴着装饰走。
SOLID_ROLES = {"body", "quote", "title"}
ROLES = set(MIN_SIZE)

# 禁则处理（避头尾）：中日韩排版里这些标点不许出现在行首 / 行尾。
NO_LINE_START = set("，。、；：？！）］｝〕〉》」』】·ー～%,.;:?!)]}>\"'…‧・")
NO_LINE_END = set("（［｛〔〈《「『【([{<\"'“‘")


class DrawError(RuntimeError):
    """绘制期违规。消息面向盲模型，必须自带足够的定位信息。"""


class Box:
    __slots__ = ("x", "y", "w", "h", "role", "text", "size", "font", "fill", "mask_bbox")

    def __init__(self, x, y, w, h, role, text, size, font, fill):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.role, self.text, self.size, self.font, self.fill = role, text, size, font, fill
        self.mask_bbox = None

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def overlaps(self, o, pad=0):
        return not (self.right + pad <= o.x or o.right + pad <= self.x
                    or self.bottom + pad <= o.y or o.bottom + pad <= self.y)

    def __repr__(self):
        return "Box({},{} {}x{} role={} {!r})".format(
            round(self.x), round(self.y), round(self.w), round(self.h),
            self.role, (self.text or "")[:18])


_LAST = []


def last_surface():
    """最近创建的 Surface。让 runner 不必猜模型把变量叫什么名字。"""
    return _LAST[-1] if _LAST else None


class Surface:
    def __init__(self, w, h, scale=2, bg=(255, 255, 255)):
        _LAST.append(self)
        if not (800 <= w <= 1200):
            raise DrawError(
                "逻辑宽度必须在 800~1200 之间（章程第 9 节），你给的是 {}".format(w))
        if h <= w:
            raise DrawError(
                "必须是竖版：高({})要大于宽({})（章程第 9 节）".format(h, w))
        self.w, self.h, self.scale = int(w), int(h), int(scale)
        self.W, self.H = self.w * self.scale, self.h * self.scale
        self.img = Image.new("RGB", (self.W, self.H), tuple(bg[:3]))
        self.boxes = []              # 已绘制的 Tier1 文字框
        self.ink = Image.new("L", (self.W, self.H), 0)   # 文字墨迹累积掩码
        self._frame = (0, 0, self.w, self.h)
        self._serial_done = 0
        self._date_done = 0
        self._composites = 0

    # ---------------------------------------------------------------- 安全区
    def frame(self, x, y, w, h):
        """声明安全区：此后所有文字必须落在其中。坐标为逻辑像素。"""
        if x < 0 or y < 0 or x + w > self.w or y + h > self.h:
            raise DrawError("安全区 ({},{},{}x{}) 超出画布 {}x{}".format(
                x, y, w, h, self.w, self.h))
        self._frame = (x, y, w, h)
        return self._frame

    # ---------------------------------------------------------------- 字体
    def _font(self, family, size, bold=False):
        path, idx = _fonts.resolve(family, bold)
        try:
            return ImageFont.truetype(path, int(round(size * self.scale)), index=idx)
        except Exception as e:
            raise DrawError("字体加载失败 {}#{}：{}".format(path, idx, e))

    def measure(self, text, family="sans", size=32, bold=False):
        """返回单行文字的逻辑宽高。"""
        f = self._font(family, size, bold)
        l, t, r, b = ImageDraw.Draw(self.img).textbbox((0, 0), text, font=f)
        return ((r - l) / self.scale, (b - t) / self.scale)

    def wrap(self, text, family="sans", size=32, max_w=None, bold=False):
        """按逻辑宽度折行。CJK 逐字断行，拉丁按词断行，两者混排也正确。

        含禁则处理（避头尾）：标点不许出现在行首，开引号不许留在行尾。
        盲模型看不见「逗号跑到行首」这种事，但它是机械规则不是审美判断，
        所以在这里根治，而不是指望模型自己发现。
        """
        max_w = max_w if max_w is not None else self._frame[2]
        f = self._font(family, size, bold)
        draw = ImageDraw.Draw(self.img)
        limit = max_w * self.scale

        def wpx(s):
            l, _, r, _ = draw.textbbox((0, 0), s, font=f)
            return r - l

        lines, cur = [], ""
        i, n = 0, len(text)
        while i < n:
            ch = text[i]
            if ch == "\n":
                lines.append(cur)
                cur = ""
                i += 1
                continue
            # 拉丁词整体推进，避免把单词劈开
            if ch.isalnum() and ord(ch) < 0x2E80:
                j = i
                while j < n and (text[j].isalnum() or text[j] in "'-") and ord(text[j]) < 0x2E80:
                    j += 1
                chunk = text[i:j]
            else:
                chunk = ch
            trial = cur + chunk
            if cur and wpx(trial) > limit:
                head, tail = cur.rstrip(), chunk.lstrip() if chunk != " " else ""
                # 禁则一：标点不能起行 —— 把上一行末尾的字一起挪下来，
                # 这样宽度仍然守得住（上一行只会变短）。
                guard = 0
                while head and tail and tail[0] in NO_LINE_START and guard < 4:
                    head, tail = head[:-1], head[-1] + tail
                    guard += 1
                # 禁则二：开引号/开括号不能留在行尾。
                guard = 0
                while head and head[-1] in NO_LINE_END and guard < 4:
                    head, tail = head[:-1], head[-1] + tail
                    guard += 1
                if not head:            # 整行都被挪空了，放弃禁则，保宽度
                    head, tail = cur.rstrip(), chunk.lstrip() if chunk != " " else ""
                lines.append(head)
                cur = tail
            else:
                cur = trial
            i += len(chunk)
        if cur.strip():
            lines.append(cur.rstrip())
        return lines or [""]

    # ---------------------------------------------------------------- 文字
    def text(self, x, y, text, family="sans", size=32, fill=(0, 0, 0),
             anchor="lt", role="body", bold=False, rotate=0.0,
             max_w=None, line_gap=0.35, allow_overlap=False):
        """画一段文字（自动折行）。返回 Box。任何违规当场抛 DrawError。

        anchor：两字母，水平 l/m/r + 垂直 t/m/b，相对整块文字。
        """
        if role not in ROLES:
            raise DrawError("role 必须是 {} 之一，你给的是 {!r}".format(sorted(ROLES), role))
        text = "" if text is None else str(text)
        if not text.strip():
            raise DrawError("role={} 的文字是空的，没有意义".format(role))

        # --- 字号下限
        if size < MIN_SIZE[role]:
            raise DrawError(
                "字号过小：role={} 用了 {}px，下限 {}px（章程第 10 节）。\n"
                "  文字：{!r}\n"
                "  正文过小会在缩略图上糊掉，请调大字号或缩短文字。".format(
                    role, size, MIN_SIZE[role], text[:40]))

        # --- 豆腐块：画之前就查 cmap
        miss = _fonts.missing_glyphs(text, family, bold)
        if miss:
            raise DrawError(
                "字体 {!r} 画不出这些字符，会变成方框：{}\n"
                "  文字：{!r}\n"
                "  中文/日文/韩文必须用 cjk-sc / cjk-tc / cjk-hk / cjk-jp / cjk-kr，"
                "拉丁文用 sans / serif / mono（章程第 10 节）。".format(
                    family, miss, text[:60]))

        fx, fy, fw, fh = self._frame
        max_w = fw if max_w is None else max_w
        lines = self.wrap(text, family, size, max_w, bold)

        f = self._font(family, size, bold)
        draw = ImageDraw.Draw(self.img)
        asc, desc = f.getmetrics()
        line_h = (asc + desc) / self.scale
        step = line_h * (1.0 + float(line_gap))
        blk_w = max(self.measure(ln, family, size, bold)[0] for ln in lines) if lines else 0
        blk_h = line_h + step * (len(lines) - 1)

        # --- 锚点 -> 左上角
        ax, ay = (anchor + "lt")[:2]
        ox = {"l": 0, "m": -blk_w / 2, "r": -blk_w}.get(ax, 0)
        oy = {"t": 0, "m": -blk_h / 2, "b": -blk_h}.get(ay, 0)
        bx, by = x + ox, y + oy

        # --- 旋转后用外接轴对齐框做碰撞与越界判断
        if rotate:
            rad = math.radians(rotate)
            c, s = abs(math.cos(rad)), abs(math.sin(rad))
            rw, rh = blk_w * c + blk_h * s, blk_w * s + blk_h * c
            cx, cy = bx + blk_w / 2, by + blk_h / 2
            gx, gy, gw, gh = cx - rw / 2, cy - rh / 2, rw, rh
        else:
            gx, gy, gw, gh = bx, by, blk_w, blk_h

        box = Box(gx, gy, gw, gh, role, text, size, family, fill)

        # --- 越界
        if gx < fx - 0.5 or gy < fy - 0.5 or gx + gw > fx + fw + 0.5 or gy + gh > fy + fh + 0.5:
            raise DrawError(
                "文字超出安全区。\n"
                "  文字      : {!r}\n"
                "  实际占位  : x={:.0f} y={:.0f} w={:.0f} h={:.0f}（右={:.0f} 底={:.0f}）\n"
                "  安全区    : x={} y={} w={} h={}（右={} 底={}）\n"
                "  画布      : {}x{} 逻辑像素\n"
                "  折行结果  : {} 行，最宽 {:.0f}px\n"
                "  解决办法  : 调小字号、传更小的 max_w、换锚点，或把起点往回挪。".format(
                    text[:40], gx, gy, gw, gh, gx + gw, gy + gh,
                    fx, fy, fw, fh, fx + fw, fy + fh, self.w, self.h,
                    len(lines), blk_w))

        # --- 压字
        if not allow_overlap and role in SOLID_ROLES:
            for o in self.boxes:
                if o.role in SOLID_ROLES and box.overlaps(o, pad=2):
                    raise DrawError(
                        "两块文字重叠了。\n"
                        "  这次要画  : {!r}\n"
                        "              x={:.0f} y={:.0f} w={:.0f} h={:.0f}（右={:.0f} 底={:.0f}）\n"
                        "  已经画了  : {!r}\n"
                        "              x={:.0f} y={:.0f} w={:.0f} h={:.0f}（右={:.0f} 底={:.0f}）\n"
                        "  解决办法  : 把这一块往下挪到 y={:.0f} 之后，或缩短上一块。".format(
                            text[:30], gx, gy, gw, gh, gx + gw, gy + gh,
                            (o.text or "")[:30], o.x, o.y, o.w, o.h, o.right, o.bottom,
                            o.bottom + 8))

        # --- 真正绘制（旋转走临时图层）
        S = self.scale
        if rotate:
            pad = int(max(blk_w, blk_h) * S)
            tmp = Image.new("RGBA", (int(blk_w * S) + pad, int(blk_h * S) + pad), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            for i, ln in enumerate(lines):
                td.text((pad // 2, pad // 2 + i * step * S), ln, font=f, fill=tuple(fill[:3]) + (255,))
            tmp = tmp.rotate(rotate, resample=Image.BICUBIC, expand=True)
            px = int(round((gx + gw / 2) * S - tmp.width / 2))
            py = int(round((gy + gh / 2) * S - tmp.height / 2))
            self.img.paste(tmp, (px, py), tmp)
            self.ink.paste(tmp.split()[3], (px, py), tmp.split()[3])
            box.mask_bbox = (px, py, px + tmp.width, py + tmp.height)
        else:
            m = Image.new("L", (self.W, self.H), 0)
            md = ImageDraw.Draw(m)
            for i, ln in enumerate(lines):
                xx = bx * S
                if ax == "m":
                    xx = (bx + (blk_w - self.measure(ln, family, size, bold)[0]) / 2) * S
                elif ax == "r":
                    xx = (bx + blk_w - self.measure(ln, family, size, bold)[0]) * S
                pos = (xx, (by + i * step) * S)
                draw.text(pos, ln, font=f, fill=tuple(fill[:3]))
                md.text(pos, ln, font=f, fill=255)
            self.ink.paste(m, (0, 0), m)
            box.mask_bbox = (int(bx * S), int(by * S),
                             int((bx + blk_w) * S), int((by + blk_h) * S))

        self.boxes.append(box)
        return box

    def serial(self, x, y, text, **kw):
        """流水号。章程第 8 节要求必须上卡，且要融入风格语汇。"""
        kw.setdefault("role", "meta")
        b = self.text(x, y, text, **kw)
        self._serial_done += 1
        return b

    def datestamp(self, x, y, text, **kw):
        kw.setdefault("role", "meta")
        b = self.text(x, y, text, **kw)
        self._date_done += 1
        return b

    # ---------------------------------------------------------------- Tier 2
    def layer(self):
        """一张与画布同尺寸的透明 RGBA numpy 数组，随便折腾。"""
        return np.zeros((self.H, self.W, 4), dtype=np.uint8)

    def composite(self, layer, mode="normal", opacity=1.0):
        """把 Tier2 图层合上来。支持 normal/multiply/screen/add。"""
        if isinstance(layer, Image.Image):
            layer = np.array(layer.convert("RGBA"))
        layer = np.asarray(layer)
        if layer.shape[:2] != (self.H, self.W):
            raise DrawError(
                "图层尺寸 {}x{} 与画布 {}x{} 不一致（都是实际像素，"
                "记得 scale={}）".format(
                    layer.shape[1], layer.shape[0], self.W, self.H, self.scale))
        if layer.shape[2] == 3:
            layer = np.dstack([layer, np.full(layer.shape[:2], 255, np.uint8)])

        base = np.array(self.img, dtype=np.float32)
        src = layer[..., :3].astype(np.float32)
        a = (layer[..., 3:4].astype(np.float32) / 255.0) * float(opacity)

        if mode == "multiply":
            src = base * src / 255.0
        elif mode == "screen":
            src = 255.0 - (255.0 - base) * (255.0 - src) / 255.0
        elif mode == "add":
            src = np.clip(base + src, 0, 255)
        elif mode != "normal":
            raise DrawError("未知合成模式 {!r}，可用 normal/multiply/screen/add".format(mode))

        out = base * (1 - a) + src * a
        self.img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
        self._composites += 1

    # ---------------------------------------------------------------- 收尾
    def save(self, path):
        self.img.save(path, "PNG")
        return path

    def stats(self):
        return {
            "logical": (self.w, self.h), "actual": (self.W, self.H),
            "scale": self.scale, "text_boxes": len(self.boxes),
            "serial_calls": self._serial_done, "date_calls": self._date_done,
            "composites": self._composites,
        }
