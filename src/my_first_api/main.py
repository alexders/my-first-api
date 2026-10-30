import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/getmessage")
async def read_root():
    return {"message": "Hello, World!!"}


@app.get("/slow/{seconds}")
async def slow(seconds: float):
    await asyncio.sleep(seconds)
    return {"slept": seconds}


@app.get("/boom")
async def boom():
    raise RuntimeError("故意炸一个")


async def fake_llm_stream():
    """模拟模型一块一块吐字（每个块停留 1秒）"""
    for piece in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(1)
        yield piece


async def event_stream():
    async for piece in fake_llm_stream():
        yield f"data: {piece}\n\n"
    yield "event: done\ndata: [DONE]\n\n"


@app.get("/chat/stream")
async def chat_stream():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
