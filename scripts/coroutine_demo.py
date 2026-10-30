import asyncio


async def worker(name: str) -> None:
    print(f"  → worker 的函数体真的执行了: {name}")


async def main() -> None:
    print("1) 调用 async def 函数，拿到什么？")
    c = worker("A")
    print(f"   type = {type(c)}")
    print(f"   asyncio.iscoroutine = {asyncio.iscoroutine(c)}")
    print("   （注意：到这里为止，worker 内部一个字都没打印）")
    print()

    print("2) 用 create_task 包装之后，变成什么？")
    task = asyncio.create_task(c)
    print(f"   type = {type(task)}")
    print(f"   isinstance Task = {isinstance(task, asyncio.Task)}")
    print("   （注意：仍然还没有打印）")
    print()

    print("3) await 它")
    await task
    print("   （这时候才打印上面那行，说明函数体是那一刻才开始跑的）")


if __name__ == "__main__":
    asyncio.run(main())
