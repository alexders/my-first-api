"""聊天相关的业务逻辑：当前用假数据模拟模型流式输出。

以后接真模型时，只改这一层，路由层不用动。
"""
from sqlalchemy import select
from sqlalchemy.orm import Session,selectinload

from ..models import Conversation
from ..schemas import ConversationCreate
import asyncio
from collections.abc import AsyncGenerator


async def fake_llm_stream() -> AsyncGenerator[str, None]:
    """模拟模型一块一块吐字（每个块停留 1 秒）。"""
    for piece in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(1)
        yield piece


async def event_stream() -> AsyncGenerator[str, None]:
    """把文本块包装成 SSE 格式，并在结束时补一个 done 事件。"""
    async for piece in fake_llm_stream():
        yield f"data: {piece}\n\n"
    yield "event: done\ndata: [DONE]\n\n"


def create_conversation(db:Session,payload:ConversationCreate) -> Conversation:
    """创建一个新的对话记录，title 可以不传，created_at 由数据库填"""
    conversation =Conversation(title=payload.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def list_conversations(db:Session) -> list[Conversation]:
    """查出所有对话，按 id 升序"""
    stmt =select(Conversation).order_by(Conversation.id.desc())
    return list(db.scalars(stmt).all())

def get_conversation_detail(db: Session, conversation_id: int) -> Conversation | None:
    """会话详情，连同它的全部消息一起查出来。查不到返回 None。"""
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    return db.scalars(stmt).first()