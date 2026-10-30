import asyncio
import time

T0 = time.perf_counter()


def log(msg: str) -> None:
    print(f"{time.perf_counter() - T0:5.2f}s  {msg}")


async def worker(name: str, seconds: float) -> None:
    log(f"{name} 开始")
    await asyncio.sleep(seconds)
    log(f"{name} 结束")


async def plain_await() -> None:
    log("--- 写法 1：纯 await 串行，队列里始终只有 1 个任务 ---")
    await worker("A", 1)
    await worker("B", 1)


async def await_but_precreated() -> None:
    log("--- 写法 2：还是 await，但先 create_task 把两个都塞进队列 ---")
    a = asyncio.create_task(worker("A", 1))
    b = asyncio.create_task(worker("B", 1))
    await a
    await b


async def main() -> None:
    await plain_await()
    await await_but_precreated()


if __name__ == "__main__":
    asyncio.run(main())
