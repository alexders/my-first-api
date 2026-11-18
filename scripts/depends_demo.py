from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient


def get_d() -> dict:
    return {"name": "张三", "age": 18}


app = FastAPI()


@app.get("/info")
async def get_dict(d: dict = Depends(get_d)) -> dict:
    return {**d, "city": "北京"}


@app.get("/info2")
async def get_dict2(d: Annotated[dict, Depends(get_d)]) -> dict:
    return {**d, "city": "北京2"}


def get_version():
    print("get_version()被调用")
    return "v1.0"


def get_config(version: str = Depends(get_version)) -> dict:
    print("get_config()被调用")
    return {"version": version, "config": "配置内容"}


@app.get("/config")
async def get_config_info(config: dict = Depends(get_config)) -> dict:
    return config


def yield_value():
    print("获取资源")
    resource = get_version()
    try:
        yield resource
    finally:
        print("yield_value()被调用,释放资源！")


@app.get("/yield")
async def get_yield_info(version: str = Depends(yield_value)):
    print("接口执行中")
    return {"version": version, "config": "配置内容"}


@app.get("/error_yield")
async def get_error_yield_info(version: str = Depends(yield_value)):
    data = version
    print("接口拿到值", data)
    if len(version) > 0:
        print("抛出异常", data)
        raise HTTPException(status_code=500, detail="模拟异常")


client = TestClient(app)
r = client.get("/info")
r2 = client.get("/info2")
r3 = client.get("/config")
r4 = client.get("/yield")
r5 = client.get("/error_yield")

print(r.status_code, r.json())
print(r2.status_code, r2.json())
print(r3.status_code, r3.json())
print(r4.status_code, r4.json())
print(r5.status_code, r5.json())
