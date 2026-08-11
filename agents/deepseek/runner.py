"""在子进程里执行模型写的渲染脚本，跑完 lint 与 preview，把报告写出来。

单独一个进程，是为了让模型脚本的崩溃、死循环、内存爆炸都不会带走编排器。
正式环境里这一层外面还要再套一个 --network none 的容器。
"""
import io
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lint            # noqa: E402
import preview         # noqa: E402
import atelier_canvas  # noqa: E402
from atelier_canvas import DrawError  # noqa: E402


def main():
    brief_path, code_path, report_path = sys.argv[1:4]
    brief = json.load(io.open(brief_path, encoding="utf-8"))
    code = io.open(code_path, encoding="utf-8").read()

    ns = {"__name__": "__render__"}
    ns.update({k: brief[k] for k in (
        "SERIAL", "DATE", "STYLE_NO", "STYLE_NAME", "LANG", "LANG_CODE",
        "TOPIC", "QUOTE", "FACT", "OUT_PATH")})

    report = {"ok": False, "stage": None, "error": None, "preview": None,
              "metrics": None, "problems": []}

    # ---------------------------------------------------- 执行
    buf = io.StringIO()
    real_stdout = sys.stdout
    sys.stdout = buf
    try:
        exec(compile(code, "render.py", "exec"), ns)
    except DrawError as e:
        sys.stdout = real_stdout
        report["stage"] = "draw"
        report["error"] = str(e)
        _finish(report, report_path, buf)
        return 1
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

    sf = atelier_canvas.last_surface()
    if sf is None:
        report["stage"] = "exec"
        report["error"] = "脚本没有创建 Surface，无从检查。必须 sf = Surface(w, h, scale=2, bg=...)。"
        _finish(report, report_path, buf)
        return 1

    # ---------------------------------------------------- 检查
    problems, metrics = lint.run(
        sf, strict=False,
        known_text=[brief.get(k) for k in ("SERIAL", "DATE", "QUOTE", "FACT")])
    report["metrics"] = metrics
    report["problems"] = problems
    try:
        report["preview"] = preview.describe(sf, metrics)
    except Exception as e:
        report["preview"] = "（画面报告生成失败：{}）".format(e)

    out = ns.get("OUT_PATH")
    if not out or not os.path.exists(out):
        problems.insert(0, "脚本没有把图保存到 OUT_PATH，最后必须调用 sf.save(OUT_PATH)。")
        report["problems"] = problems

    if problems:
        report["stage"] = "lint"
        report["error"] = "渲染后检查未通过（{} 项）：\n  - {}".format(
            len(problems), "\n  - ".join(problems))
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
