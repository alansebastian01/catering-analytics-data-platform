# B2B Catering Analytics Platform — Complete Deployment & Operations Guide

This single guide consolidates the project’s deployment, validation, orchestration, data-quality, BI, operations, and troubleshooting instructions into one place.

It reflects the completed local implementation built with **Python, MinIO, PostgreSQL, dbt, Apache Hop, FastAPI, Apache Superset, Redis, Docker Compose, PowerShell, and DBeaver**.

> **Scope:** This is a production-style local reference implementation designed for Windows + Docker Desktop. It demonstrates production engineering patterns, but it is not a production deployment.

---

## 1. Architecture at a glance

```text
                         Apache Hop Web
                               |
                               | HTTP
                               v
                     FastAPI Pipeline Runner
                               |
                               v
                       src.run_pipeline
                               |
                               v
                  Clean Synthetic Generator
                               |
                               v
                         MinIO landing
                               |
                               v
                 Python validation / ingestion
                         /             \
                        /               \
                       v                 v
               PostgreSQL RAW      rejected rows
                 + audit           + MinIO quarantine
                       |
                       v
                 Reconciliation
                       |
                       v
                      dbt
                  staging -> marts
                       |
                       v
                  Apache Superset
                /                  \
               v                    v
       Executive Analytics   Product Analytics
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| Python | Source generation, validation, ingestion, reconciliation, end-to-end runner |
| MinIO | S3-compatible landing, curated, and quarantine storage |
| PostgreSQL | RAW, audit, staging, marts |
| dbt | Transformations, dimensional models, tests |
| Apache Hop | Visual orchestration and success/failure control |
| FastAPI | Internal execution boundary between Hop and the pipeline |
| Apache Superset | BI datasets, KPIs, charts, dashboards |
| Redis | Superset supporting cache service |
| Docker Compose | Service lifecycle, networking, health dependencies, volumes |
| DBeaver | PostgreSQL inspection and validation |

---

## 2. Repository layout

```text
.
├── compose.yaml
├── .env.example
├── .gitignore
├── README.md
│
├── src/
│   ├── common.py
│   ├── generate_and_land.py
│   ├── generate_and_land_bad_data.py
│   ├── load_minio_to_postgres.py
│   ├── reconcile.py
│   ├── run_pipeline.py
│   └── pipeline_runner_api.py
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── tests/
│
├── postgres/init/
├── minio/policies/
├── docker/
│   ├── minio/
│   ├── pipeline/
│   └── superset/
│
├── hop/
│   └── workflows/
│       └── catering_analytics_orchestration.hwf
│
├── diagrams/
├── scripts/windows/
├── docs/
├── logs/       # runtime, gitignored
└── backups/    # local output, gitignored
```

---

## 3. Windows prerequisites

Recommended environment:

- Windows 10/11
- Docker Desktop using WSL2
- Git
- VS Code
- PowerShell 7 preferred; Windows PowerShell also works
- DBeaver recommended
- 4 CPU cores minimum; 8 preferred
- 12 GB RAM minimum; 16 GB preferred
- at least 20 GB free disk space

Keep the project outside OneDrive or other sync folders when possible.

Example location:

```text
C:\github\catering_analytics_production_reference
```

### Validate Docker

```powershell
docker version
docker compose version
docker run --rm hello-world
```

If the Docker client works but the server does not, start Docker Desktop.

---

## 4. Clone and open the project

```powershell
cd C:\github
git clone <YOUR_REPOSITORY_URL> catering_analytics_production_reference
cd .\catering_analytics_production_reference
code .
```

Check Git:

```powershell
git status
```

Expected on a clean clone:

```text
nothing to commit, working tree clean
```

---

## 5. Create the local `.env`

The repository should contain `.env.example`, but not `.env`.

### Option A — supplied bootstrap script

```powershell
.\scripts\windows\bootstrap.ps1
```

If PowerShell blocks scripts for the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then rerun the bootstrap script.

### Option B — manual copy

```powershell
Copy-Item .env.example .env
```

Open it:

```powershell
code .env
```

Replace every placeholder credential.

Important variable groups include:

```text
POSTGRES_ADMIN_PASSWORD
INGEST_PASSWORD
DBT_PASSWORD
BI_READER_PASSWORD
MINIO_ROOT_PASSWORD
MINIO_PIPELINE_PASSWORD
SUPERSET_ADMIN_PASSWORD
SUPERSET_META_PASSWORD
SUPERSET_SECRET_KEY
```

### Generate a Superset secret key

Run in PowerShell:

```powershell
-join ((48..57)+(65..90)+(97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

Copy the generated value into:

```text
SUPERSET_SECRET_KEY=<generated-value>
```

### Normal source mode

For normal operation keep:

```text
BAD_RECORD_PERCENT=0
```

The project has a separate bad-data generator for explicit failure-path testing.

### Confirm `.env` is ignored

```powershell
git check-ignore .env
```

Expected:

```text
.env
```

Never commit `.env`.

---

## 6. Validate Compose before starting

```powershell
docker compose config > $null
```

Normal services:

```powershell
docker compose config --services
```

Tools profile:

```powershell
docker compose --profile tools config --services
```

The tools output should include the manual `pipeline` service.

Primary services are expected to include:

```text
postgres
minio
minio-init
pipeline
pipeline-runner
hop-web
superset-meta
redis
superset
```

`pipeline` appears when the `tools` profile is enabled.

---

## 7. Build the platform

```powershell
docker compose build
```

Build the tools image as well if required by your Compose version/workflow:

```powershell
docker compose --profile tools build pipeline
```

Useful targeted builds:

```powershell
docker compose build pipeline-runner
docker compose build superset
```

---

## 8. Start the platform

```powershell
docker compose up -d
```

Or use the supplied Windows script:

```powershell
.\scripts\windows\start.ps1
```

Check status:

```powershell
docker compose ps
```

Expected long-running services should show `Up`; health-enabled services should become `healthy`.

A healthy completed stack typically includes:

```text
postgres          healthy
minio             healthy
pipeline-runner   healthy
redis             healthy
superset-meta     healthy
superset          healthy
hop-web           running
```

`minio-init` is intentionally a one-shot container and should exit successfully.

Check it with:

```powershell
docker compose ps -a
```

Expected:

```text
minio-init   Exited (0)
```

---

## 9. Local service URLs

| Service | Local address |
|---|---|
| Apache Hop Web | `http://localhost:8080` |
| Apache Superset | `http://localhost:8088` |
| MinIO API | `http://localhost:9000` |
| MinIO Console | `http://localhost:9001` |
| PostgreSQL / DBeaver | `localhost:5432` |

The FastAPI `pipeline-runner` is intentionally internal to Docker and does not need a Windows host port.

---

## 10. Validate MinIO initialization

Check logs:

```powershell
docker compose logs minio-init
```

Expected behavior:

- MinIO alias configured
- `landing`, `curated`, and `quarantine` buckets created if missing
- anonymous access disabled
- pipeline user created or retained
- pipeline policy created/attached
- initializer exits code 0

The initialization is designed to be rerunnable/idempotent.

---

## 11. Validate the FastAPI pipeline runner

Check health from the tools container:

```powershell
docker compose --profile tools run --rm --no-deps pipeline python -c "import urllib.request; print(urllib.request.urlopen('http://pipeline-runner:8000/health').read().decode())"
```

Expected response resembles:

```json
{"status":"ok","timestamp":"..."}
```

Runner endpoints:

```text
GET  /health
POST /run
GET  /hop/run
```

---

## 12. Source generation modes

The project deliberately separates clean simulation from failure testing.

### Clean generator

```text
src/generate_and_land.py
```

Used by the normal pipeline and Hop orchestration.

Run only source generation:

```powershell
docker compose --profile tools run --rm pipeline python -m src.generate_and_land
```

It generates:

```text
customers
products
orders
order_items
payments
order.created events
```

Landing layout:

```text
landing/
  customers/ingest_date=YYYY-MM-DD/
  products/ingest_date=YYYY-MM-DD/
  orders/ingest_date=YYYY-MM-DD/
  order_items/ingest_date=YYYY-MM-DD/
  payments/ingest_date=YYYY-MM-DD/
  events/order_created/ingest_date=YYYY-MM-DD/
  _manifests/ingest_date=YYYY-MM-DD/
```

### Controlled bad-data generator

```text
src/generate_and_land_bad_data.py
```

Used only for data-quality testing.

Run:

```powershell
docker compose --profile tools run --rm pipeline python -m src.generate_and_land_bad_data
```

It deliberately introduces validation failures such as:

- unsupported customer segment
- negative product price
- invalid order status
- non-positive order-item quantity
- negative payment amount

This script is not part of the normal clean orchestration path.

---

## 13. Run the full clean pipeline

Recommended end-to-end command:

```powershell
docker compose --profile tools run --rm pipeline
```

Equivalent project stages are:

```text
generate clean batch
    -> land to MinIO
    -> load unseen objects to PostgreSQL RAW
    -> reconcile
    -> dbt build + tests
```

Expected final message:

```text
Pipeline completed successfully.
```

You can also use:

```powershell
.\scripts\windows\run-pipeline.ps1
```

where the script is present and aligned with the current Compose file.

---

## 14. Run individual pipeline stages

### Generate

```powershell
docker compose --profile tools run --rm pipeline python -m src.generate_and_land
```

### Ingest MinIO -> PostgreSQL

```powershell
docker compose --profile tools run --rm pipeline python -m src.load_minio_to_postgres
```

### Reconcile

```powershell
docker compose --profile tools run --rm pipeline python -m src.reconcile
```

### dbt build

```powershell
docker compose --profile tools run --rm pipeline dbt build --project-dir /app/dbt --profiles-dir /app/dbt
```

---

## 15. DBeaver connection

### Administrator/development connection

```text
Connection name: Catering Analytics - Admin
Host: localhost
Port: 5432
Database: analytics
Username: platform_admin
Password: <POSTGRES_ADMIN_PASSWORD>
```

### Read-only BI validation connection

```text
Connection name: Catering Analytics - BI Reader
Host: localhost
Port: 5432
Database: analytics
Username: bi_reader
Password: <BI_READER_PASSWORD>
```

Expected schemas:

```text
audit
raw
staging
marts
public
```

---

## 16. Validate ingestion in PostgreSQL

### Recent pipeline runs

```sql
SELECT *
FROM audit.pipeline_runs
ORDER BY started_at DESC
LIMIT 10;
```

### Ingested source objects

```sql
SELECT *
FROM audit.ingested_objects
ORDER BY loaded_at DESC
LIMIT 20;
```

If your current schema uses a slightly different timestamp column, inspect the table in DBeaver and use the actual column name.

### Rejected rows

```sql
SELECT *
FROM audit.rejected_rows
ORDER BY rejected_at DESC
LIMIT 20;
```

### RAW counts

```sql
SELECT COUNT(*) FROM raw.customers;
SELECT COUNT(*) FROM raw.products;
SELECT COUNT(*) FROM raw.orders;
SELECT COUNT(*) FROM raw.order_items;
SELECT COUNT(*) FROM raw.payments;
```

---

## 17. Validate idempotency

After a successful ingestion, rerun the loader without generating another batch:

```powershell
docker compose --profile tools run --rm pipeline python -m src.load_minio_to_postgres
```

Expected result:

```json
{
  "rows_loaded": 0,
  "objects_processed": 0,
  "rejected_rows": 0
}
```

This proves already processed MinIO object versions are skipped instead of duplicated.

Then generate a new clean batch and rerun ingestion to prove incremental loading.

---

## 18. Validate controlled bad-data handling

Run the bad-data generator:

```powershell
docker compose --profile tools run --rm pipeline python -m src.generate_and_land_bad_data
```

Then ingest normally:

```powershell
docker compose --profile tools run --rm pipeline python -m src.load_minio_to_postgres
```

Verify rejection counts:

```sql
SELECT
    entity_name,
    reason,
    COUNT(*) AS rejected_count
FROM audit.rejected_rows
GROUP BY entity_name, reason
ORDER BY entity_name, reason;
```

Open MinIO and inspect:

```text
quarantine/
```

A validated test of this project detected **505 intentionally invalid rows**.

### Confirm invalid records did not contaminate trusted RAW

```sql
SELECT COUNT(*)
FROM raw.orders
WHERE order_status NOT IN ('DELIVERED','CONFIRMED','CANCELLED');
```

```sql
SELECT COUNT(*)
FROM raw.order_items
WHERE quantity <= 0;
```

```sql
SELECT COUNT(*)
FROM raw.payments
WHERE payment_amount < 0;
```

Expected for a clean trusted RAW state:

```text
0
```

---

## 19. Reconciliation

Run:

```powershell
docker compose --profile tools run --rm pipeline python -m src.reconcile
```

Checks include:

```text
orders_vs_order_items_orphans
payments_vs_orders_orphans
negative_order_totals
order_item_amount_mismatch
```

Healthy output:

```json
{
  "orders_vs_order_items_orphans": 0,
  "payments_vs_orders_orphans": 0,
  "negative_order_totals": 0,
  "order_item_amount_mismatch": 0
}
```

The bad-data exercise demonstrated why reconciliation is needed in addition to row validation: independently valid child rows may become orphaned when a parent row is rejected.

---

## 20. dbt transformation and tests

Run:

```powershell
docker compose --profile tools run --rm pipeline dbt build --project-dir /app/dbt --profiles-dir /app/dbt
```

Current validated project shape:

```text
5 staging models
6 mart models
27 data tests
38 total operations
```

Validated clean result:

```text
PASS=38
WARN=0
ERROR=0
SKIP=0
TOTAL=38
```

Marts include:

```text
marts.dim_customer
marts.dim_product
marts.dim_payment
marts.dim_date
marts.fact_orders
marts.fact_order_items
```

Inspect:

```sql
SELECT COUNT(*) FROM marts.fact_orders;
SELECT COUNT(*) FROM marts.fact_order_items;
SELECT * FROM marts.fact_orders LIMIT 10;
```

---

## 21. Apache Hop orchestration

Open:

```text
http://localhost:8080
```

Workflow path inside Hop:

```text
/project/workflows/catering_analytics_orchestration.hwf
```

The repository bind mount maps:

```text
Windows: ./hop
Docker:  /project
```

Workflow logic:

```text
Start
  |
  v
Run Catering Analytics Pipeline
  |\
  | +---- failure ----> Failure
  |
  +------ success ----> Success
```

HTTP endpoint:

```text
http://pipeline-runner:8000/hop/run
```

Hop response target:

```text
/project/workflows/output/pipeline_runner_response.json
```

The output directory should remain gitignored.

Monitor runner logs:

```powershell
docker compose logs -f pipeline-runner
```

A successful Hop run should execute the clean generator, ingestion, reconciliation, and dbt build and end on the Success path.

---

## 22. Apache Superset connection

Open:

```text
http://localhost:8088
```

Create the PostgreSQL database connection with the read-only BI account.

Inside Docker use the Compose service name, not localhost:

```text
Host: postgres
Port: 5432
Database: analytics
Username: bi_reader
Password: <BI_READER_PASSWORD>
```

SQLAlchemy URI form:

```text
postgresql+psycopg2://bi_reader:<BI_READER_PASSWORD>@postgres:5432/analytics
```

Test and save the connection.

---

## 23. Superset virtual datasets

The completed project uses two virtual analytics datasets.

### Catering Order Analytics

Built from order facts with customer/payment context.

Supports:

```text
Total Revenue
Total Orders
Average Order Value
Unique Customers
Revenue Trend
Revenue by Customer Segment
Orders by Status
Payment Method Mix
```

### Catering Product Analytics

Built from order-item facts with product/customer context.

Supports:

```text
Top 10 Products by Revenue
Revenue by Product Category
Units Sold by Category
```

Use the `marts` layer as the source of trusted BI data. Avoid building production-facing dashboards directly from `raw`.

---

## 24. Dashboard validation

Validate important KPIs in DBeaver before presenting the dashboard.

Examples:

### Revenue

```sql
SELECT SUM(total_amount)
FROM marts.fact_orders;
```

### Orders

```sql
SELECT COUNT(DISTINCT order_id)
FROM marts.fact_orders;
```

### Average order value

```sql
SELECT AVG(total_amount)
FROM marts.fact_orders;
```

### Revenue trend

```sql
SELECT
    date_trunc('week', order_ts) AS week,
    SUM(total_amount) AS revenue
FROM marts.fact_orders
GROUP BY 1
ORDER BY 1;
```

Dashboard values change as new synthetic batches are generated, so point-in-time values are not permanent deployment acceptance criteria.

---

## 25. Normal daily workflow

Start:

```powershell
docker compose up -d
```

Check:

```powershell
docker compose ps
```

Run a new clean batch end to end:

```powershell
docker compose --profile tools run --rm pipeline
```

Or execute through Apache Hop.

Stop without deleting volumes:

```powershell
docker compose down
```

---

## 26. Logs

### All services

```powershell
docker compose logs --tail=100
```

### PostgreSQL

```powershell
docker compose logs -f postgres
```

### MinIO

```powershell
docker compose logs -f minio
```

### MinIO initializer

```powershell
docker compose logs minio-init
```

### Pipeline runner

```powershell
docker compose logs -f pipeline-runner
```

### Superset

```powershell
docker compose logs -f superset
```

### Hop

```powershell
docker compose logs -f hop-web
```

---

## 27. Backup

The supplied Windows backup script creates a PostgreSQL custom-format dump:

```powershell
.\scripts\windows\backup.ps1
```

Backups are written under:

```text
backups/
```

A complete production backup strategy would also include:

- MinIO/object storage
- Superset metadata
- secrets/encryption material where appropriate
- restore tests
- retention policies

Do not claim a backup is valid until a restore has been tested.

---

## 28. Stop vs reset

### Safe stop

```powershell
docker compose down
```

or:

```powershell
.\scripts\windows\stop.ps1
```

This preserves named volumes.

### Destructive reset

```powershell
.\scripts\windows\reset.ps1
```

The reset removes persistent Docker volumes after confirmation.

It can delete:

- PostgreSQL data
- MinIO objects
- Superset metadata
- Redis data
- Hop volume data

Avoid this unless a full rebuild is intentional.

Never casually run:

```powershell
docker compose down -v
```

on a state you want to preserve.

---

## 29. Troubleshooting

### PowerShell scripts are disabled

For the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then rerun the script.

### Compose environment variables appear blank

Confirm `.env` exists in the repository root:

```powershell
Get-Item .env
```

Then:

```powershell
docker compose config > $null
```

### Port already in use

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -in 5432,8080,8088,9000,9001
```

Change the corresponding host port in `.env` if needed.

### MinIO initializer fails

```powershell
docker compose logs minio-init
```

Confirm credentials are populated and the policy file exists.

### Superset does not start

```powershell
docker compose ps -a
docker compose logs --tail=150 superset
```

The custom Superset image must include the PostgreSQL driver required by the metadata and analytics connections.

### Pipeline runner is unhealthy

```powershell
docker compose logs --tail=150 pipeline-runner
```

Then test:

```powershell
docker compose --profile tools run --rm --no-deps pipeline python -c "import urllib.request; print(urllib.request.urlopen('http://pipeline-runner:8000/health').read().decode())"
```

### Hop HTTP action fails writing a file

Ensure the target is under the writable `/project` bind mount, for example:

```text
/project/workflows/output/pipeline_runner_response.json
```

Do not use unwritable Tomcat paths.

### dbt relationship tests fail

Run reconciliation and inspect RAW counts first. Relationship failures can indicate incomplete or inconsistent ingestion rather than a dbt defect.

### PostgreSQL init scripts were changed after first startup

Files under `postgres/init` are normally executed only when the PostgreSQL data volume is first initialized. Apply later schema changes manually/migrations, or reset only in a disposable environment.

---

## 30. Security and production-readiness

Already demonstrated locally:

- explicit container version pins
- ports bound to localhost where applicable
- separate PostgreSQL admin/ingest/dbt/BI roles
- non-root MinIO pipeline identity
- Superset separate metadata database
- read-only BI access
- persistent volumes
- health checks
- log rotation
- audit tables
- idempotent object ingestion
- quarantine handling

Before a real production deployment add:

- external secrets manager
- TLS everywhere
- SSO/OIDC/SAML where appropriate
- network segmentation
- managed/HA data services
- centralized logs, metrics, tracing, alerts
- CI/CD
- vulnerability scanning/SBOM/signing
- tested backups and restore drills
- resource limits and capacity management
- RPO/RTO planning
- data classification/retention/PII controls
- schema contracts and controlled evolution

---

## 31. Version policy

Do not replace pinned versions with `latest` simply because a newer image exists.

Upgrade one component at a time:

```text
1. Read release notes
2. Change one version pin
3. Rebuild
4. Start from a known state
5. Generate + ingest a clean batch
6. Test idempotency
7. Run reconciliation
8. Run dbt build
9. Validate Hop
10. Validate Superset
11. Commit only after all checks pass
```

This is more valuable than chasing newest versions without validation.

---

## 32. Deployment acceptance checklist

### Configuration

```text
[ ] .env created from .env.example
[ ] placeholder passwords replaced
[ ] Superset secret generated
[ ] BAD_RECORD_PERCENT=0 for normal operation
[ ] .env ignored by Git
```

### Infrastructure

```text
[ ] docker compose config passes
[ ] PostgreSQL healthy
[ ] MinIO healthy
[ ] minio-init exits 0
[ ] Redis healthy
[ ] Superset metadata DB healthy
[ ] Superset healthy
[ ] pipeline-runner healthy
[ ] Hop Web opens
```

### Data pipeline

```text
[ ] clean batch generated
[ ] landing files visible in MinIO
[ ] ingestion succeeds
[ ] audit.pipeline_runs populated
[ ] audit.ingested_objects populated
[ ] reconciliation all zero
[ ] dbt build passes
[ ] marts contain rows
```

### Reliability

```text
[ ] rerun with no new objects loads 0 rows
[ ] new batch processes incrementally
[ ] bad-data generator produces controlled invalid records
[ ] rejected rows visible in audit.rejected_rows
[ ] reject files visible in MinIO quarantine
```

### Orchestration

```text
[ ] pipeline-runner health endpoint returns ok
[ ] Hop workflow loads from /project/workflows
[ ] Hop success path works
[ ] Hop failure branch exists
[ ] runtime response output is gitignored
```

### BI

```text
[ ] Superset connects as bi_reader
[ ] Catering Order Analytics dataset created
[ ] Catering Product Analytics dataset created
[ ] Executive dashboard works
[ ] Product dashboard works
[ ] key KPIs validated against SQL
```

### Git / publishing

```text
[ ] .env is not tracked
[ ] dbt local user artifacts ignored
[ ] Hop runtime output ignored
[ ] architecture image committed
[ ] dashboard screenshots committed
[ ] README renders correctly on GitHub
[ ] git status clean
```

---

## 33. Validated project evidence

This completed reference implementation has demonstrated:

```text
Clean synthetic generation                PASS
Separate bad-data generation              PASS
Date-partitioned MinIO landing            PASS
Incremental ingestion                     PASS
Idempotent rerun (0 duplicate objects)    PASS
PostgreSQL RAW + audit                    PASS
Controlled rejected rows (505 test)       PASS
MinIO quarantine                          PASS
Cross-entity reconciliation               PASS
5 dbt staging models                      PASS
6 dbt mart models                         PASS
27 dbt data tests                         PASS
38/38 total dbt operations                PASS
FastAPI pipeline runner                   PASS
Apache Hop orchestration                  PASS
Success/failure workflow branching        PASS
Read-only Superset connection             PASS
Executive dashboard                       PASS
Product dashboard                         PASS
```

---

## 34. What this project demonstrates

This deployment is more than a file-transfer demo.

It can answer:

- Where did a warehouse record come from?
- Has this exact source object already been processed?
- Can ingestion be rerun safely?
- What happened to invalid records?
- Can bad records be investigated later?
- Are parent/child entities still coherent after validation?
- Did transformation rules pass automated tests?
- Can orchestration control success and failure paths?
- Can BI consume trusted marts without administrative database privileges?

The key patterns are:

```text
lineage
+ idempotency
+ incremental processing
+ validation
+ quarantine
+ reconciliation
+ dimensional modeling
+ automated testing
+ orchestration
+ least-privilege consumption
```

---

## 35. Production boundary

This stack is intentionally local and laptop-runnable.

A future production evolution may introduce:

```text
managed PostgreSQL
managed object storage
secrets manager
CI/CD
Infrastructure as Code
central observability
managed orchestration
database-per-service boundaries
Kafka / MSK
schema registry
Avro/event compatibility
CDC/Kafka Connect
Snowflake or another cloud warehouse
Kubernetes
```

Those are future deployment concerns, not requirements for this local reference to demonstrate the core data-engineering controls.

---

## 36. Final notes

- All business data is synthetic.
- No real customer, order, payment, or marketplace data is required.
- Do not commit local secrets.
- Keep the clean and bad-data generators separate.
- Validate with reconciliation and dbt before trusting BI output.
- Prefer safe stop/restart over destructive volume deletion.
- Treat a successful pipeline as **quality + integrity + transformation success**, not merely successful file movement.
