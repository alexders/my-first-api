"""Item 相关的 HTTP 路由。

这一层只做三件事：
1. 声明路径、方法、状态码、response_model
2. 用 Depends 拿到 db 会话
3. 调用 service，必要时把 None 翻译成 404

不写 SQL，不写 commit。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..db import get_db
from ..schemas import ItemCreate, ItemPublic
from ..services import items as service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/list", response_model=list[ItemPublic])
def read_items(db: Session = Depends(get_db)):
    """列出所有 item。"""
    return service.list_items(db)


@router.get("/{item_id}", response_model=ItemPublic)
def read_line_item(item_id: int, db: Session = Depends(get_db)):
    """按 id 查一条，查不到返回 404。"""
    line_item = service.get_item(db, item_id)
    if line_item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return line_item


@router.post(
    "/add_item", response_model=ItemPublic, status_code=status.HTTP_201_CREATED
)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """新增一条 item。"""
    return service.add_item(db, item)
