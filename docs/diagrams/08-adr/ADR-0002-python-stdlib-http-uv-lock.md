# ADR-0002 — Python stdlib HTTP server, uv-locked minimal dependencies

- Status: accepted (retro-documented)
- Date: retro-documented 2026-11-04 (lock and strict mypy since `e9a2533`, 2026-10-22)

## Context

Service เล็ก ใช้คนเดียว ต้องการ attack surface ต่ำและ reproducible install (SPEC-001)

## Decision

- HTTP ด้วย `http.server.ThreadingHTTPServer` + `BaseHTTPRequestHandler` ไม่มี web framework
- Runtime dependencies เพียง `PyYAML` และ `sentry-sdk`; dev: pytest, pytest-cov, mypy, types-PyYAML
- `uv.lock` pin ทุกอย่าง, `[tool.uv] package = false` (รันจาก checkout ไม่ใช่ installable package)
- Python 3.12, mypy `--strict`-equivalent overrides สำหรับ service modules, Ruff ตาม `ruff.toml`

## Consequences

- Body / Content-Length / Transfer-Encoding limit ต้องเขียนเอง (`RequestHandler._dispatch`, `MAX_BODY_BYTES = 16 KiB`)
- HTTP client ทั้งหมดเป็น `urllib.request`; `_NoRedirect` handlers ใช้ใน `task_store.py`, `cloud_read_adapters.py`, `paas_execute.py` แต่ live inventory reads (`paas_health.py` `_get_json`/`_post_json`) ใช้ `urlopen` ธรรมดาที่ตาม redirect

## Evidence

`server.py` imports, `pyproject.toml`, `uv.lock`, `ruff.toml`, `.github/workflows/ci.yml` (`python-version: "3.12"`), `specs/001-l2-baseline/spec.md`, commit `e9a2533`
