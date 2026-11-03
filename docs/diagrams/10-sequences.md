# 10 — Sequences

## 1. Cloud usage (live)

```mermaid
sequenceDiagram
  participant W as owner-web
  participant H as RequestHandler
  participant C as CloudApi
  participant U as cloud_usage
  participant S as secret_resolver
  participant P as Providers
  W->>H: GET /api/v1/cloud/usage?live=true + Bearer
  H->>C: handle(GET, target, headers, peer)
  C->>C: _require_read_auth
  C->>U: build_snapshot(live=true)
  U->>S: resolve credentials per provider
  U->>P: inventory, R2 metrics, Vercel billing, GitHub Actions usage
  P-->>U: JSON
  U-->>C: sanitized snapshot
  C-->>H: 200 cloud.v1 envelope route=cloud_usage
  H-->>W: JSON, Cache-Control no-store
  Note over C,U: any exception becomes 503 cloud_usage_unavailable
```

## 2. Register and approve a proposal

```mermaid
sequenceDiagram
  participant O as Local owner
  participant C as CloudApi
  participant X as paas_execute
  participant A as paas_action
  participant D as Decisions API
  O->>C: POST /api/v1/paas/commands operation=register
  C->>C: _owner_gate, _json_body
  C->>X: dispatch
  X->>A: build_proposal, register_proposal
  A->>D: GET by dedupe_key
  A->>D: POST /v1/decisions (paas-operator token)
  D-->>A: id
  X-->>C: snapshot
  C-->>O: 200 route=paas_command
  O->>C: POST commands operation=approve confirm=true proposal_id
  C->>X: dispatch
  X->>D: GET record + history (owner-cli token)
  X->>D: PATCH status approved, action_status queued, decided_at, expected_version
  X-->>C: snapshot
  C-->>O: 200
```

## 3. Execute and verify

```mermaid
sequenceDiagram
  participant O as Local owner
  participant X as paas_execute
  participant D as Decisions API
  participant R as Render API
  participant HP as Service health URL
  O->>X: execute(decision_id), confirm=true
  X->>X: policy enabled and adapter render-v1
  X->>D: check approval (fresh, bound, queued)
  X->>R: preflight: service, environment, deploys
  X->>D: PATCH action_status blocked + execution_lock_key + attempt submission_unknown
  alt claim refused
    D-->>X: 409
    X-->>O: 409 execution-already-claimed or resource-operation-in-progress
  else claimed
    X->>R: submit deploy, restart, rollback or PATCH autoDeploy
    R-->>X: deploy id or error
    X->>D: PATCH attempt pending or verification_required or submission_unknown
    X-->>O: 200 snapshot
  end
  O->>X: verify(decision_id)
  X->>R: read deploy or service state
  X->>HP: unauthenticated GET health_path, no redirects
  X->>D: PATCH action_status executed or failed, release lock
```

## 4. Reconcile an ambiguous submission

```mermaid
sequenceDiagram
  participant O as Local owner
  participant C as CloudApi
  participant X as paas_execute
  participant R as Render API
  participant D as Decisions API
  O->>C: POST commands execute
  C->>X: dispatch
  X-->>C: unexpected exception
  C->>C: capture(exc) if SENTRY_DSN
  C-->>O: 503 command_result_unknown
  O->>C: POST commands operation=reconcile confirm=true
  C->>X: dispatch
  X->>R: read recent deploys matching revision
  X->>D: PATCH executed or failed or stay blocked, reconciled=true
  X-->>O: 200 snapshot (never resubmits)
```

Sources: `server.py` (`handle`, `_cloud_usage`, `_command`), `adapters/cloud_usage.py` (`build_snapshot`), `adapters/paas_execute.py` (`dispatch`, `approve`, `execute`, `verify`, `reconcile`, `Render`), `adapters/paas_action.py` (`register_proposal`), `adapters/decision_store.py`, `error_reporting.py`
