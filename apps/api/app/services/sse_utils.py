"""SSE 流式输出共享工具。"""

from __future__ import annotations

import json


def format_sse(event: str, payload: object) -> str:
    data = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return f"event: {event}\ndata: {data}\n\n"


class ClientDisconnected(Exception):
    pass


async def ensure_client_connected(request: object | None) -> None:
    if request is not None and hasattr(request, "is_disconnected") and await request.is_disconnected():
        raise ClientDisconnected()
