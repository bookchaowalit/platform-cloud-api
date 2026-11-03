# 18 — Git / release workflow

`main` **ไม่มี branch protection** (`gh api .../branches/main/protection` → 404 "Branch not protected", ไม่มี rulesets) commits ส่วนใหญ่ push ตรงเข้า `main` มี PR เดียว (#1, squash) ไม่มี tag หรือ release

```mermaid
gitGraph
  commit id: "c065053 local work"
  commit id: "a828861"
  commit id: "899a205 standalone"
  commit id: "438ba09 vendor adapters"
  commit id: "5875ae1 docpack"
  commit id: "9f994ba fix redirects"
  branch ci/devsecops-phase1
  commit id: "8ab3731 CI red"
  commit id: "8c1e9d9"
  commit id: "74b366d CI green"
  checkout main
  merge ci/devsecops-phase1 id: "4ab2a89 PR #1 squash"
  commit id: "e9a2533 L2 baseline"
  commit id: "be8ce1a SPEC review"
```

(PR #1 ถูก squash-merge; gitGraph แสดงเป็น merge เพื่อให้เห็น branch)

```mermaid
flowchart LR
  DEV["Edit in clone or worktree"] --> CH{"Path"}
  CH -->|"most commits"| PUSH["git push main"]
  CH -->|"PR #1 only"| PR["Branch + PR"]
  PR --> CIPR["CI on pull_request"]
  CIPR --> MERGE["Merge into main"]
  PUSH --> CIM["CI on push main"]
  MERGE --> CIM
  CIM --> REL["Release = new main; owner restarts local server.py"]
```

Sources: `git log origin/main` (at `be8ce1a`), `gh pr list -R bookchaowalit/platform-cloud-api --state all`, `gh run list -R bookchaowalit/platform-cloud-api`, `gh api repos/bookchaowalit/platform-cloud-api/branches/main/protection`, `gh api .../rulesets`, `.github/workflows/ci.yml`, SPEC-001 ("Main-only: yes")

## Open questions

- ต้องการ branch protection / required checks บน `main` ไหม (ตอนนี้ red CI ไม่บล็อก push)
- การ "release" ไปเครื่อง owner ทำอย่างไร (pull + restart) — ไม่มีบันทึกใน repo
