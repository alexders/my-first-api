from my_first_api.main import app
from fastapi.testclient import TestClient


client =TestClient(app)

def main() ->None:
   r= client.post("/items/",json={
  "name": "item1",
  "description": "这是一个测试商品",
  "price": 12.5,
  "tax": 1.2,
  "cost": 8.0
})
   print(r.status_code,r.json())

if __name__ =="__main__":
    main()