"""聊天相关的业务逻辑：当前用假数据模拟模型流式输出。

以后接真模型时，只改这一层，路由层不用动。
"""

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import SessionLocal
from ..models import Conversation, Message
from ..schemas import ConversationCreate


async def fake_llm_stream() -> AsyncGenerator[str, None]:
    """模拟模型一块一块吐字（每个块停留 1 秒）。"""
    for piece in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(1)
        yield piece


def save_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
    """存一条消息。role 只能是 user / assistant。"""
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


async def event_stream(conversation_id: int, prompt: str) -> AsyncGenerator[str, None]:
    """流式输出，同时把这一轮的问答存进数据库。"""
    # 先存用户的提问
    db = SessionLocal()
    try:
        save_message(db, conversation_id, "user", prompt)

        pieces: list[str] = []
        async for piece in fake_llm_stream():
            pieces.append(piece)
            yield f"data: {piece}\n\n"
        save_message(db, conversation_id, "assistant", "".join(pieces))
        yield "event: done\ndata: [DONE]\n\n"
    finally:
        db.close()


def create_conversation(db: Session, payload: ConversationCreate) -> Conversation:
    """创建一个新的对话记录，title 可以不传，created_at 由数据库填"""
    conversation = Conversation(title=payload.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session) -> list[Conversation]:
    """查出所有对话，按 id 升序"""
    stmt = select(Conversation).order_by(Conversation.id.desc())
    return list(db.scalars(stmt).all())


def get_conversation_detail(db: Session, conversation_id: int) -> Conversation | None:
    """会话详情，连同它的全部消息一起查出来。查不到返回 None。"""
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    return db.scalars(stmt).first()
