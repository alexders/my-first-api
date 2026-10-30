import asyncio


def parse_sse(buffer: str):
    """模拟浏览器 EventSource 的解析规则：
    只有遇到空行，才算一条消息结束。返回 (解析出的事件, 剩余缓冲)"""
    events = []
    while "\n\n" in buffer:
        raw, buffer = buffer.split("\n\n", 1)
        data = "\n".join(
            line[len("data: ") :]
            for line in raw.split("\n")
            if line.startswith("data: ")
        )
        events.append(data)
    return events, buffer


async def fake_llm_stream():
    for word in ["今天", "天气", "不错", "，", "适合", "出门"]:
        await asyncio.sleep(0.1)
        yield word


async def event_stream(separator: str):
    async for chunk in fake_llm_stream():
        yield f"data: {chunk}{separator}"


async def consume(separator: str, label: str) -> None:
    buffer = ""
    received = []
    async for sse in event_stream(separator):
        buffer += sse
        new_events, buffer = parse_sse(buffer)
        received.extend(new_events)

    print(f"{label}")
    print(f"    解析器收到 {len(received)} 条消息: {received}")
    if buffer:
        print(f"    卡在缓冲区里、永远发不出去的内容: {buffer!r}")
    print()


async def main() -> None:
    await consume("\n\n", "SSE 正确写法：用两个换行分隔")
    # await consume("\n", "你改的写法：用一个换行")


if __name__ == "__main__":
    asyncio.run(main())
