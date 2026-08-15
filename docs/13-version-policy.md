# 13 - Version policy (August 2026 reference)

The package intentionally pins stable releases rather than using floating `latest` tags.

| Component | Pin used | Rationale |
|---|---|---|
| PostgreSQL | 18.4 | Current stable PostgreSQL 18 maintenance line; PostgreSQL 19 is still beta in August 2026. |
| Apache Hop | 2.18.1 | June 2026 patch release after 2.18.0. |
| Apache Superset | 6.1.0 | Current stable release published May 2026. |
| dbt Core | 1.12.0 | Stable Python dbt release published July 2026; dbt Core 2.0 remains alpha at this time. |
| dbt-postgres | 1.11.0 | Current production/stable PostgreSQL adapter release published July 2026. |
| MinIO | RELEASE.2025-10-15T17-29-55Z | Security-fixed source release; the project builds the server image locally from this pinned source tag because prebuilt community distribution changed. |
| MinIO Client | RELEASE.2025-08-13T08-35-41Z | Pinned legacy client release for local initialization. |

## Important MinIO note

The MinIO open-source repository was archived in April 2026 and its community distribution is now source-only. This package builds a pinned MinIO server image from the security-fixed source tag because your stated learning architecture specifically uses MinIO and because the community prebuilt distribution changed. For actual production, choose a currently supported S3-compatible object store/service or build/use the supported MinIO distribution according to current vendor guidance.

## Upgrade rule

Never blindly replace a version pin in a working portfolio project. Read release notes, update one component at a time, rebuild from a clean environment, run the pipeline twice, run dbt tests/reconciliation, validate the dashboard, and only then commit the version change.
