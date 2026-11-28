"""聊天相关的业务逻辑：当前用假数据模拟模型流式输出。

以后接真模型时，只改这一层，路由层不用动。
"""

import logging
import time
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..db import SessionLocal
from ..llm import get_llm_client
from ..models import Conversation, Message, RequestLog
from ..schemas import ConversationCreate
from .embedding import embed_text

logger = logging.getLogger(__name__)
settings = get_settings()
SYSTEM_PROMPT = "你是一个简洁的中文助手，回答控制在 100 字以内。"


def load_history(db: Session, conversation_id: int, limit: int = 20) -> list[dict]:
    """取最近 limit 条消息，按时间正序，转成 API 需要的格式。"""
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    rows = list(db.scalars(stmt).all())
    rows.reverse()
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *({"role": m.role, "content": m.content} for m in rows),
    ]


async def llm_stream(
    messages: list[dict],
    client: AsyncOpenAI | None = None,
    usage_holder: dict | None = None,
) -> AsyncGenerator[str, None]:
    """调用模型，逐块吐出增量文本。传入 usage_holder 可回填 token 用量"""
    client = client or get_llm_client()
    stream = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.7,
        max_tokens=800,
        stream=True,
        stream_options={"include_usage": True},
    )
    # 先取 usage，再判断 choices —— 顺序不能反
    async for chunk in stream:
        if chunk.usage and usage_holder is not None:
            usage_holder["usage"] = chunk.usage
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    embedding: list[float] | None = None,
) -> Message:
    """存一条消息。role 只能是 user / assistant。"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        embedding=embedding,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


async def event_stream(
    conversation_id: int, prompt: str, client: AsyncOpenAI | None = None
) -> AsyncGenerator[str, None]:
    """流式输出，同时把这一轮的问答存进数据库。"""
    client = client or get_llm_client()
    db = SessionLocal()
    try:
        # ── 阶段 1：准备上下文（失败就无法开口）──
        try:
            prompt_vec = await embed_text(prompt, client)
            # 先检索（此时当前消息还没入库，不会检索到自己）
            hits = (
                retrieve_similar(db, prompt_vec, conversation_id, 5)
                if prompt_vec
                else []
            )
            save_message(db, conversation_id, "user", prompt, prompt_vec)
            history = load_history(db, conversation_id, 10)
        except Exception:
            logger.exception("准备对话上下文失败")
            db.rollback()
            yield "event: error\ndata: 服务准备失败，请重试\n\n"
            return

        if hits:
            context = "\n".join(f"- {m.content}" for m in hits)
            history[0]["content"] += f"\n\n可能相关的历史记录：\n{context}"
            logger.info("检索到 %d 条：%s", len(hits), [m.id for m in hits])
            # logger.info(f"拼接的prompt{history[0]['content']}")

        # ── 阶段 2：流式生成 ──
        pieces: list[str] = []
        usage_holder: dict = {}
        started = time.perf_counter()
        first_token_at: float | None = None
        try:
            async for piece in llm_stream(history, client, usage_holder):
                if first_token_at is None:
                    first_token_at = time.perf_counter()
                pieces.append(piece)
                # 模型回答里一旦有换行（列表、分段），SSE 会被拆成多个事件，前端拼接就乱了
                yield f"data: {piece.replace(chr(10), ' ')}\n\n"
        except Exception:
            logger.exception("调用模型失败")
            yield "event: error\ndata: 模型调用失败\n\n"
            return
        total_ms = (time.perf_counter() - started) * 1000
        ttft_ms = (first_token_at - started) * 1000 if first_token_at else None

        usage = usage_holder.get("usage")
        if usage:
            logger.info(
                "会话 %s 首字 %.0fms / 总耗时 %.0fms / 输入 %d / 输出 %d token",
                conversation_id,
                ttft_ms or 0,
                total_ms,
                usage.prompt_tokens,
                usage.completion_tokens,
            )
        # ── 阶段 3：落库 ──
        reply = "".join(pieces)
        try:
            reply_vec = await embed_text(reply, client)
            save_message(db, conversation_id, "assistant", reply, reply_vec)
        except Exception:
            logger.exception("保存回复失败")
            db.rollback()
            yield "event: error\ndata: 回答已生成但保存失败\n\n"
            return
        # ── 阶段 4：记录指标 ──
        try:
            db.add(
                RequestLog(
                    conversation_id=conversation_id,
                    prompt_token=usage.prompt_tokens if usage else 0,
                    completion_token=usage.completion_tokens if usage else 0,
                    ttft_ms=round(ttft_ms) if ttft_ms is not None else None,
                    total_ms=round(total_ms),
                )
            )
            db.commit()
        except Exception:
            logger.exception("记录请求指标失败")
            db.rollback()

        logger.info("会话 %s 完成一轮问答，%d 字", conversation_id, len(reply))
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


def retrieve_similar(
    db: Session, query_vec: list[float], conversation_id: int, k: int = 5
) -> list[Message]:
    """在当前会话里找和 query_vec 最相近的 k 条消息（Top-K）。"""
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.embedding.is_not(None))
        .order_by(Message.embedding.cosine_distance(query_vec))
        .limit(k)
    )
    return list(db.scalars(stmt).all())
