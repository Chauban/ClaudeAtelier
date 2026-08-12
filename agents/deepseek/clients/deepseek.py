"""DeepSeek 客户端。

目前与 base 完全同形，只在这里挡住一件事：**它没有视觉能力**。
真给它塞图不会报错，只会安静地浪费 token 并让模型胡说 —— 与其如此，
不如让它在开发期就当场炸掉。
"""
from clients.base import ClientError, chat as _chat, extract_json  # noqa: F401


def chat(messages, images=None, stage=None, **kw):
    # stage（render/research/critique）是给认 reasoning_effort 的厂商用的语义档位。
    # DeepSeek 接受这类参数却静默忽略（config.py 里记着实测），所以这里直接吞掉，
    # 免得白发一个不起作用的字段。
    if images:
        raise ClientError(
            "DeepSeek 这条线没有视觉能力，不该给它发图。"
            "看不见的模型走 compose.py（受控画布 + 文字版画面报告），"
            "不走 compose_vision.py。")
    return _chat(messages, **kw)
