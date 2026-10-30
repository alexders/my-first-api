import asyncio
import threading
import time

T0 = time.perf_counter()


def log(msg: str) -> None:
    elapsed = time.perf_counter() - T0
    print(f"{elapsed:5.2f}s  [线程 {threading.get_ident()}]  {msg}")


async def worker(name: str, seconds: float) -> None:
    log(f"{name} 开始")
    await asyncio.sleep(seconds)
    log(f"{name} 结束")


async def sequential() -> None:
    log("=== 写法 A：直接 await，一个一个来 ===")
    await worker("A", 1)
    await worker("B", 1)


async def concurrent() -> None:
    log("=== 写法 B：gather 包成 Task，同时来 ===")
    await asyncio.gather(
        worker("A", 1),
        worker("B", 1),
        worker("C", 1),
    )


async def main() -> None:
    await sequential()
    await concurrent()


if __name__ == "__main__":
    asyncio.run(main())
