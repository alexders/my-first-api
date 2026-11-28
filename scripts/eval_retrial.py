"""检索评测：对比不同 K 值的 Recall 和 MRR。"""

import asyncio

from my_first_api.db import SessionLocal
from my_first_api.llm import get_llm_client
from my_first_api.services.chat import retrieve_similar
from my_first_api.services.embedding import embed_text

CONVERSATION_ID = 1
K_VALUES = [1, 2, 3, 5, 8]
client = get_llm_client()
CASES = [
    {"q": "昨天午饭花了多少钱", "expect": "45块"},
    {"q": "RAG 是什么", "expect": "检索增强生成"},
    {"q": "LLM 是什么", "expect": "大语言模型"},
    {"q": "怎么让模型回答时引用我自己的资料", "expect": "检索增强生成"},
    {"q": "怎么减少大模型胡说八道", "expect": "检索增强生成"},
    {"q": "模型是怎么学会说话的", "expect": "海量文本训练"},
    {"q": "中午那顿饭花了多少钱", "expect": "45块"},
    {"q": "我想知道这个月伙食开销", "expect": "餐饮合计"},
]


async def main() -> None:
    db = SessionLocal()
    try:
        # 先把所有问题的向量算好，避免每个 K 都重复调 API
        vectors = []
        for case in CASES:
            vectors.append(await embed_text(case["q"], client))

        total = len(CASES)
        print(f"{'K':>3} | {'Recall':>12} | {'MRR':>6}")
        print("-" * 30)

        for k in K_VALUES:
            hits = 0
            rr_sum = 0.0
            for case, vec in zip(CASES, vectors):
                rows = retrieve_similar(db, vec, CONVERSATION_ID, k) if vec else []
                rank = None
                for i, msg in enumerate(rows, start=1):
                    if case["expect"] in msg.content:
                        rank = i
                        break
                if rank:
                    hits += 1
                    rr_sum += 1 / rank

            print(
                f"{k:>3} | {hits}/{total} {hits / total:>6.0%} | {rr_sum / total:>6.2f}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
