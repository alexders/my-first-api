"""AI 抽取接口的契约测试：用假客户端替换真模型，不花 token、不依赖网络。"""

from types import SimpleNamespace

import pytest

from my_first_api.llm import get_llm_client
from my_first_api.main import app


def make_stub_client(content: str) -> SimpleNamespace:
    """构造一个假的 AsyncOpenAI：create() 直接返回固定内容。"""

    class _Completions:
        async def create(self, **kwargs):
            message = SimpleNamespace(content=content)
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    return SimpleNamespace(chat=SimpleNamespace(completions=_Completions()))


@pytest.fixture()
def override_llm():
    """替换 LLM 客户端依赖，测试结束后只清理这一项，不影响 get_db 的替换。"""

    def _override(content: str) -> None:
        app.dependency_overrides[get_llm_client] = lambda: make_stub_client(content)

    yield _override
    app.dependency_overrides.pop(get_llm_client, None)


def test_extract_ok(client, override_llm):
    override_llm('{"items": [{"amount": 38, "category": "交通", "note": "打车"}]}')

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


def test_extract_invalid_output(client, override_llm):
    """模型两次都不守约 → 校验失败 → 路由翻译成 502。"""
    override_llm("这不是 JSON")

    r = client.post("/ai/extract", json={"text": "随便说点什么"})
    assert r.status_code == 502
