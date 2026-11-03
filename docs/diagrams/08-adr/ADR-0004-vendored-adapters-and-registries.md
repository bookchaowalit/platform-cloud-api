# ADR-0004 — Vendor provider adapters and registries into the repo

- Status: accepted (retro-documented)
- Date: 2026-10-11 (commit `438ba09`)

## Context

เดิม service อยู่ใน solo-empire `services/cloud-api` และ resolve adapters จาก `SOLO_EMPIRE_ROOT` (`899a205`) ต้องการให้ repo รันได้เดี่ยวๆ

## Decision

- Copy adapters จาก solo-empire `infra/scripts/{platform,utils}` มาไว้ `adapters/` และ registries มาไว้ `registry/`; `server.py` ใส่ `adapters/` ใน `sys.path`
- `SOLO_ACCOUNTS_ROOT` (checkout ของ `bookchaowalit/platform-accounts-api`) เป็น optional สำหรับ account metadata
- Tasks / decisions เป็น API clients (`task_store.py`, `decision_store.py`); SQLite backends retired และเหลือเป็น test double (`tests/support/`)

## Consequences

- Adapters อาจ drift จากต้นฉบับ (product card §6, §8 "sync check")

## Evidence

`README.md` (standalone note), `server.py` (`ADAPTERS_ROOT`), commits `899a205`, `438ba09`, `adapters/cloud_usage.py` (`ACCOUNTS_REPO`), `tests/support/legacy_decision_tables.sql`, `DOCPACK/00-product-card.md`
