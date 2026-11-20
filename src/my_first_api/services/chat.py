"""聊天相关的业务逻辑：当前用假数据模拟模型流式输出。

以后接真模型时，只改这一层，路由层不用动。
"""

import asyncio
from collections.abc import AsyncGenerator


async def fake_llm_stream() -> AsyncGenerator[str, None]:
    """模拟模型一块一块吐字（每个块停留 1 秒）。"""
    for piece in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(1)
        yield piece


async def event_stream() -> AsyncGenerator[str, None]:
    """把文本块包装成 SSE 格式，并在结束时补一个 done 事件。"""
    async for piece in fake_llm_stream():
        yield f"data: {piece}\n\n"
    yield "event: done\ndata: [DONE]\n\n"
