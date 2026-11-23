from fastapi.testclient import TestClient

from my_first_api.main import app

client = TestClient(app)


def main() -> None:
    r = client.post(
        "/items/",
        json={
            "name": "item1",
            "description": "这是一个测试商品",
            "price": 12.5,
            "tax": 1.2,
            "cost": 8.0,
        },
    )
    print(r.status_code, r.json())


item_res = client.get("/items/999")
print(item_res.status_code, item_res.json())

boom_res = client.get("/boom")
print(boom_res.status_code, boom_res.json())

cor_res = client.get("/items/1", headers={"Origin": "http://localhost:8889"})
print(cor_res.status_code, cor_res.json())

config_res = client.get("/config")
print(config_res.status_code, config_res.json())

if __name__ == "__main__":
    main()
