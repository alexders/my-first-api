import asyncio
import time

import httpx

URL = "https://httpbin.org/delay/1"
N = 10


def sync_fetch(url: str) -> int:
    resp = httpx.get(url)
    return resp.status_code


async def async_fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code


def main() -> None:
    start = time.perf_counter()
    print(f"start: {start}")
    for i in range(N):
        code = sync_fetch(URL)
        print(f"code : {code}")
    end = time.perf_counter()
    print(f"end: {end}")
    print(f"同步串行 {i + 1} 次: {end - start:.2f}s")


async def async_main() -> None:
    start = time.perf_counter()
    print(f"start: {start}")

    async with httpx.AsyncClient() as client:
        tasks = [async_fetch(client, URL) for _ in range(N)]
        await asyncio.gather(*tasks)

    end = time.perf_counter()
    print(f"end: {end}")
    print(f"异步并行 {N} 次: {end - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(async_main())
