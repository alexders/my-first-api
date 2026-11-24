"""接口的请求 / 响应契约（Pydantic 模型）。

这里只描述"进出接口的数据长什么样"，不涉及数据库。
数据库实体在 models.py，连接与会话在 db.py。
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ItemCreate(BaseModel):
    """POST /items/ 的请求体。

    不包含 id：新增时 id 由数据库自增生成，客户端无从提供。
    """

    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    cost: float


class ItemPublic(BaseModel):
    """对外返回的 Item。

    不含 tax / cost：成本价属于内部数据，不对外暴露。
    from_attributes 让 Pydantic 能从 SQLAlchemy 的 ORM 对象读取属性。
    """

    id: int
    name: str
    description: str | None = None
    price: float

    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """POST /customers/ 的请求体（当前只用于练请求体校验，尚未落库）。"""

    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


class ConversationCreate(BaseModel):
    """POST /conversations/ 的请求体。"""

    title: str | None = None


class ConversationPublic(BaseModel):
    """对外返回的 Conversation。"""

    id: int
    title: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessagePublic(BaseModel):
    """对外返回的 Message。"""

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationDetail(ConversationPublic):
    """对外返回的 Conversation 详情，包含消息列表。"""

    messages: list[MessagePublic] = []