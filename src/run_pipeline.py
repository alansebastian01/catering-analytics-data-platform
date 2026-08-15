from __future__ import annotations

import subprocess
import sys

from .generate_and_land import main as generate
from .load_minio_to_postgres import main as ingest


def run(command: list[str]) -> None:
    print("\n>>>", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    batch_id = generate()
    ingest(batch_id=batch_id)
    run([sys.executable, "-m", "src.reconcile"])
    run(["dbt", "deps", "--project-dir", "/app/dbt", "--profiles-dir", "/app/dbt"])
    run(["dbt", "build", "--project-dir", "/app/dbt", "--profiles-dir", "/app/dbt"])
    print("\nPipeline completed successfully.", flush=True)


if __name__ == "__main__":
    main()
