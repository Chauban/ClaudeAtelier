"""对模型写的渲染脚本做 AST 静态检查。

定位：**第二道防线，不是唯一防线。**
真正的隔离是把脚本丢进 --network none 的一次性容器里跑（见 workflow）。
这里拦的是「明显不该出现的东西」，顺便给模型一条即时、可读的反馈，
省得等到容器里失败一轮才知道。
"""
import ast

# 允许导入的模块（含子模块前缀匹配）
ALLOWED_IMPORTS = {
    "math", "random", "colorsys", "itertools", "functools", "typing",
    # 排版正当需求：折行、断词、对齐都要用。2026-08-12 实测 K3 首张卡
    # 就 import re 触发了一条无谓的警告。它们都不碰 IO、不碰网络。
    "re", "string", "textwrap", "unicodedata",
    "numpy", "PIL", "atelier_canvas", "fonts",
}
# 明确禁止：网络、子进程、文件系统漫游、动态执行
BANNED_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "requests", "urllib",
    "http", "ftplib", "smtplib", "pickle", "marshal", "ctypes", "importlib",
    "pathlib", "glob", "tempfile", "webbrowser", "multiprocessing", "threading",
}
BANNED_CALLS = {
    "eval", "exec", "compile", "__import__", "open", "input",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
}
# 文字必须走 Surface；这些是绕过受控层的典型写法
TEXT_BYPASS = {"truetype", "load_default", "FreeTypeFont"}


class GuardError(RuntimeError):
    pass


def check(src, filename="render.py", allow_raw_text=None):
    """通过则返回警告列表；不通过抛 GuardError。

    allow_raw_text —— 允不允许 ImageFont.truetype / ImageDraw.text 直接画字。
        默认跟着 config.VISION 走：

        · 看不见图的模型：**不允许**。文字必须走 Surface.text()，那是它的手杖 ——
          越界、缺字、压字只能在调用当场抓出来，事后没人替它看。
        · 看得见图的模型：**允许**。逼它走受控画布等于替它检查，而「它看不看得懂
          自己画的图」正是要展出的东西。它用裸 Pillow，和 Claude 那条线一样。

        安全相关的检查（禁 import、禁 eval/open、禁 dunder）**两边完全相同** ——
        那一层与视力无关，只与「模型写代码、我们执行」有关。
    """
    if allow_raw_text is None:
        import config
        allow_raw_text = config.VISION
    try:
        tree = ast.parse(src, filename=filename)
    except SyntaxError as e:
        raise GuardError("脚本语法错误：第 {} 行 {}\n  {}".format(
            e.lineno, e.msg, (e.text or "").strip()))

    problems, warnings = [], []

    def root(name):
        return (name or "").split(".")[0]

    for node in ast.walk(tree):
        # ---- import
        if isinstance(node, ast.Import):
            for a in node.names:
                r = root(a.name)
                if r in BANNED_IMPORTS:
                    problems.append("第 {} 行：禁止 import {}".format(node.lineno, a.name))
                elif r not in ALLOWED_IMPORTS:
                    warnings.append("第 {} 行：import {} 不在白名单".format(node.lineno, a.name))
        elif isinstance(node, ast.ImportFrom):
            r = root(node.module or "")
            if r in BANNED_IMPORTS:
                problems.append("第 {} 行：禁止 from {} import ...".format(node.lineno, node.module))
            elif r and r not in ALLOWED_IMPORTS:
                warnings.append("第 {} 行：from {} import ... 不在白名单".format(node.lineno, node.module))
            for a in node.names:
                if a.name in TEXT_BYPASS and not allow_raw_text:
                    problems.append(
                        "第 {} 行：不许直接用 {} —— 文字必须走 Surface.text()，"
                        "否则越界/缺字/压字都检查不到".format(node.lineno, a.name))

        # ---- 危险调用
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            if isinstance(f, ast.Name) and f.id in BANNED_CALLS:
                problems.append("第 {} 行：禁止调用 {}()".format(node.lineno, f.id))
            if name in TEXT_BYPASS and not allow_raw_text:
                problems.append(
                    "第 {} 行：不许调用 {}() —— 文字必须走 Surface.text()".format(
                        node.lineno, name))
            # ImageDraw.text / draw.text 绕过受控层
            if isinstance(f, ast.Attribute) and f.attr == "text" and not allow_raw_text:
                base = f.value
                base_name = base.id if isinstance(base, ast.Name) else None
                if base_name and base_name not in ("sf", "surface", "canvas", "s"):
                    warnings.append(
                        "第 {} 行：{}.text(...) 看起来像绕过 Surface 直接画字。"
                        "文字一律用 sf.text()。".format(node.lineno, base_name))

        # ---- dunder 属性访问
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__") and node.attr.endswith("__"):
                if node.attr not in ("__name__", "__doc__"):
                    problems.append("第 {} 行：禁止访问 {}".format(node.lineno, node.attr))

    if problems:
        tail = ("说明：脚本在无网络的子进程里跑，只能用 PIL / numpy / math 这类纯计算库，"
                "不能读写画布之外的任何东西。"
                if allow_raw_text else
                "说明：文字必须用 sf.text()/sf.serial()/sf.datestamp()；"
                "视觉效果用 sf.layer() 拿 numpy 数组随便画，再 sf.composite() 合上去。")
        raise GuardError(
            "渲染脚本没通过静态检查：\n  - {}\n\n{}".format(
                "\n  - ".join(problems), tail))
    return warnings
