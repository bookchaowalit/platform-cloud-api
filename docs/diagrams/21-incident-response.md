# 21 — Incident response

ไม่มี on-call / paging / Telegram alert สำหรับ service นี้ (local tool) ช่องทางสัญญาณที่มีจริงคือ: response code ที่ owner เห็นเอง, Sentry (ถ้าตั้ง DSN), และ GitHub Actions CI ผล flow ด้านล่างใช้ runbook ที่ฝังอยู่ใน code (ข้อความ "PaaS command result is unknown; inspect the decision record")

```mermaid
flowchart TD
  A1["503 command_result_unknown from POST commands"] --> T1["Triage: operation=status on decision_id"]
  A2["Sentry issue tag service=cloud-api (if DSN)"] --> T0["Triage: which route, which exception class"]
  A3["503 *_unavailable or provider error_class on Cloud page"] --> T2["Triage: credentials, provider status, network"]
  A4["CI red on main or PR"] --> T3["Triage: gh run view --log-failed"]
  T1 --> R{"attempt status"}
  R -->|"submission_unknown or verification_required or pending"| RC["operation=reconcile (reads Render, never resubmits)"]
  R -->|"failed"| NEW["Register a new proposal (rollback is a separate proposal)"]
  RC --> OUT{"Resolved?"}
  OUT -->|"executed or failed"| DONE["Lock released"]
  OUT -->|"still pending after 900 s"| MAN["Check Render dashboard manually"]
  T0 --> FIX["Fix in repo, push main, CI"]
  T2 --> FIX2["Fix credential or wait for provider"]
  T3 --> FIX
  DONE --> PM["Postmortem: not defined in repo"]
  MAN --> PM
  FIX --> PM
```

- Postmortem template / location: **not defined** (ไม่มีใน repo)
- `automatic_rollback: false`: rollback ต้องเป็น proposal ใหม่ผ่าน approval

Sources: `server.py` (`_command`, `_unavailable`), `error_reporting.py`, `adapters/paas_execute.py` (`verify`, `reconcile`, timeout 900 s), `registry/paas-action-policy.json` (`verification`), `.github/workflows/ci.yml`, `PRODUCT.md` Measures ("each needs a decision-record check")

## Open questions

- ต้องการ alert (เช่น Telegram) เมื่อเกิด `command_result_unknown` หรือไม่
- ที่เก็บ postmortem สำหรับ PaaS incidents
