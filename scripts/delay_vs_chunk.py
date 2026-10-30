import asyncio
import time


async def stream_by(chunks: list[str], delay: float):
    for c in chunks:
        await asyncio.sleep(delay)
        yield c


async def consume(chunks: list[str], delay: float, label: str) -> None:
    start = time.perf_counter()
    count = 0
    async for _ in stream_by(chunks, delay):
        count += 1
    duration = time.perf_counter() - start
    print(f"{label:<24} 收到 {count:>2} 块，耗时 {duration:.2f}s")


async def main() -> None:
    text = list("今天天气不错，适合出门")

    await consume(text, 0.2, "逐字 · delay=0.2")
    await consume(text, 0.05, "逐字 · delay=0.05")
    await consume(["今天天气不错，适合出门"], 0.2, "整句 · delay=0.2")


if __name__ == "__main__":
    asyncio.run(main())
