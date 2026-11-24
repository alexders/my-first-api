FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir -i https://mirrors.cloud.tencent.com/pypi/simple uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY README.md ./
COPY src ./src
COPY static ./static
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-sync", "uvicorn", "my_first_api.main:app", "--host", "0.0.0.0", "--port", "8000"]