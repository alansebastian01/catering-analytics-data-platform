SET ROLE ingest_user;

SET search_path = audit, public;

CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id UUID PRIMARY KEY,
    batch_id TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('RUNNING','SUCCESS','FAILED')),
    rows_loaded BIGINT NOT NULL DEFAULT 0,
    objects_processed INTEGER NOT NULL DEFAULT 0,
    message TEXT
);

CREATE TABLE IF NOT EXISTS audit.ingested_objects (
    bucket_name TEXT NOT NULL,
    object_key TEXT NOT NULL,
    etag TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    row_count BIGINT NOT NULL DEFAULT 0,
    run_id UUID REFERENCES audit.pipeline_runs(run_id),
    PRIMARY KEY (bucket_name, object_key, etag)
);

CREATE TABLE IF NOT EXISTS audit.rejected_rows (
    reject_id BIGSERIAL PRIMARY KEY,
    run_id UUID REFERENCES audit.pipeline_runs(run_id),
    entity_name TEXT NOT NULL,
    source_object TEXT NOT NULL,
    row_number BIGINT,
    raw_record JSONB,
    reason TEXT NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_pipeline_runs_started_at ON audit.pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS ix_ingested_objects_loaded_at ON audit.ingested_objects(loaded_at DESC);
CREATE INDEX IF NOT EXISTS ix_rejected_rows_rejected_at ON audit.rejected_rows(rejected_at DESC);
