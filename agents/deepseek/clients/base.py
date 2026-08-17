"""OpenAI 形状的 chat/completions 传输层，各厂商共用。

为什么两家挤在一个文件里：DeepSeek 和 Kimi 的接口**现在**逐字同形
（messages / tools / response_format / Bearer），差异全在参数名和 key 变量上，
而那些已经在 config.PROVIDERS 里。真到某家分岔了，它的 clients/*.py 自己覆盖
就行 —— 分文件是为那一天准备的，不是因为今天有差异。

实测要点（DeepSeek 上撞出来的，对任何一家都成立）：
  · reasoning_tokens 是 completion_tokens 的子集，会挤占可见输出 ——
    token 预算必须给足，否则拿到空 content 却看不出原因。
  · 遇到过 IncompleteRead（响应被截断），不重试就白白报废一整张卡。
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request

import config


class ClientError(RuntimeError):
    pass


def api_key():
    """按 config.KEY_ENVS 的顺序找第一个非空的。

    **绝不把 key 写进任何文件、任何日志、任何异常消息。**
    下面的报错只说环境变量名，不回显取到的值。
    """
    for name in config.KEY_ENVS:
        v = os.environ.get(name, "").strip()
        if v:
            return v
    raise ClientError(
        "没找到 API key。请设置环境变量 {}（本地用 shell 导出，"
        "CI 里用仓库 secret —— 不要写进任何文件）。".format(
            " 或 ".join(config.KEY_ENVS)))


def attach_images(messages, images, mime="image/jpeg"):
    """把图挂到最后一条 user 消息上，转成 OpenAI 的 content 数组形状。

    Kimi 不收公网图片 URL，只认 base64 data URI 或 Files API 的 ms:// —— 用前者。
    图放在文字**前面**：多模态模型普遍对"先看图再读要求"更敏感。
    """
    if not images:
        return messages
    out = list(messages)
    for i in range(len(out) - 1, -1, -1):
        if out[i].get("role") == "user":
            text = out[i].get("content") or ""
            parts = []
            for raw in images:
                b64 = base64.b64encode(raw).decode("ascii")
                parts.append({"type": "image_url", "image_url": {
                    "url": "data:{};base64,{}".format(mime, b64)}})
            if isinstance(text, str):
                parts.append({"type": "text", "text": text})
            else:
                parts.extend(text)
            out[i] = dict(out[i], content=parts)
            return out
    raise ClientError("要附图但 messages 里没有 user 消息")


def chat(messages, tools=None, max_tokens=None, json_mode=False,
         timeout=None, key=None, verbose=True, images=None, reasoning=None):
    """返回 (message_dict, meta)。message_dict 是原始 assistant 消息。"""
    key = key or api_key()

    payload = {"model": config.MODEL,
               "messages": attach_images(messages, images)}
    # 参数名按厂商来：Kimi 的 max_tokens 已弃用，用 max_completion_tokens。
    payload[config.TOKEN_PARAM] = max_tokens or config.MAX_TOKENS
    if tools:
        payload["tools"] = tools
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if reasoning and config.REASONING_PARAM:
        payload[config.REASONING_PARAM] = reasoning
    body = json.dumps(payload).encode()

    endpoint = config.API_BASE.rstrip("/") + "/chat/completions"
    last = None
    t0 = time.time()
    for attempt in range(1, config.HTTP_RETRIES + 1):
        req = urllib.request.Request(
            endpoint, data=body, method="POST",
            headers={"Authorization": "Bearer " + key,
                     "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout or config.HTTP_TIMEOUT) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (408, 429, 500, 502, 503, 504) or attempt == config.HTTP_RETRIES:
                detail = ""
                try:
                    detail = e.read().decode()[:300]
                except Exception:
                    pass
                raise ClientError("HTTP {}：{}".format(e.code, detail))
        except Exception as e:
            last = e
            if attempt == config.HTTP_RETRIES:
                raise ClientError("{}：{}".format(type(e).__name__, e))
        wait = 4 * (2 ** (attempt - 1))
        if verbose:
            print("    [传输故障 {}：{}] {}s 后重试（{}/{}）".format(
                type(last).__name__, str(last)[:60], wait, attempt, config.HTTP_RETRIES))
        time.sleep(wait)

    ch = data["choices"][0]
    u = data.get("usage", {}) or {}
    # 输入 token 与其中的缓存命中数。**这两个数以前没记，是个代价不小的疏漏**：
    # 2026-08-12 第一张 K3 卡花了 14 元，其中约 12.6 元在输入上，而当时日志里
    # 只有输出 token，根本看不出钱花在哪儿。缓存命中价通常是未命中的十分之一，
    # 命中率是这条线成本的头号变量，必须能看见。
    #
    # 各家字段名不统一：Moonshot/OpenAI 走 prompt_tokens_details.cached_tokens，
    # DeepSeek 走顶层的 prompt_cache_hit_tokens。两个都认。
    cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
    if cached is None:
        cached = u.get("prompt_cache_hit_tokens")
    meta = {
        "sec": round(time.time() - t0, 1),
        "in": u.get("prompt_tokens"),
        "cached": cached,
        "out": u.get("completion_tokens"),
        "reasoning": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        "finish": ch.get("finish_reason"),
        # 服务端回声的模型号。台账优先记它。
        #
        # 这是档案馆相对画廊唯一不可替代的价值：一个模型别名总有一天会下线、
        # 会被悄悄换掉权重，那时「这只手 2026 年是这样画画的」还站不站得住，
        # 全看这一列写的是版本还是别名。
        #
        # **已知缺口**：并非每家都回解析后的版本串。Kimi 文档说响应里的
        # model 就是请求里那个别名 —— 那条线的这一列只能是别名，不是版本。
        # 记在这里，免得后人以为它是版本。
        "model": data.get("model") or None,
        # 后端配置指纹。**它补的正是上面那条「已知缺口」的另一半**：
        # 别名会漂，版本串也未必够 —— 同一个 deepseek-v4-flash 在两个月里
        # 可以是不同日期后缀的权重，回声的 model 却一模一样。指纹是这两次
        # 之间唯一看得出差别的东西。
        #
        # 只记录，不展出：画廊没有它的位置，档案馆没它不成立。
        # 各家填不填、填什么全看厂商，拿不到就是 None（读作「不知道」，
        # 不是「没变过」）。
        "fingerprint": data.get("system_fingerprint") or None,
        "id": data.get("id") or None,
    }
    return ch["message"], meta


def extract_json(text):
    """从可能夹着散文或围栏的回复里挖出第一个 JSON 对象。"""
    import re
    if not text:
        raise ClientError("模型没有返回任何内容")
    m = re.findall(r"```(?:json)?\s*\n(.*?)```", text, re.S)
    for blob in (m or []) + [text]:
        blob = blob.strip()
        i, j = blob.find("{"), blob.rfind("}")
        if i < 0 or j <= i:
            continue
        try:
            return json.loads(blob[i:j + 1])
        except Exception:
            continue
    raise ClientError("回复里解析不出 JSON：{!r}".format((text or "")[:200]))
