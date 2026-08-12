"""在子进程里执行渲染脚本 —— 看得见图的那条线用这个。

和 runner.py 的区别只有一条：**这里不做任何画面检查。**

runner.py 那套（受控画布 + lint 的十几项判定）是给盲模型的代眼睛。给有视力的
模型套上，等于替它把「你看没看懂自己画的图」这道题答了 —— 而那正是这个博物馆
要展出的东西。所以这里只回答两个跟艺术无关的问题：

    脚本跑起来了吗？图落地了吗？

外加几个纯客观的读数（尺寸、模式、字节数）回灌给模型。那些是 Claude 那条线
用眼睛也看得到的东西，给它不算代劳。

子进程隔离照旧 —— 那与视力无关，只与「模型写代码、我们执行」有关。
"""
import io
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BRIEF_KEYS = ("SERIAL", "DATE", "STYLE_NO", "STYLE_NAME", "LANG", "LANG_CODE",
              "TOPIC", "QUOTE", "FACT", "OUT_PATH")
# CONTEXT 刻意不在上面这张表里：它是给构图用的语感，不是卡面内容。
# 脚本里引用不到，也就画不上去 —— 比在提示词里反复叮嘱可靠。


def main():
    brief_path, code_path, report_path = sys.argv[1:4]
    brief = json.load(io.open(brief_path, encoding="utf-8"))
    code = io.open(code_path, encoding="utf-8").read()

    ns = {"__name__": "__render__"}
    ns.update({k: brief[k] for k in BRIEF_KEYS if k in brief})

    report = {"ok": False, "stage": None, "error": None, "png": None}

    buf = io.StringIO()
    real_stdout = sys.stdout
    sys.stdout = buf
    try:
        exec(compile(code, "render.py", "exec"), ns)
    except Exception:
        sys.stdout = real_stdout
        tb = traceback.format_exc()
        # 只保留 render.py 自己的帧，库内部栈对模型没用
        lines = [l for l in tb.splitlines()
                 if "render.py" in l or not l.strip().startswith("File ")]
        report["stage"] = "exec"
        report["error"] = "脚本执行出错：\n" + "\n".join(lines[-14:])
        _finish(report, report_path, buf)
        return 1
    finally:
        sys.stdout = real_stdout

    out = ns.get("OUT_PATH") or brief.get("OUT_PATH")
    if not out or not os.path.exists(out):
        report["stage"] = "save"
        report["error"] = (
            "脚本跑完了，但 OUT_PATH 上没有文件。最后必须把图存到 OUT_PATH，"
            "例如 img.save(OUT_PATH)。")
        _finish(report, report_path, buf)
        return 1

    try:
        from PIL import Image
        with Image.open(out) as im:
            w, h = im.size
            mode = im.mode
        report["png"] = {"w": w, "h": h, "mode": mode,
                         "bytes": os.path.getsize(out)}
    except Exception as e:
        report["stage"] = "save"
        report["error"] = "OUT_PATH 上的文件打不开，不是一张有效的图：{}".format(e)
        _finish(report, report_path, buf)
        return 1

    report["ok"] = True
    report["stage"] = "done"
    _finish(report, report_path, buf)
    return 0


def _finish(report, path, buf):
    report["stdout"] = buf.getvalue()[-2000:]
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
