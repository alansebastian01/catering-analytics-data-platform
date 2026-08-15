FROM python:3.12.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY docker/pipeline/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src /app/src
COPY dbt /app/dbt

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app
USER appuser

CMD ["python", "-m", "src.run_pipeline"]
