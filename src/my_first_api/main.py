import asyncio
import os
from typing import Annotated

from fastapi import FastAPI, Query, responses
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette import status

print(f"当前工作目录: {os.getcwd()}")
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




class Customer(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.post("/customers/", status_code=status.HTTP_201_CREATED)
async def create_customer(customer: Customer) -> Customer:
    return customer

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    cost:float

class ItemPublic(BaseModel):
    name: str
    description: str | None = None
    price: float



@app.post("/items/",response_model=ItemPublic)
async def get_public_item(item:Item):
    return item

