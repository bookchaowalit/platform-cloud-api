# 11 — State machines

## Decision record (PaaS) — `action_status` ร่วมกับ `status` / `approval_status`

```mermaid
stateDiagram-v2
  [*] --> pending_approval: register (status proposed, approval pending)
  pending_approval --> queued: approve by owner-cli (status approved, decided_at)
  queued --> queued: execute gate fails (409, nothing claimed)
  queued --> blocked: execute claims lock (attempt submission_unknown)
  blocked --> executed: verify or reconcile succeeded (status completed, lock released)
  blocked --> failed: verify or reconcile failed (lock released)
  blocked --> blocked: pending or verification_required
  executed --> [*]
  failed --> [*]
```

Approval ใช้ได้ 3600 s จาก `decided_at` หลังจากนั้น execute ถูกปฏิเสธ (`assess_approval_row` `approval_fresh`) Reject / defer อยู่ใน schema แต่ไม่มี operation ใน API นี้

## Execution attempt (event metadata, actor `paas_executor`)

```mermaid
stateDiagram-v2
  [*] --> submission_unknown: claimed before network I/O
  submission_unknown --> pending: Render returned dep- id, or set-auto-deploy
  submission_unknown --> verification_required: response without deploy id
  submission_unknown --> submission_unknown: submit raised (error_class)
  pending --> succeeded: verify, state live and health 2xx
  pending --> failed: verify, build_failed or canceled etc
  pending --> verification_required: verify cannot prove result
  submission_unknown --> succeeded: reconcile
  submission_unknown --> failed: reconcile
  verification_required --> succeeded: reconcile
  verification_required --> failed: reconcile
  succeeded --> [*]
  failed --> [*]
```

Pending นานเกิน 900 s → `verification-timeout-check-provider` (ไม่เปลี่ยน state)

Sources: `adapters/paas_action.py` (`register_proposal`, `assess_approval_row`), `adapters/paas_execute.py` (`approve`, `execute`, `verify`, `reconcile`, `update`, `Render.verify`, `Render.reconcile`), `registry/paas-action-policy.json` (`approval`, `verification.timeout_seconds`), `tests/support/legacy_decision_tables.sql` (CHECK lists)
