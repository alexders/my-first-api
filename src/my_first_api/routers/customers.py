"""顾客相关的路由。

目前只做请求体校验的练习，没有落库，所以没有对应的 models / services。
"""

from fastapi import APIRouter
from starlette import status

from ..schemas import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer(customer: Customer) -> Customer:
    """原样返回提交的顾客信息（演示用）。"""
    return customer
