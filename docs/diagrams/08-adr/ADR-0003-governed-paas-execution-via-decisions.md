# ADR-0003 — Governed PaaS execution through decision records

- Status: accepted (retro-documented)
- Date: retro-documented 2026-11-04

## Context

PaaS change ต้องไม่เกิดโดยไม่มี approval ที่สดและผูกกับ proposal ที่ตรวจแล้ว (`PRODUCT.md` Success) และ submission ที่กำกวมต้องไม่ถูกส่งซ้ำ

## Decision

- Source of truth ของ approval = decisions API `decision_records` (domain `paas`, `action_type` `external_change`), ผ่าน `decision_store.ApiDecisionStore`
- Proposal ผูกด้วย fingerprint: `source_ref == "paas-proposal:" + sha256(canonical request)[:20]`; dedupe key `paas-action:<fingerprint>`
- Approval อายุสูงสุด 3600 s จาก `decided_at` (`registry/paas-action-policy.json` `approval.max_age_seconds`)
- Approve ใช้ identity `owner-cli`; register/execute/verify/reconcile ใช้ `paas-operator`
- Execute: policy enabled + adapter `render-v1` + approval valid + live preflight → atomic claim (update ที่ `expected_version` + unique `execution_lock_key`) ก่อน network I/O
- Timeout/ambiguous → `submission_unknown`, ไม่ resubmit; แก้ด้วย `reconcile` ที่อ่าน provider เท่านั้น
- `automatic_rollback: false`; rollback เป็น proposal แยก
- มีเพียง Render adapter (`render-v1`) ที่ execute ได้; Vercel/Railway/Fly.io/Heroku เป็น `disabled`

## Consequences

- PaaS commands ใช้ไม่ได้ถ้า decisions API หรือ automation token ไม่มี (`ClientConfigError`)
- ต้องมีคนตรวจ decision record เมื่อได้ 503 `command_result_unknown`

## Evidence

`adapters/paas_execute.py` (`approve`, `execute`, `verify`, `reconcile`, `update`, `connection`), `adapters/paas_action.py` (`proposal_fingerprint`, `execution_lock_key`, `register_proposal`, `assess_approval_row`), `adapters/decision_store.py`, `registry/paas-action-policy.json`, `tests/paas_execute_test.py` (`test_two_executors_can_only_submit_once`, `test_timeout_is_unknown_and_never_retried_even_if_requeued`, `test_expired_approval_blocks_before_provider_preflight`)
