FROM ghcr.io/astral-sh/uv:0.12.17 AS uv
FROM python:3.13-slim-bookworm
COPY --from=uv /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-group notebook
COPY *.py ./
RUN useradd --create-home --uid 10001 agent && chown agent:agent /app
USER agent
EXPOSE 8000
CMD ["/app/.venv/bin/python", "main.py", "--serve", "--host", "0.0.0.0", "--port", "8000"]
