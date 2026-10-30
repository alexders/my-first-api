import asyncio
import time

T0 = time.perf_counter()


def log(msg: str) -> None:
    print(f"{time.perf_counter() - T0:5.2f}s  {msg}")


async def countdown(n: int):
    """异步生成器：每隔 0.2 秒才吐出一个值"""
    for i in range(n, 0, -1):
        await asyncio.sleep(0.2)
        yield i


async def main() -> None:
    log("开始消费")

    async for value in countdown(3):
        log(f"收到 {value}")

    log("消费结束")


if __name__ == "__main__":
    asyncio.run(main())
