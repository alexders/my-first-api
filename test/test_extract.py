from my_first_api.schemas import ExpenseExtraction, ExpenseItem


def test_extract_ok(client, monkeypatch):
    """接口契约：把 service 的返回值正确转成 JSON。"""

    async def fake_extract(text: str) -> ExpenseExtraction:
        return ExpenseExtraction(
            items=[ExpenseItem(amount=38.0, category="交通", note="打车")]
        )

    monkeypatch.setattr(
        "my_first_api.routers.ai.ai_service.extract_expenses", fake_extract
    )

    r = client.post("/ai/extract", json={"text": "打车 38"})
    assert r.status_code == 200
    assert r.json()["items"][0]["category"] == "交通"
    assert r.json()["items"][0]["amount"] == 38.0


def test_extract_empty_text(client):
    """空文本在路由层就被拦掉，不会调模型。"""
    r = client.post("/ai/extract", json={"text": ""})
    assert r.status_code == 422


def test_extract_too_long(client):
    """超长文本同样被 Field(max_length=500) 拦住。"""
    r = client.post("/ai/extract", json={"text": "啊" * 501})
    assert r.status_code == 422


def test_extract_model_failure(client, monkeypatch):
    """模型输出不可解析时，翻译成 502 而不是 500。"""

    async def broken_extract(text: str):
        raise ValueError("模型输出无法解析")

    monkeypatch.setattr(
        "my_first_api.routers.ai.ai_service.extract_expenses", broken_extract
    )

    r = client.post("/ai/extract", json={"text": "随便说点什么"})
    assert r.status_code == 502
