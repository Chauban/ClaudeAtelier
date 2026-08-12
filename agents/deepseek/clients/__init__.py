"""按 config.PROVIDER 选一家的实现。加一家厂商 = 这里多一行 + 多一个文件。"""
import importlib

import config

_MODULES = {
    "deepseek": "clients.deepseek",
    "kimi": "clients.kimi",
}


def get(provider=None):
    p = provider or config.PROVIDER
    if p not in _MODULES:
        raise SystemExit(
            "provider={!r} 不认识。可选：{}".format(p, "、".join(sorted(_MODULES))))
    return importlib.import_module(_MODULES[p])
