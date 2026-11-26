"""应用入口：只负责"装配"。

分工：
- config.py   配置
- db.py       连接与会话
- models.py   数据库实体
- schemas.py  接口契约
- services/   业务逻辑
- routers/    HTTP 路由

这里保留：app 创建、路由挂载、中间件、全局异常处理、lifespan、启动入口。
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .logging_config import setup_logging
from .routers import chat, customers, items, system, ai

logger = logging.getLogger(__name__)
settings = get_settings()
setup_logging(settings.log_level, "INFO" if settings.debug else "WARNING")
logger.info(f"当前工作目录: {os.getcwd()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用跑起来了...")
    yield
    logger.info("应用要关闭了...")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    cost_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        cost_ms,
    )
    return response


app.include_router(items.router)
app.include_router(chat.router)
app.include_router(customers.router)
app.include_router(system.router)
app.include_router(ai.router)

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
        content={"code": 500, "message": str(exc), "path": request.url.path},
    )


def run() -> None:
    import uvicorn

    uvicorn.run("my_first_api.main:app", host="127.0.0.1", port=8000, reload=True)
