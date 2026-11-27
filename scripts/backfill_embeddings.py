"""给历史消息补算向量。只处理 embedding 为 NULL 的行，可重复执行。"""

import asyncio

from sqlalchemy import func, select

from my_first_api.db import SessionLocal
from my_first_api.models import Message
from my_first_api.services.embedding import embed_texts

BATCH = 10  # text-embedding-v3 单次请求上限


async def main() -> None:
    db = SessionLocal()
    try:
        stmt = select(Message).where(Message.embedding.is_(None)).order_by(Message.id)
        res = list(db.scalars(stmt).all())
        print(f"待补共{len(res)}条")
        if not res:
            return
        for start in range(0, len(res), BATCH):
            chunk = res[start : start + BATCH]
            vectors = await embed_texts([m.content for m in chunk])
            # zip组合到一起（msg,vec）
            for msg, vec in zip(chunk, vectors):
                if vec is not None:
                    msg.embedding = vec
            db.commit()

        print("补算结束")
    finally:
        # 结尾，print("补算结束") 之前
        remaining = db.scalar(
            select(func.count()).select_from(Message).where(Message.embedding.is_(None))
        )
        print(f"剩余未补算：{remaining} 条")
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
