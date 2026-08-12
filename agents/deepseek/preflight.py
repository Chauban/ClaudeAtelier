"""开跑前的凭据自检：一次最小请求，确认 key 能用。

为什么单独一步：不做的话，一把不能用的 key 要等到 research 深处才炸出来，
栈里全是 urllib 的帧，日志末尾一行 401，看不出到底是 key 错了、host 错了、
还是余额没充。而这三件的处理方式完全不同。

**绝不打印 key 本身，也绝不打印它的任何片段。** 这个仓库是公开的，Actions
日志跟着公开；GitHub 会自动遮蔽 secret 的原值，但遮不住由它派生出来的东西。
所以这里只报长度和格式，那两个数足够区分「粘贴时缺了几位」和「打错了站」。
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config           # noqa: E402
from clients import base  # noqa: E402

# 同一家厂商的另一个站点。两边的 key **不通用**，而错拿的症状恰恰是 401，
# 与「key 打错了」长得一模一样 —— 所以自检时顺手问一下另一边。
SIBLING = {
    "https://api.moonshot.cn": "https://api.moonshot.ai",
    "https://api.moonshot.ai": "https://api.moonshot.cn",
}


def probe(host, key, timeout=20):
    """GET {host}/v1/models。返回 (状态码, 响应体前 200 字)。"""
    url = host.rstrip("/")
    if not url.endswith("/v1"):
        url += "/v1"
    url += "/models"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(200).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read(200).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body
    except Exception as e:
        return None, "{}: {}".format(type(e).__name__, e)


def main():
    print("[凭据自检] {} / {}".format(config.AI_LABEL, config.MODEL))
    try:
        key = base.api_key()
    except base.ClientError as e:
        print("  {}".format(e))
        return 2

    # 只报形状，不报内容
    print("  key：长度 {}，前缀 {}".format(
        len(key), "sk-" if key.startswith("sk-") else "（不是 sk- 开头）"))
    if len(key) < 20:
        print("  ! 太短了，多半是粘贴时截断了，或者把 key 的名字当成值填了进去。")

    base_url = config.API_BASE.rstrip("/").replace("/v1", "")
    code, body = probe(config.API_BASE, key)
    print("  {} -> HTTP {}".format(config.API_BASE, code))
    if code == 200:
        try:
            n = len(json.loads(body + "]}" if not body.endswith("}") else body)
                    .get("data", []))
        except Exception:
            n = None
        print("  通过。" + ("可用模型 {} 个。".format(n) if n else ""))
        return 0

    print("  响应：{}".format(body[:200]))

    sib = SIBLING.get(base_url)
    if sib and code in (401, 403):
        c2, b2 = probe(sib, key)
        print("  顺手问另一个站点 {} -> HTTP {}".format(sib, c2))
        if c2 == 200:
            print("\n  ★ 这把 key 属于 {}，不属于 {}。".format(sib, base_url))
            print("    改 config.PROVIDERS['{}']['api_base'] 为 {}/v1，"
                  "或者去对应控制台重新申请一把。".format(config.PROVIDER, sib))
            return 1

    if code in (401, 403):
        print("\n  ★ key 被拒。常见原因，按可能性排：")
        print("    1. 粘贴时带了空格/换行，或少粘了几位（对一下上面的长度）")
        print("    2. 在另一个站点的控制台申请的（上面已经替你问过了）")
        print("    3. key 刚建还没生效，或账户未达最低充值门槛")
    elif code == 429:
        print("\n  ★ 限流或余额不足 —— key 本身是好的。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
