# Product

<!-- impeccable:product-schema 1 -->

## Platform

api

## Users

- The owner, through `owner-web` (`bookchaowalit/life-dashboard-web`), which reads the cloud usage
  and PaaS inventory projections (default CORS origins `http://localhost:3400` and
  `http://127.0.0.1:3400`). Which pages use which route today: [ต้องยืนยัน].
- The owner at the local machine, for PaaS commands: `POST /api/v1/paas/commands` accepts only a
  loopback peer with an allowed local `Origin`.

## Product Purpose

One place to see what the owner uses across cloud and PaaS providers (usage, free-quota headroom,
billing, inventory) and to run a small set of governed Render actions, without provider
credentials ever reaching a browser and without returning provider payloads.

Success: the owner can answer "what am I using and what does it cost" from one sanitized
projection, and no PaaS change happens without an approved, fresh decision record.

## Positioning

A local admin API, not a public service. It reads with the owner's provider credentials (resolved
by `adapters/secret_resolver.py` through Infisical, Vault or the environment) and can change
infrastructure, so it must not sit on a public host. The provider adapters and their registries
are owned here (`adapters/`, `registry/`); no other checkout is needed.

## Operating Context

- Local by design (registry `online-systems.yaml`, id `cloud`, status `exception`, host `local`).
  Run with `python3 server.py` on `127.0.0.1:3440`; no production URL, no Dockerfile, no deploy
  target.
- A non-loopback bind or `CLOUD_API_ENV=production` fails closed unless `CLOUD_API_TOKEN` is set.
- Read routes default to offline/credential-only mode; `?live=true` makes an explicit provider read.
- PaaS approvals live in the decisions API (`decision_records`), reached with the `paas-operator`
  and `owner-cli` automation tokens.
- Errors go to Sentry only when `SENTRY_DSN` is set (errors only, no personal data, tokens and URLs
  scrubbed). Whether a DSN is set on the owner's machine: [ต้องยืนยัน].

## Capabilities and Constraints

- `GET /health`; `GET /api/v1/cloud/usage`; `GET /api/v1/paas/inventory` (optional
  `provider_id`); `GET /api/v1/paas/actions` (the action policy); `GET
  /api/v1/paas/render/discovery`; `GET /api/v1/paas/render/preflight` and `/action-preflight`
  (read-only checks); `POST /api/v1/paas/commands`. Each projection carries the `cloud.v1` envelope
  (`contracts/cloud.v1.json`).
- Providers in `registry/cloud-providers.yaml` include Cloudflare, GitHub, Vercel, Render, Railway,
  Fly.io, Heroku, Neon, Supabase, Upstash and others; PaaS inventory and health cover Vercel,
  Render, Railway, Fly.io and Heroku.
- Commands: a loopback peer, an allowed local `Origin`, `X-Solo-PaaS-Command: 1`, JSON content at
  most 16 KiB, no forwarding headers, and the bearer token when configured. `paas_execute.dispatch`
  enforces proposal binding (fingerprint equals `source_ref`), approval at most one hour old,
  explicit confirmation, live provider preflight and an execution lock.
- Only the `render-v1` adapter executes (deploy of a full commit SHA, rollback, restart,
  set-auto-deploy on web services after live preflight); other adapters stay disabled. Redirects
  are refused on authenticated provider requests.
- Errors never include provider bodies, URLs, tokens or tracebacks: gate errors answer 409, invalid
  commands 400, unknown command outcomes 503 `command_result_unknown`, anything else 500
  `internal_error`.
- Out of scope: public hosting, browser-held credentials, actions on providers other than Render.

## Measures

- Providers whose live usage read succeeds versus `error` or `not_configured`.
- PaaS commands that end `command_result_unknown` (target: 0; each needs a decision-record check).
- Free-quota headroom per provider (`free_quota`) and monthly billed cost (Vercel, GitHub Actions,
  Cloudflare R2): [ต้องยืนยัน] which of these the owner reviews and how often.
