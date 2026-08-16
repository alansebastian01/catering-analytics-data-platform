from __future__ import annotations

import subprocess
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Catering Analytics Pipeline Runner",
    version="1.1.0",
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def execute_pipeline() -> dict:
    run_id = str(uuid.uuid4())

    command = [
        "python",
        "-m",
        "src.run_pipeline",
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "run_id": run_id,
                "status": "FAILED",
                "stdout": process.stdout[-5000:],
                "stderr": process.stderr[-5000:],
            },
        )

    return {
        "run_id": run_id,
        "status": "SUCCESS",
        "stdout": process.stdout[-5000:],
    }


@app.post("/run")
def run_pipeline_post() -> dict:
    return execute_pipeline()


@app.get("/hop/run")
def run_pipeline_from_hop() -> dict:
    return execute_pipeline()