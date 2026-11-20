"""聊天相关的路由：SSE 流式输出。"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..services import chat as service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/stream")
async def chat_stream():
    """以 SSE 形式逐块推送文本，前端用 EventSource 消费。"""
    return StreamingResponse(
        service.event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
