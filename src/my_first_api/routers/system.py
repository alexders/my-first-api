"""系统类接口：健康检查、慢请求、异常测试、配置查看。

这些接口没有业务模型，也没有数据库操作，所以不套 services 层。
"""

import asyncio

from fastapi import APIRouter

from ..config import get_settings

router = APIRouter(tags=["system"])


@router.get("/getmessage")
async def read_root():
    return {"message": "Hello, World!!"}


@router.get("/slow/{seconds}")
async def slow(seconds: float):
    """故意等待 N 秒，用来观察异步并发行为。"""
    await asyncio.sleep(seconds)
    return {"slept": seconds}


@router.get("/boom")
async def boom():
    """故意抛未捕获异常，用来验证全局异常处理器。"""
    raise RuntimeError("故意炸一个")


@router.get("/config")
async def read_config():
    """查看当前生效的配置（不含敏感信息）。"""
    config = get_settings()
    return {
        "app_name": config.app_name,
        "debug": config.debug,
        "database_url": config.database_url,
    }
