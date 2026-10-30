import asyncio


def normal(x: int) -> int:
    return x * 2


async def async_fn(x: int) -> int:
    return x * 2


print("=== 1. 函数对象本身的类型（没调用的时候） ===")
print(f"type(normal)   = {type(normal)}")
print(f"type(async_fn) = {type(async_fn)}")
print()

print("=== 2. 调用之后的返回类型 ===")
r1 = normal(2)
print(f"normal(2)   -> 值 {r1!r}, 类型 {type(r1)}")

r2 = async_fn(2)
print(f"async_fn(2) -> 值 {r2!r}, 类型 {type(r2)}")
print()

print("=== 3. 怎么一眼判断谁是协程函数 ===")
print(f"asyncio.iscoroutinefunction(normal)   = {asyncio.iscoroutinefunction(normal)}")
print(f"asyncio.iscoroutinefunction(async_fn) = {asyncio.iscoroutinefunction(async_fn)}")
print()

print("=== 4. async_fn 要拿真结果，必须 await ===")
print(f"asyncio.run(async_fn(2)) = {asyncio.run(async_fn(2))}")
