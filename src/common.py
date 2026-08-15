from __future__ import annotations

import logging
import os
from pathlib import Path

import boto3
from botocore.client import Config


def configure_logging() -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    Path("/app/logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("/app/logs/pipeline.log", encoding="utf-8"),
        ],
    )
    return logging.getLogger("catering_pipeline")


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
        region_name="us-east-1",
        config=Config(signature_version="s3v4", retries={"max_attempts": 5, "mode": "standard"}),
    )


def ingest_dsn() -> str:
    return os.environ["INGEST_DSN"]
