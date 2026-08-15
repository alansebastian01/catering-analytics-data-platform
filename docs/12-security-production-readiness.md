# 12 - Security and production-readiness checklist

The package follows production patterns where practical on a laptop, but deliberately avoids pretending a local Compose stack is production.

## Already demonstrated

- Services are pinned to explicit versions rather than floating `latest` tags.
- Published service ports bind to `127.0.0.1` only.
- Pipeline uses a non-root MinIO identity.
- Ingestion, dbt, and BI have separate PostgreSQL roles.
- Superset uses a separate metadata database.
- BI uses a read-only PostgreSQL role.
- PostgreSQL records query statistics.
- Data volumes are persistent.
- Logs are size-rotated.
- Health checks and startup dependencies are defined.
- Pipeline runs have audit records.
- Object-level ingestion manifests make reruns idempotent.
- Invalid rows are quarantined rather than silently discarded.

## Required before a real production deployment

- Move passwords and keys to Vault/AWS Secrets Manager/Azure Key Vault/GCP Secret Manager.
- TLS everywhere; reverse proxy or ingress for Hop/Superset.
- SSO/OIDC/SAML and enterprise RBAC.
- Network segmentation; databases/object stores not publicly published.
- Managed HA database/object storage or multi-node architecture.
- Centralized logs/metrics/traces and alerts.
- Automated backups plus tested restore drills.
- Dependency/image vulnerability scanning and signed images/SBOMs.
- CI/CD with unit tests, dbt build, linting, security checks, and controlled promotion.
- Resource requests/limits and autoscaling where appropriate.
- Disaster recovery objectives: RPO/RTO.
- Data retention, classification, PII handling, encryption-at-rest key management.
- Schema contracts and change management.
- Runbooks and ownership/escalation policies.
