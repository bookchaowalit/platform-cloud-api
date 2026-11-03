# 03 — User flows

ไม่มี UI ใน repo นี้ (API only, `PRODUCT.md` Platform = api) flow ด้านล่างจึงเป็น journey ระดับ request ต่อ role จาก routes ใน `server.py`

## Flow 1 — Owner ดู Cloud page ใน owner-web

```mermaid
flowchart TD
  S["Owner opens Cloud module in owner-web"] --> P["owner-web proxy /api/cloud/v1/..."]
  P --> AUTH{"Token configured on cloud-api?"}
  AUTH -->|"yes and Bearer matches"| OK["Read route runs"]
  AUTH -->|"yes but missing or wrong"| E401["401 cloud_api_auth_required"]
  AUTH -->|"no token, env != production"| OK
  OK --> U["GET /api/v1/cloud/usage?live=false"]
  OK --> I["GET /api/v1/paas/inventory?live=false"]
  OK --> A["GET /api/v1/paas/actions"]
  U --> R["Render providers, quota, billing"]
  I --> R
  A --> R
  R --> L{"Need fresh provider data?"}
  L -->|"yes"| LV["Same routes with live=true"]
  L -->|"no"| END["Done"]
  LV --> R
```

## Flow 2 — Local owner รัน Render action

```mermaid
flowchart TD
  D["GET /api/v1/paas/render/discovery?live=true"] --> PF["GET /api/v1/paas/render/action-preflight?service_id&environment_id&action"]
  PF --> REG["POST commands: register"]
  REG --> ST["POST commands: status"]
  ST --> AP["POST commands: approve, confirm=true, proposal_id"]
  AP --> EX["POST commands: execute, confirm=true (within 1 hour)"]
  EX --> R{"Result"}
  R -->|"200 attempt pending"| VE["POST commands: verify"]
  R -->|"409 gate code"| FIX["Fix cause or register again"]
  R -->|"200 submission_unknown or verification_required"| RC
  R -->|"503 command_result_unknown"| RC["POST commands: reconcile"]
  VE --> T{"attempt status terminal?"}
  RC --> T
  T -->|"executed or failed"| DONE["Done"]
  T -->|"still nonterminal"| POLL["Poll verify or reconcile again, or inspect in Render dashboard"]
  POLL --> T
```

## Flow 3 — Health check

```mermaid
flowchart LR
  C["Any caller"] --> H["GET /health"] --> J["status ok, service, schema_version, environment, timestamp"]
```

Sources: `server.py` (`handle`, `_command`, `_render_discovery`, `_render_preflight`, `_owner_gate`), `adapters/paas_execute.py` (`dispatch`), `README.md` (Run), owner-web `modules/cloud/api.ts`, `lib/backends.ts`, `app/api/[service]/[...path]/route.ts`

## Open questions

- owner-web เคยเปิด `live=true` จาก UI หรือไม่ และกดเมื่อไร (`modules/cloud/api.ts` รับ `live` เป็น parameter)
