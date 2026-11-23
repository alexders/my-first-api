
from fastapi.testclient import TestClient
def test_list_empty(client: TestClient):
    r = client.get("/items/list")
    assert r.status_code == 200
    assert r.json() == []