# 05 — C4 Context

```mermaid
C4Context
  title cloud-api system context
  Person(owner, "Owner", "Single operator of Solo Empire")
  System(cloudapi, "cloud-api", "Local admin API on 127.0.0.1:3440: sanitized cloud usage, PaaS inventory, governed Render actions")
  System_Ext(ownerweb, "owner-web", "bookchaowalit/life-dashboard-web, Next.js on :3400, proxies GET routes")
  System_Ext(decisions, "Decisions API", "Decision records and events, EMPIRE_DECISIONS_API")
  System_Ext(secrets, "Infisical / Vault", "Provider credentials, SECRETS_PROVIDER")
  System_Ext(paas, "PaaS providers", "Render, Vercel, Railway, Fly.io, Heroku")
  System_Ext(cloud, "Cloud and SaaS providers", "Cloudflare R2, GitHub billing, Neon, Supabase, Upstash, RunPod")
  System_Ext(sentry, "Sentry", "Errors only, when SENTRY_DSN is set")
  Rel(owner, ownerweb, "Views Cloud page")
  Rel(owner, cloudapi, "PaaS commands from loopback")
  Rel(ownerweb, cloudapi, "GET /api/v1/...", "HTTP + Bearer")
  Rel(cloudapi, decisions, "Register, approve, claim, update", "HTTPS + automation token")
  Rel(cloudapi, secrets, "Resolve credentials", "CLI or REST")
  Rel(cloudapi, paas, "Read inventory; Render writes", "HTTPS")
  Rel(cloudapi, cloud, "Read usage and inventory", "HTTPS")
  Rel(cloudapi, sentry, "Scrubbed exceptions", "HTTPS")
```

Sources: `server.py`, `error_reporting.py`, `adapters/decision_store.py`, `adapters/secret_resolver.py`, `adapters/paas_inventory.py`, `adapters/cloud_read_adapters.py`, `adapters/cloudflare_r2_usage.py`, `adapters/github_actions_usage.py`, `adapters/vercel_billing.py`, `adapters/paas_execute.py`, owner-web `lib/backends.ts`

## Open questions

- Decisions API ที่ใช้จริงบนเครื่อง owner เป็น hosted cell หรือ local (ค่า `EMPIRE_DECISIONS_API` อยู่นอก repo)
