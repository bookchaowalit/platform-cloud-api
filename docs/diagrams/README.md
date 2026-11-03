# Core 22 SDLC diagram pack — platform-cloud-api

ชุด diagram 22 รายการตาม SDLC Diagram Catalog v2 (knowledge-base `knowledge/tech/core-cs/sdlc-diagram-catalog.md`) วาดจาก code / config ของ repo นี้ที่ `origin/main` `be8ce1a` (2026-10-24)

repo นี้คือ `solo-empire-cloud-api`: **local admin API** (Python stdlib HTTP, `127.0.0.1:3440`) ที่ให้ sanitized cloud usage / PaaS inventory แก่ owner-web และรัน Render actions ผ่าน decision-record approval ไม่มี hosted deployment ไม่มี database ของตัวเอง ทุก diagram มี `Sources:` และ "Open questions" แยกไว้ ข้อมูล consumer อ้าง owner-web `bookchaowalit/life-dashboard-web` (local checkout `bdc4e63`, 2026-10-22) ops records ใน memory ไม่มีบรรทัดที่ระบุ repo นี้ จึงไม่ได้อ้าง

| # | Item | Status | File | Sources read |
|---|---|---|---|---|
| 01 | Business process (As-Is / To-Be) | done (To-Be = open question) | [01-business-process.md](01-business-process.md) | PRODUCT.md, README.md, server.py, paas_execute.py, paas_action.py, SPEC-001, DOCPACK card |
| 02 | Use cases | done | [02-use-cases.md](02-use-cases.md) | server.py auth/gate, paas_execute.py identities, owner-web backends.ts |
| 03 | User flows (request journeys; no UI) | done | [03-user-flows.md](03-user-flows.md) | server.py, paas_execute.py dispatch, owner-web cloud module + proxy route |
| 04 | Traceability (RTM) | done | [04-traceability.md](04-traceability.md) | PRODUCT.md, SPEC-001, server.py, adapters/, tests/, ci.yml |
| 05 | C4 Context | done | [05-c4-context.md](05-c4-context.md) | server.py, adapters/*, error_reporting.py, owner-web |
| 06 | C4 Container | done | [06-c4-container.md](06-c4-container.md) | server.py, adapters/, registry/, error_reporting.py, cloud_usage.py |
| 07 | C4 Component | done | [07-c4-component.md](07-c4-component.md) | server.py, adapters/* imports and entry points |
| 08 | ADRs (5) | done | [08-adr/](08-adr/) | server.py, pyproject.toml, uv.lock, paas_execute.py, paas_action.py, policy, README.md, git log |
| 09 | ERD | done (client-side model of decisions API + registry documents) | [09-erd.md](09-erd.md) | paas_action.py, paas_execute.py, decision_store.py, legacy_decision_tables.sql, registry/* |
| 10 | Sequences | done | [10-sequences.md](10-sequences.md) | server.py, cloud_usage.py, paas_execute.py, paas_action.py, decision_store.py |
| 11 | State machines | done | [11-state-machines.md](11-state-machines.md) | paas_action.py, paas_execute.py, policy, legacy DDL |
| 12 | API and integrations | reused + extended | [12-api-integration.md](12-api-integration.md) → [`contracts/cloud.v1.json`](../../contracts/cloud.v1.json) | server.py, contract, all adapters with base URLs |
| 13 | Threat model (DFD + STRIDE) | done | [13-threat-model.md](13-threat-model.md) | server.py, error_reporting.py, adapters (gate, redirects, SSRF), ci.yml |
| 14 | Backup / DR | done (stateless; data owned elsewhere; RTO/RPO not defined) | [14-backup-dr.md](14-backup-dr.md) | README.md, PRODUCT.md, ci.yml, decision_store.py, task_store.py |
| 15 | CI/CD pipeline | done (CI only, no CD) | [15-cicd-pipeline.md](15-cicd-pipeline.md) | ci.yml, platform-ci-workflows @87dc5e1, gh run view, renovate.json |
| 16 | Deployment | done (local runtime; no hosted deploy) | [16-deployment.md](16-deployment.md) | PRODUCT.md, README.md, server.py, adapters config readers, owner-web |
| 17 | Test coverage matrix | done | [17-test-coverage-matrix.md](17-test-coverage-matrix.md) | tests/*.py, tests/support/, ci.yml, SPEC-001 §6 |
| 18 | Git / release workflow | done | [18-git-release-workflow.md](18-git-release-workflow.md) | git log, gh pr list, gh run list, gh branch protection API |
| 19 | Service dependency map | done | [19-service-dependency-map.md](19-service-dependency-map.md) | server.py, adapters/*, pyproject.toml, ci.yml, owner-web |
| 20 | Observability | done | [20-observability.md](20-observability.md) | error_reporting.py, server.py, decision_store.py, PRODUCT.md |
| 21 | Incident response | done (no alert channel; code runbook) | [21-incident-response.md](21-incident-response.md) | server.py, paas_execute.py, policy, PRODUCT.md |
| 22 | DORA | done (proxies; no deploys exist) | [22-dora.md](22-dora.md) | git log, gh pr list, gh run list |

## ADRs

- [ADR-0001](08-adr/ADR-0001-local-loopback-admin-api.md) Local loopback admin API, fail closed off-loopback
- [ADR-0002](08-adr/ADR-0002-python-stdlib-http-uv-lock.md) Python stdlib HTTP server, uv-locked minimal dependencies
- [ADR-0003](08-adr/ADR-0003-governed-paas-execution-via-decisions.md) Governed PaaS execution through decision records
- [ADR-0004](08-adr/ADR-0004-vendored-adapters-and-registries.md) Vendor provider adapters and registries into the repo
- [ADR-0005](08-adr/ADR-0005-offline-default-and-sanitized-projections.md) Offline-by-default reads, sanitized projections, runtime-only credentials

## Related docs (reused, not copied)

- [`PRODUCT.md`](../../PRODUCT.md), [`README.md`](../../README.md)
- [`contracts/cloud.v1.json`](../../contracts/cloud.v1.json)
- [`specs/001-l2-baseline/spec.md`](../../specs/001-l2-baseline/spec.md)
- [`DOCPACK/00-product-card.md`](../../DOCPACK/00-product-card.md)
- Central standard: [ADR-0004 TDD + SDD](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md)

## Open questions for the owner (รวม)

1. คง local หรือขึ้นเป็น hosted cell (product card §8) — กำหนด To-Be, deployment, DORA
2. ตั้ง `CLOUD_API_TOKEN` และ `SENTRY_DSN` บนเครื่อง owner หรือไม่
3. `EMPIRE_DECISIONS_API` ชี้ไป instance ไหน และ backup ของ decisions cell ครอบ PaaS records ไหม
4. RTO / RPO และที่เก็บ postmortem
5. Branch protection / required checks บน `main`
6. Reject proposal ทำผ่าน decision-cli นอก API นี้ — ยืนยัน; ต้องการแยกคน approve / execute ไหม
7. SPEC-001 รอ owner approve และ §4 ต้องแก้ (review 2026-10-24)
