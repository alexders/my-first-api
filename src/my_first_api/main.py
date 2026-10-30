import asyncio

from fastapi import FastAPI

app = FastAPI()


@app.get("/getmessage")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/slow/{seconds}")
async def slow(seconds: float):
    await asyncio.sleep(seconds)
    return {"slept": seconds}


@app.get("/boom")
async def boom():
    raise RuntimeError("故意炸一个")
