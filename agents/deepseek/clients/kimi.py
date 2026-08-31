"""Kimi（Moonshot）客户端 —— 原生多模态，这条线的模型看得见自己画的图。

接口是 OpenAI 形状，所以传输层直接用 base。这里只处理三处已知差异：

  · token 参数叫 max_completion_tokens（max_tokens 已弃用）—— 在 config.PROVIDERS
  · reasoning_effort: low / high / max，默认 max，K3 常开思考 —— 见下面的 DEFAULT_EFFORT
  · 图只收 base64 data URI 或 Files API 的 ms://，**不收公网 URL** —— 见 base.attach_images

尚未实测、跑通后回填的：单次响应最长耗时、是否会出现截断、图片计费的实际量级。
在那之前 HTTP_TIMEOUT / HTTP_RETRIES 沿用 DeepSeek 那条线撞出来的值。
"""
from clients.base import ClientError, chat as _chat, extract_json  # noqa: F401

# 各阶段默认的思考档位。三步都给 high —— 选题核实、写渲染代码、看图自检，
# 要的都是判断力，省在这里是省错了地方。
#
# 2026-09-01 把 render 从 low 改回 high。原来的理由是「DeepSeek 那条线上
# 『推理烧光预算、可见输出为零』的坑（config.py 里记着）在常开思考的模型上
# 更容易撞」—— 但那个坑是 DeepSeek 撞的，K3 一次都没撞过。拿别家的事故按住
# 这只手的思考深度，等于让它带着减半的算力去答同一道题，而 Claude 那条线
# 写渲染脚本时想多久都行。**那不是能力差别，是规则差别。**
#
# 真撞上了有兜底：compose_vision.run() 遇到空输出会原样重发那一轮，并把这张卡
# 剩下的轮次都降到 low。降档是事后止损，不是每张卡预先付的税。
EFFORT = {
    "render": "high",
    "research": "high",
    "critique": "high",
}


def chat(messages, stage=None, reasoning=None, **kw):
    """stage 是本项目的语义档位（render / research / critique），
    显式传 reasoning 则优先。"""
    if reasoning is None and stage:
        reasoning = EFFORT.get(stage)
    return _chat(messages, reasoning=reasoning, **kw)
