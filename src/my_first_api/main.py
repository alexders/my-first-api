import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette import status
from .config import get_settings
print(f"当前工作目录: {os.getcwd()}")
@asynccontextmanager
async def lifespan(app):
    print("应用跑起来了...")
    yield
    print("应用要关闭了...")
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={"code": "500", "message": str(exc), "path": request.url.path},
    )


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
    cost: float


class ItemPublic(BaseModel):
    name: str
    description: str | None = None
    price: float


@app.post("/items/", response_model=ItemPublic)
async def get_public_item(item: Item):
    return item


# 假的存储层：先用字典模拟数据库，C 阶段会换成 SQLAlchemy
FAKE_ITEMS: dict[int, Item] = {
    1: Item(
        name="笔记本", description="13 寸轻薄本", price=5999.0, tax=0.13, cost=4800.0
    ),
    2: Item(name="鼠标", description="无线静音", price=129.0, tax=0.13, cost=60.0),
}


@app.get("/items/{item_id}", response_model=ItemPublic)
async def get_item_id(item_id: int):
    if item_id not in FAKE_ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return FAKE_ITEMS[item_id]

@app.get("/config")
async def get_config():
    config = get_settings()
    return {
        "app_name": config.app_name,
        "debug": config.debug,
        "database_url": config.database_url,
    }