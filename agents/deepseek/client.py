"""DeepSeek HTTP 客户端。带重试，供 research 和 compose 共用。

实测要点：
  · 工具调用与并行工具调用都支持，response_format:json_object 也支持。
  · reasoning_tokens 是 completion_tokens 的子集，会挤占可见输出 ——
    max_tokens 必须给足，否则拿到空 content 却看不出原因。
  · 遇到过 IncompleteRead（响应被截断），不重试就白白报废一整张卡。
"""
import json
import time
import urllib.error
import urllib.request

import config

ENDPOINT = config.API_BASE + "/chat/completions"


class ClientError(RuntimeError):
    pass


def chat(messages, tools=None, max_tokens=None, json_mode=False,
         timeout=None, key=None, verbose=True):
    """返回 (message_dict, meta)。message_dict 是原始 assistant 消息。"""
    import os
    key = key or os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise ClientError("环境变量 DEEPSEEK_API_KEY 没设置")

    payload = {"model": config.MODEL, "messages": messages,
               "max_tokens": max_tokens or config.MAX_TOKENS}
    if tools:
        payload["tools"] = tools
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    body = json.dumps(payload).encode()

    last = None
    for attempt in range(1, config.HTTP_RETRIES + 1):
        req = urllib.request.Request(
            ENDPOINT, data=body, method="POST",
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
    meta = {
        "sec": round(time.time() - t0, 1),
        "out": u.get("completion_tokens"),
        "reasoning": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
        "finish": ch.get("finish_reason"),
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
