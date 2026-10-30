import asyncio

import httpx

SLOW = "http://127.0.0.1:8000/slow/1"
BOOM = "http://127.0.0.1:8000/boom"
VERY_SLOW = "http://127.0.0.1:8000/slow/3"


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    resp.raise_for_status()  # 少了这行，500 不会抛异常
    return resp.status_code


async def noop() -> str:
    return "done"


async def main() -> None:
    # 0) 陷阱：async 函数调用后拿到的是什么
    coro = noop()
    print(f"[陷阱] noop() 返回的其实是 {type(coro).__name__}，不是结果本身")
    coro.close()  # 不 await 就要手动关掉，否则会有 RuntimeWarning

    async with httpx.AsyncClient() as client:
        # 1) 默认行为：httpx 拿到 500 也不抛异常
        resp = await client.get(BOOM)
        print(f"[默认] /boom 返回 {resp.status_code}，但 httpx 没有抛异常")

        # 2) 加上 raise_for_status 之后，单点失败才会变成异常
        urls = [SLOW] * 8 + [BOOM] * 2
        results = await asyncio.gather(
            *[fetch(client, u) for u in urls], return_exceptions=True
        )
        ok = [r for r in results if isinstance(r, int)]
        bad = [r for r in results if isinstance(r, Exception)]
        bad_type = type(bad[0]).__name__ if bad else "无"
        print(f"[容错] 成功 {len(ok)} 个，失败 {len(bad)} 个（{bad_type}）")

        # 3) 超时
        try:
            await asyncio.wait_for(fetch(client, VERY_SLOW), timeout=1)
        except TimeoutError:
            print("[超时] /slow/3 在 1 秒内没返回，已取消")


if __name__ == "__main__":
    asyncio.run(main())
