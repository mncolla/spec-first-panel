FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
