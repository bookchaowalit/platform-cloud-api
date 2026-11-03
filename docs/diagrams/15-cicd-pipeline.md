# 15 — CI/CD pipeline

CI เท่านั้น ไม่มี CD (ไม่มี deploy job / deploy config) Workflow เดียว `.github/workflows/ci.yml` เรียก reusable workflows จาก `bookchaowalit/platform-ci-workflows` pin SHA `87dc5e1` (v1.1.1) บน GitHub-hosted runners (repo public)

```mermaid
flowchart TD
  T1["push to main"] --> CI["workflow CI (concurrency ci-ref, cancel in progress)"]
  T2["pull_request"] --> CI
  T3["workflow_dispatch"] --> CI
  CI --> API["job api: ci-python.yml, python 3.12"]
  CI --> SEC["job security: security.yml"]
  subgraph APIJ["api / python (.)"]
    A1["Checkout"] --> A2["setup-uv + Python"]
    A2 --> A3["uv sync --frozen --all-extras"]
    A3 --> A4["Lint: Ruff"]
    A4 --> A5["Typecheck: mypy"]
    A5 --> A6["Test: pytest"]
    A6 --> A7["Coverage gate 61%"]
  end
  subgraph SECJ["security"]
    S1["gitleaks"]
    S2["semgrep"]
    S3["osv-scanner"]
    S4["trivy-fs"]
  end
  API --> APIJ
  SEC --> SECJ
  APIJ --> R["Status on commit / PR"]
  SECJ --> R
  R -.->|"no deploy step"| L["Owner pulls main and runs python3 server.py locally"]
  REN["Renovate: Mon before 9am BKK; lockfile monthly"] -.->|"opens PRs"| T2
```

ผลล่าสุด run `40084274005` (push `be8ce1a`, 2026-10-24): `api / python (.)`, `security / gitleaks`, `security / trivy-fs`, `security / osv-scanner`, `security / semgrep` = success

Sources: `.github/workflows/ci.yml`, `platform-ci-workflows` `ci-python.yml` and `security.yml` at `87dc5e1c7e0416886a6371d5a101bb2ccba38edd` (via `gh api .../contents`), `gh run view 40084274005 --json jobs`, `renovate.json`, `PRODUCT.md`
