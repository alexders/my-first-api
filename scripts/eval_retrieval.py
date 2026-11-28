"""检索评测：计算 Recall@K 和 MRR。看看检索的准不准"""

import asyncio

from my_first_api.db import SessionLocal
from my_first_api.llm import get_llm_client
from my_first_api.services.chat import retrieve_similar
from my_first_api.services.embedding import embed_text

CONVERSATION_ID = 1
K = 5
client = get_llm_client()
# expect 一律用"短、无标点、专有"的片段，避免因空格/标点差异误判
CASES = [
    # 简单题：作为对照
    {"q": "昨天午饭花了多少钱", "expect": "45块"},
    {"q": "RAG 是什么", "expect": "检索增强生成"},
    {"q": "LLM 是什么", "expect": "大语言模型"},
    # 难题：问题里不出现原文关键词，纯靠语义匹配
    {"q": "怎么让模型回答时引用我自己的资料", "expect": "检索增强生成"},
    {"q": "怎么减少大模型胡说八道", "expect": "检索增强生成"},
    {"q": "模型是怎么学会说话的", "expect": "海量文本训练"},
    {"q": "中午那顿饭花了多少钱", "expect": "45块"},
    {"q": "我想知道这个月伙食开销", "expect": "餐饮合计"},
]


async def main() -> None:
    db = SessionLocal()
    try:
        hits = 0
        rr_sum = 0.0
        for item in CASES:
            vec = await embed_text(item["q"], client)
            rows = retrieve_similar(db, vec, CONVERSATION_ID, K) if vec else []

            rank = None
            for i, msg in enumerate(rows, start=1):
                if item["expect"] in msg.content:
                    rank = i
                    break
            if rank:
                hits += 1
                rr_sum += 1 / rank
                print(f"命中 第{rank}位  {item['q']}")
            else:
                print(f"未命中        {item['q']}")
        total = len(CASES)
        print(f"\nRecall@{K}: {hits}/{total} = {hits / total:.0%}")
        print(f"MRR: {rr_sum / total:.2f}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
