import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from .config import get_settings
from .db import Base, engine, get_db
from .models import Item
from .schemas import ItemCreate, ItemPublic

print(f"当前工作目录: {os.getcwd()}")


@asynccontextmanager
async def lifespan(app):
    print("应用跑起来了...")
    Base.metadata.create_all(bind=engine)
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


@app.get("/items/", response_model=list[ItemPublic])
async def read_items(db: Session = Depends(get_db)):
    return db.scalars(select(Item)).all()


@app.get("/items/{item_id}", response_model=ItemPublic)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return db_item


@app.post("/items/", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # 1. 用请求体造一个 ORM 对象（此时 id 还是空的）
    db_item = Item(**item.model_dump())
    # 2. 挂进会话
    db.add(db_item)
    # 3. 提交事务，真正写库
    db.commit()
    # 4. 回读，拿到数据库生成的自增 id
    db.refresh(db_item)
    # 5. 直接返回 ORM 对象，交给 response_model 裁剪
    return db_item


@app.get("/config")
async def get_config():
    config = get_settings()
    return {
        "app_name": config.app_name,
        "debug": config.debug,
        "database_url": config.database_url,
    }