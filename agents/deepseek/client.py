"""客户端门面：按 config.PROVIDER 转调 clients/ 里那一家。

保留这一层，是为了让 research.py / compose.py / compose_vision.py 照旧写
`client.chat(...)` —— 加一家厂商不该让调用方跟着改。

（2026-08-12 之前这个文件就是 DeepSeek 的实现本身，96 行。接 Kimi 时按
`HANDOFF-接入新AI.md` 5.2 的建议拆成了 clients/ 一家一个文件。）
"""
import clients
from clients.base import ClientError, extract_json  # noqa: F401

_IMPL = None


def impl():
    global _IMPL
    if _IMPL is None:
        _IMPL = clients.get()
    return _IMPL


def chat(messages, **kw):
    """返回 (message_dict, meta)。

    常用关键字：
      tools / max_tokens / json_mode / timeout / verbose
      images   —— [bytes, ...]，只有看得见图的那几家收，别家会当场报错
      stage    —— 'render' / 'research' / 'critique'，语义档位，
                  认 reasoning_effort 的厂商据此选思考深度，别家忽略
    """
    return impl().chat(messages, **kw)
