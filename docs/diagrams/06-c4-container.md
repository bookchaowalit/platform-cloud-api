# 06 — C4 Container

```mermaid
C4Container
  title cloud-api containers
  Person(owner, "Owner")
  System_Ext(ownerweb, "owner-web", "Next.js :3400")
  Container_Boundary(b, "cloud-api process (python3 server.py)") {
    Container(http, "HTTP adapter", "ThreadingHTTPServer + RequestHandler", "Bounds body, Content-Length, CORS headers")
    Container(core, "CloudApi", "Python", "Routing, auth, owner gate, safe errors")
    Container(adapters, "Vendored adapters", "Python modules in adapters/", "Usage, inventory, policy, preflight, execute")
    ContainerDb(registry, "Registries", "YAML / JSON files in registry/", "Providers, action policy, free resources")
    Container(errrep, "error_reporting", "sentry-sdk, opt-in", "Scrubbed capture")
  }
  ContainerDb_Ext(accounts, "Account metadata", "YAML under SOLO_ACCOUNTS_ROOT/accounts/cloud", "Optional platform-accounts-api checkout")
  System_Ext(decisions, "Decisions API")
  System_Ext(secrets, "Infisical / Vault / env")
  System_Ext(providers, "Provider APIs")
  System_Ext(sentry, "Sentry")
  Rel(owner, http, "Commands from loopback")
  Rel(ownerweb, http, "GET read routes")
  Rel(http, core, "handle(method, target, headers, body, peer)")
  Rel(core, adapters, "Function calls")
  Rel(core, errrep, "capture(exc)")
  Rel(adapters, registry, "Read")
  Rel(adapters, accounts, "Read")
  Rel(adapters, decisions, "HTTPS")
  Rel(adapters, secrets, "Resolve")
  Rel(adapters, providers, "HTTPS, no redirects")
  Rel(errrep, sentry, "HTTPS")
```

Sources: `server.py` (`CloudApiServer`, `RequestHandler`, `CloudApi`), `adapters/`, `registry/`, `error_reporting.py`, `adapters/cloud_usage.py` (`ACCOUNTS_REPO`), `README.md`

ไม่มี Dockerfile หรือ container image: "container" ในที่นี้คือหน่วย runtime ภายใน process เดียว (`PRODUCT.md`: no Dockerfile, no deploy target)
