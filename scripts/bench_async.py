import asyncio
import time

import httpx

URL = "http://127.0.0.1:8000/slow/1"
N = 10


async def one(client: httpx.AsyncClient) -> int:
    resp = await client.get(URL)
    return resp.status_code


async def main() -> None:
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[one(client) for _ in range(N)])
    print(f"异步并发 {N} 次: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
