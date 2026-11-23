"""pytest 全局配置：为测试提供独立的内存数据库和 TestClient。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from my_first_api.db import Base, get_db
from my_first_api.main import app

# 必须用内存库 "sqlite://"，不能复用生产库的 URL，
# 否则 create_all / drop_all 会作用到 app.db 上。
# StaticPool 保证所有会话共用同一个内存库。
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, expire_on_commit=False
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 用测试库替换生产库
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    """为测试提供独立的 TestClient。"""
    Base.metadata.create_all(bind=test_engine)
    try:
        yield TestClient(app)  # 不加 with，不触发 lifespan
    finally:
        Base.metadata.drop_all(bind=test_engine)
