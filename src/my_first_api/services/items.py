"""Item 的业务逻辑：只负责和数据库打交道，不感知 HTTP。

约定：
- 入参是 db 会话和纯数据，不出现在 FastAPI 的 Request / Response
- 查不到就返回 None，不抛 HTTPException（由路由层翻译成 404）
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Item
from ..schemas import ItemCreate


def list_items(db: Session) -> list[Item]:
    """查出所有 item，按 id 升序。"""
    return list(db.scalars(select(Item).order_by(Item.id)).all())


def get_item(db: Session, item_id: int) -> Item | None:
    """根据 id 查 item，查不到返回 None"""
    return db.get(Item, item_id)


def add_item(db: Session, item: ItemCreate):
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
