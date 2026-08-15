# 15 - Roadmap toward the Andela-style architecture

The attached role reference emphasizes PostgreSQL service ownership, UUID logical references between services, Kafka/Avro propagation, dual operational/analytical event consumers, and Snowflake/dbt medallion analytics.

This local project deliberately implements the analytical pipeline first. Extend it in phases:

## Phase A - Current package

Python -> MinIO -> PostgreSQL raw -> dbt -> PostgreSQL marts -> Superset, orchestrated conceptually by Hop.

## Phase B - OLTP service boundaries

Add dedicated PostgreSQL databases for customer, menu, order, payment, and delivery domains. Use UUID logical references between services rather than cross-service physical foreign keys.

## Phase C - Transactional outbox

Write domain changes and outbox events in the same local ACID transaction. Add a publisher process.

## Phase D - Kafka / Redpanda + Avro

Publish versioned `order.created`, `payment.authorized`, and `delivery.status.changed` events. Add schema registry and event compatibility tests.

## Phase E - Dual consumers

One consumer materializes operational state/search needs; another lands analytics events into Bronze object storage. Add reconciliation between service data and events.

## Phase F - Snowflake

Replace/extend PostgreSQL marts with Snowflake Bronze/Silver/Gold and keep dbt as the modeling/testing layer.

This progression gives you a credible portfolio narrative: start with a working reproducible analytics pipeline, then evolve it toward event-driven, database-per-service architecture.
