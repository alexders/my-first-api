import time

import httpx

URL = "http://127.0.0.1:8000/slow/1"
N = 10


def main() -> None:
    start = time.perf_counter()
    with httpx.Client() as client:
        for _ in range(N):
            client.get(URL)
    print(f"同步串行 {N} 次: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
