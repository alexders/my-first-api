from fastapi.testclient import TestClient


def test_list_empty(client: TestClient):
    r = client.get("/items/list")
    assert r.status_code == 200
    assert r.json() == []


def test_create_item(client: TestClient):
    payload = {"name": "键盘", "price": 99.0, "tax": 0.13, "cost": 60.0}
    r = client.post("items/add_item", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "键盘"
    assert data["id"] == 1


def test_read_item(client: TestClient):
    # 先创建一条，拿到真实 id
    created = client.post(
        "/items/add_item", json={"name": "键盘", "price": 99.0, "cost": 60.0}
    ).json()
    r = client.get(f"/items/{created['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "键盘"
    assert data["id"] == 1


def test_read_item_not_found(client: TestClient):
    r = client.get("/items/999")
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == "Item 999 not found"


def test_create_missing_field(client: TestClient):
    payload = {"name": "鼠标", "price": 50.0}
    r = client.post("/items/add_item", json=payload)
    assert r.status_code == 422


def test_list_after_create(client: TestClient):
    client.post("/items/add_item", json={"name": "A", "price": 1.0, "cost": 0.5})
    client.post("/items/add_item", json={"name": "B", "price": 2.0, "cost": 1.0})

    r = client.get("/items/list")

    assert r.status_code == 200
    assert len(r.json()) == 2
    assert [item["name"] for item in r.json()] == ["A", "B"]
