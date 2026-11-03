# ADR-0005 — Offline-by-default reads, sanitized projections, runtime-only credentials

- Status: accepted (retro-documented)
- Date: retro-documented 2026-11-04

## Context

Browser ต้องไม่ถือ credential และ response ต้องไม่มี provider payload (`README.md`, `PRODUCT.md`)

## Decision

- Read routes default `live=false`: สร้าง projection จาก registry + credential state เท่านั้น; `?live=true` จึงอ่าน provider
- Credential resolve ตอนใช้ผ่าน `secret_resolver` (`SECRETS_PROVIDER` = `auto` | `env` | `infisical` | `vault`), เก็บใน memory เท่านั้น
- ทุก response ห่อด้วย envelope `cloud.v1` (`contract`, `route`) ตาม `contracts/cloud.v1.json`
- Error ที่ส่งกลับเป็นโค้ดปลอดภัย (`SAFE_ERROR_CODE`), ไม่มี body/URL/traceback; Sentry opt-in และ scrub (SPEC-001 AC-01..07)

## Evidence

`server.py` (`_query_bool` default false, `_contract_payload`, `_safe_error_code`, `_unavailable`), `adapters/secret_resolver.py` (module docstring), `adapters/auth_resolver.py`, `contracts/cloud.v1.json`, `error_reporting.py`, `tests/cloud_read_adapters_test.py` (`test_all_offline_adapters_never_resolve_auth_or_read_api`), `tests/paas_control_plane_test.py` (`test_live_check_is_bounded_and_never_returns_provider_payload`)
