import asyncio
import time

T0 = time.perf_counter()


def log(msg: str) -> None:
    print(f"{time.perf_counter() - T0:5.2f}s  {msg}")


async def fake_llm_stream():
    """模拟模型一个字一个字往外吐"""
    for word in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(0.2)
        yield word


async def event_stream():
    """这就是 SSE 的产出侧：把上游的每个词包成一条 SSE 消息"""
    async for chunk in fake_llm_stream():
        yield f"data: {chunk}\n\n"


async def consumer():
    """模拟 StreamingResponse 干的事：拿到一块就立刻写出去"""
    agen = event_stream()
    log(f"event_stream() 返回的类型：{type(agen)}")

    async for sse in agen:
        log(f"推给浏览器：{sse.strip()}")


async def main() -> None:
    log("请求开始")
    await consumer()
    log("请求结束")


if __name__ == "__main__":
    asyncio.run(main())
