# 07 — C4 Component

```mermaid
C4Component
  title cloud-api components
  Container_Boundary(core, "CloudApi (server.py)") {
    Component(router, "handle", "Python", "Path routing, 414/400/404/405")
    Component(readauth, "_require_read_auth", "Python", "Bearer compare_digest; production without token fails closed")
    Component(gate, "_owner_gate", "Python", "Loopback peer, no forwarding headers, marker, JSON, local Origin")
    Component(cmd, "_command", "Python", "Maps GateError 409, ValueError 400, other 503")
  }
  Container_Boundary(ad, "adapters/") {
    Component(usage, "cloud_usage.build_snapshot", "Python", "Aggregates inventory, R2, Vercel billing, GitHub Actions, free quota, accounts")
    Component(inv, "paas_inventory.run_inventory", "Python", "Vercel, Render, Railway, Fly.io, Heroku + cloud_read_adapters")
    Component(health, "paas_health", "Python", "Provider health and safe errors")
    Component(policy, "paas_action", "Python", "Policy, proposal fingerprint, lock key, approval check")
    Component(pre, "render_preflight", "Python", "Discovery and action preflight via API or render CLI")
    Component(exec, "paas_execute.dispatch", "Python", "register, status, approve, execute, verify, reconcile; Render adapter")
    Component(dstore, "decision_store.ApiDecisionStore", "Python", "Decisions API client, no redirects")
    Component(auth, "auth_resolver / secret_resolver", "Python", "Infisical, Vault or env")
  }
  Rel(router, readauth, "GET routes")
  Rel(router, cmd, "POST /api/v1/paas/commands")
  Rel(cmd, gate, "First")
  Rel(router, usage, "/api/v1/cloud/usage")
  Rel(router, inv, "/api/v1/paas/inventory")
  Rel(router, policy, "/api/v1/paas/actions")
  Rel(router, pre, "/api/v1/paas/render/*")
  Rel(cmd, exec, "dispatch(command)")
  Rel(usage, inv, "run_inventory")
  Rel(inv, health, "Uses")
  Rel(exec, policy, "Uses")
  Rel(exec, dstore, "Read and update records")
  Rel(policy, dstore, "register_proposal")
  Rel(exec, auth, "Render credential")
  Rel(inv, auth, "Provider credentials")
  Rel(pre, auth, "Render credential")
```

Sources: `server.py`, `adapters/cloud_usage.py` (imports), `adapters/paas_inventory.py` (`INVENTORIES`, `run_inventory`), `adapters/paas_execute.py` (imports, `Render`, `dispatch`), `adapters/paas_action.py`, `adapters/render_preflight.py` (`SOURCES = {"api", "cli"}`, `_run_cli`), `adapters/decision_store.py`, `adapters/auth_resolver.py`, `adapters/secret_resolver.py`
