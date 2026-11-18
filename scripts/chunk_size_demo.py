import asyncio
import time

T0 = time.perf_counter()


def log(msg: str) -> None:
    print(f"{time.perf_counter() - T0:5.2f}s  {msg}")


async def stream_by(chunks: list[str], delay: float):
    for c in chunks:
        await asyncio.sleep(delay)
        yield c


async def consume(chunks: list[str], label: str) -> None:
    log(f"--- {label} ---")
    buffer = ""
    async for piece in stream_by(chunks, 0.1):
        buffer += piece
        log(f"   收到 {piece!r}  →  已拼成 {buffer!r}")
    print()


async def main() -> None:
    text = "今天天气不错，适合出门"

    await consume(list(text), "逐字：每个块 = 1 个字")
    await consume(
        ["今天", "天气", "不错", "，", "适合", "出门"], "逐词：每个块 = 2 个字"
    )
    await consume([text], "整句：一次全给")


if __name__ == "__main__":
    asyncio.run(main())
