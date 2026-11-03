# ADR-0001 — Local loopback admin API, fail closed off-loopback

- Status: accepted (retro-documented)
- Date: retro-documented 2026-11-04 (behaviour present since the 2026-10-11 standalone split)

## Context

API นี้อ่านด้วย provider credentials ของ owner และเปลี่ยน infrastructure ได้ (Render actions) `PRODUCT.md` Positioning: "A local admin API, not a public service … it must not sit on a public host"

## Decision

- Bind ค่าเริ่มต้น `127.0.0.1:3440` (`CLOUD_API_HOST`, `CLOUD_API_PORT`)
- `serve()` ปฏิเสธการเริ่มเมื่อ bind non-loopback หรือ `CLOUD_API_ENV=production` โดยไม่มี `CLOUD_API_TOKEN`
- Read routes ต้อง Bearer ตรงกับ token (`secrets.compare_digest`) เมื่อตั้ง token; ไม่มี token ผ่านได้เฉพาะ env ที่ไม่ใช่ production
- Command route ต้อง loopback peer + allowed local `Origin` (http, ไม่มี userinfo) + `Host` loopback + `X-Solo-PaaS-Command: 1` + `application/json` + ไม่มี forwarding headers + token ถ้าตั้ง

## Consequences

- ไม่มี hosted deployment, ไม่มี Dockerfile; owner-web ต้องรันบนเครื่องเดียวกัน (default origin `http://127.0.0.1:3440`)
- Reverse proxy ใดๆ ที่ใส่ `X-Forwarded-*` จะทำให้ commands ถูก 403 โดยตั้งใจ

## Evidence

`server.py` (`serve`, `_authorized`, `_owner_gate`, `LOOPBACK_PEERS`, `FORWARDED_HEADERS`), `README.md` (Run), `PRODUCT.md` (Positioning, Operating Context), `tests/test_server.py` (`test_production_without_token_fails_closed`, `test_command_requires_local_owner_boundary`, `test_command_rejects_forwarded_headers_and_oversized_body`)
