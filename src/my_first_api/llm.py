"""LLM 客户端：全局单例，供服务层与依赖注入共用。

惰性创建：只有真正调用模型时才校验 key，
避免在没有 .env 的环境（如 CI）中导入即失败。
"""

from functools import lru_cache

from openai import AsyncOpenAI

from .config import get_settings


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    """返回共享的 AsyncOpenAI 实例。测试里可用 dependency_overrides 替换。

    构造阶段不校验凭据：没有 key 时用占位符，
    真正的失败留给实际调用（返回 401），
    这样没有 key 的环境（CI、只测参数校验）也能正常解析依赖。
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.llm_api_key or "missing-api-key",
        base_url=settings.llm_base_url,
        timeout=60,
    )
