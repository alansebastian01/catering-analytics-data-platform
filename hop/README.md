# Apache Hop orchestration

The core pipeline is intentionally runnable without Hop first. That makes debugging deterministic: prove each component, then place orchestration around it.

## Recommended production-style Hop workflow

Create `catering_full_pipeline.hwf` in Hop Web with these actions:

1. **Start**
2. **HTTP / Shell action: Generate & land** - trigger the same command used by the pipeline service.
3. **HTTP / Shell action: Ingest** - load only MinIO objects not already present in `audit.ingested_objects`.
4. **Shell action: Reconcile** - fail if source integrity checks are non-zero.
5. **Shell action: dbt build** - build + test staging/marts.
6. **Success / Failure logging** - write run status to an audit table or log file.
7. **End**.

For this laptop reference package, the simplest fully working execution command remains:

```powershell
docker compose --profile tools run --rm pipeline
```

Use Hop Web to design, version, and demonstrate the orchestration. For a real server deployment, run Hop Server/containers with an authenticated execution endpoint rather than exposing a development UI.

See `docs/07-apache-hop.md` for the exact workflow build procedure and trade-offs.
