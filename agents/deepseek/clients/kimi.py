"""Kimi（Moonshot）客户端 —— 原生多模态，这条线的模型看得见自己画的图。

接口是 OpenAI 形状，所以传输层直接用 base。这里只处理三处已知差异：

  · token 参数叫 max_completion_tokens（max_tokens 已弃用）—— 在 config.PROVIDERS
  · reasoning_effort: low / high / max，默认 max，K3 常开思考 —— 见下面的 DEFAULT_EFFORT
  · 图只收 base64 data URI 或 Files API 的 ms://，**不收公网 URL** —— 见 base.attach_images

尚未实测、跑通后回填的：单次响应最长耗时、是否会出现截断、图片计费的实际量级。
在那之前 HTTP_TIMEOUT / HTTP_RETRIES 沿用 DeepSeek 那条线撞出来的值。
"""
from clients.base import ClientError, chat as _chat, extract_json  # noqa: F401

# 各阶段默认的思考档位。
#
# 写渲染代码给 low：DeepSeek 那条线上「推理烧光预算、可见输出为零」的坑
# （config.py 里记着）在常开思考的模型上更容易撞。区别是 K3 真的认这个参数。
# 选题核实与看图自检给 high：那两步要的正是判断力，省在这里是省错了地方。
EFFORT = {
    "render": "low",
    "research": "high",
    "critique": "high",
}


def chat(messages, stage=None, reasoning=None, **kw):
    """stage 是本项目的语义档位（render / research / critique），
    显式传 reasoning 则优先。"""
    if reasoning is None and stage:
        reasoning = EFFORT.get(stage)
    return _chat(messages, reasoning=reasoning, **kw)
