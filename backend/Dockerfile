# === dependency builder ===
FROM python:3.12-slim AS builder

# Pin uv — never use :latest in production
COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# === production runtime ===
FROM python:3.12-slim AS production

LABEL org.opencontainers.image.title="SPARC Backend" \
      org.opencontainers.image.description="Production Django/Daphne service"

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # PostgreSQL client lib — remove if not using psycopg2
        libpq5 \
        # PID 1 init: proper signal forwarding + zombie reaping
        tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built venv from builder — no build tools in the final image
COPY --from=builder /app/.venv /app/.venv

COPY . .

# Collect static + create dirs + create non-root user in as few layers as possible
RUN mkdir -p /app/staticfiles /app/media \
    && SECRET_KEY=build-only-not-a-real-secret python manage.py collectstatic --noinput \
    && groupadd --system django \
    && useradd --system --gid django --no-create-home django \
    && chown -R django:django /app

USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" \
    || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

# --proxy-headers: trust X-Forwarded-For/Proto from nginx
# --access-log -:  stream access logs to stdout for Docker log drivers
CMD ["daphne", \
     "--proxy-headers", \
     "--access-log", "-", \
     "-b", "0.0.0.0", \
     "-p", "8000", \
     "config.asgi:application"]


# === Development environment setup ===
FROM python:3.12-slim AS development

COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./

# Install ALL deps including dev tools
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
