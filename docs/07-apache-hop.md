# 07 - Apache Hop workflow guide

Apache Hop is the orchestration layer. dbt remains the SQL transformation engine.

Open Hop Web at `http://localhost:8080`.

## Workflow to build

Create a workflow named `catering_full_pipeline` with this logical control flow:

```text
START
  |
  v
Generate synthetic batch
  |
  v
Verify MinIO landing files
  |
  v
Load new objects -> PostgreSQL raw
  |
  v
Run reconciliation
  |
  v
Run dbt build
  |
  +---- failure ----> Log / notify failure ----> END FAILED
  |
  v
Log success
  |
  v
END SUCCESS
```

## Important container boundary

Do not assume the Hop Web container contains Python, dbt, or the Docker CLI. For a serious deployment, orchestration should call a dedicated execution service, Hop Server, Kubernetes job, CI runner, or another controlled runtime. The supplied local package therefore keeps the **fully executable pipeline command** in the `pipeline` container and uses Hop Web for workflow design/demonstration.

This is more accurate than mounting Python files into Hop and expecting a Java-focused Hop image to execute them automatically.

## Interview explanation

Say: “Hop owns sequencing, retries, dependencies, schedule, and failure paths. Python owns source generation/ingestion. dbt owns SQL transformations and data tests. PostgreSQL owns durable relational storage. Superset is a read-only consumer.”

## Scheduling

For a laptop, schedule the PowerShell wrapper with Windows Task Scheduler or use Hop scheduling once you have a dedicated Hop runtime. For production, use a persistent orchestrator runtime with credentials stored in a secret manager, not in the workflow file.
