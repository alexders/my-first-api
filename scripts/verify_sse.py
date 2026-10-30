import time

import httpx

T0 = time.perf_counter()
URL = "http://127.0.0.1:8000/chat/stream"


def main() -> None:
    with httpx.Client(timeout=30) as client:
        with client.stream("GET", URL) as resp:
            print(f"状态码: {resp.status_code}")
            print(f"content-type: {resp.headers.get('content-type')}")
            print()
            for raw in resp.iter_raw():
                elapsed = time.perf_counter() - T0
                print(f"{elapsed:5.2f}s  收到原始字节: {raw!r}")


if __name__ == "__main__":
    main()
