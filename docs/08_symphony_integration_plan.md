# Symphony Integration Plan

Status: active planning ledger for bundled single-repo integration

Last updated: 2026-04-25

## Purpose

This document is the local working plan for integrating OpenAI Symphony as the
execution layer for AIPD.

It exists so future work can be checked against a stable plan instead of relying
on chat history.

Update this file whenever a phase or task is completed, blocked, superseded, or
split.

## Core Principle

```text
AIPD owns semantic authority.
Symphony owns execution mechanics.
Every Symphony action must be derived from a validated AIPD gate outcome.
If the gate outcome is missing, invalid, or ambiguous, Symphony must fail closed.
```

## Repository Boundaries

| Area | Path | Role |
| :--- | :--- | :--- |
| AIPD protocol repo | `/Users/lihaozheng/Documents/AI/Product-Dev` | Protocol rules, artifacts, schemas, gate contracts, guard checks, and AIPD tests |
| Bundled Symphony runtime | `/Users/lihaozheng/Documents/AI/Product-Dev/runtime/symphony` | In-repo runtime distribution for one-download AIPD delivery |
| Symphony upstream checkout | `/Users/lihaozheng/Documents/AI/external/openai-symphony` | External read/audit source for Symphony |
| External demo roots | `/Users/lihaozheng/Documents/AI/aipd-symphony-demo-roots/*` | Real product/demo execution roots, kept outside the protocol repo |

Do not collapse protocol truth, bundled runtime, and external project truth into
one directory tree.

The AIPD repo now ships the Symphony runtime for one-download delivery, but the
semantic split remains:

- protocol rules and schemas live at the repository root
- bundled runtime code lives under `runtime/symphony`
- real product state still lives in the external `PROJECT_ROOT`

## Current Symphony Snapshot

| Field | Value |
| :--- | :--- |
| Upstream URL | `https://github.com/openai/symphony` |
| Local checkout | `/Users/lihaozheng/Documents/AI/external/openai-symphony` |
| Commit | `9e89dd9ff0a3eddb8813c77f633ca4534d6e14b2` |
| License | Apache-2.0 with `NOTICE` |
| Checkout state | clean except untracked `.DS_Store` in the external checkout |

## Completed External Audit

### Download And Pin

- [x] Cloned official upstream Symphony into an external directory.
- [x] Verified remote URL.
- [x] Pinned commit SHA.
- [x] Confirmed AIPD repo was not modified during checkout.

### Static Security Review

- [x] Confirmed no custom Git `core.hooksPath`.
- [x] Confirmed `.git/hooks` only contains Git sample hooks.
- [x] Identified executable files:
  - `.codex/worktree_init.sh`
  - `.codex/skills/land/land_watch.py`
- [x] Reviewed explicit high-risk execution surfaces:
  - workspace lifecycle hooks in `elixir/lib/symphony_elixir/workspace.ex`
  - Codex app-server launch in `elixir/lib/symphony_elixir/codex/app_server.ex`
  - SSH execution in `elixir/lib/symphony_elixir/ssh.ex`
  - Docker live e2e support under `elixir/test/support/live_e2e_docker/`
  - Linear/GitHub-oriented `.codex/skills/*`
  - default `elixir/WORKFLOW.md` hooks
- [x] Confirmed no hidden self-starting malware pattern was found in the static review.

Security conclusion:

```text
No hidden malware or auto-executing repository hook was found.
Symphony is still a high-authority execution runtime and must be gated by AIPD
before any production or real-project use.
```

### Local Tests

- [x] Installed `mise`.
- [x] Installed declared toolchain:
  - Erlang/OTP 28
  - Elixir 1.19.5-otp-28
- [x] Downloaded Hex dependencies with `mise exec -- mix deps.get`.
- [x] Ran local tests without live e2e, Docker worker, Linear, or real Codex session.

Observed test results:

| Run | Result | Notes |
| :--- | :--- | :--- |
| `mise exec -- mix test` | `230 tests, 1 failure, 2 skipped` | SSH fake trace timing failure |
| Targeted SSH test rerun | `8 tests, 0 failures` | Prior failure did not reproduce |
| `mise exec -- mix test` rerun | `230 tests, 2 failures, 2 skipped` | Retry timer lower-bound assertions |
| Targeted retry timing reruns | `1 test, 0 failures` for each failed case | Failures did not reproduce in isolation |
| `mise exec -- mix test --max-cases 1` | `230 tests, 1 failure, 2 skipped` | Retry timer lower-bound assertion |

Testing conclusion:

```text
The upstream local test suite is mostly healthy, but some timing assertions are
flaky on this machine. The failures are not evidence of malware or hidden
execution, but retry/backoff timing tests should be hardened before we rely on
them as integration gates.
```

## Integration Architecture

Target chain:

```text
AIPD MB Registry
  -> AIPD MB Tracker Adapter
  -> Symphony Orchestrator
  -> AIPD attempt_start Gate
  -> Symphony Codex App-Server Runner
  -> AIPD attempt_finish Gate
  -> Symphony Outcome Handler
```

Symphony may schedule an MB, but AIPD must authorize every execution attempt
before Codex starts and must judge every attempt result before Symphony retries,
releases, reviews, or closes the MB.

## Role Information Split

### AIPD Decision Surface

AIPD must decide:

- whether the MB may start now
- whether required inputs exist
- whether retry limit is reached
- whether human approval is required
- whether the attempt passed
- whether failure is retryable
- which issue type was found
- which role owns the next action
- which artifacts and evidence prove the outcome

### Symphony Instruction Surface

Symphony must receive:

- whether Codex may start
- which prompt packet to run
- whether to release, pause, defer, retry, review, close, or route recovery
- whether runtime retry/backoff is allowed
- retry delay when applicable
- worker/concurrency metadata
- observability references

Symphony must not infer AIPD ownership, semantic retry eligibility, or recovery
routing from process exit alone.

## Gate Outcome Contract

Future schema:

- `schemas/aipd-gate-outcome.schema.json`

Required shape:

```json
{
  "gate": "attempt_start",
  "mb_id": "fb1-mb2",
  "attempt_id": null,
  "aipd_decision": {
    "status": "blocked",
    "issue_type": "spec_gap",
    "route_to": "spec_architect",
    "next_action": "clarify_acceptance"
  },
  "symphony_instruction": {
    "action": "release_and_pause",
    "may_start_codex": false,
    "retryable": false,
    "retry_after_ms": null
  },
  "reason": "parent FB acceptance is missing or contradictory",
  "evidence_refs": [
    "runtime/preflight/mb_preflight_fb1-mb2.json"
  ],
  "state_ref": "runtime/state/fb1-mb2.state.json"
}
```

Allowed AIPD issue types:

- `spec_gap`
- `implementation_bug`
- `quality_evidence_gap`
- `state_drift`
- `environment_issue`
- `review_context_gap`

Allowed Symphony actions:

- `dispatch_codex`
- `defer_retry`
- `schedule_semantic_retry`
- `release_and_pause`
- `release_and_wait_input`
- `pause_wait_human`
- `release_to_review`
- `close_mb`
- `stop_and_route_owner`
- `stop_and_route_recovery`

Unknown action, missing field, or invalid enum must fail closed.

## Attempt Gates

### `attempt_start`

Responsibilities:

- run MB preflight
- check runtime state
- check retry limit
- check human approval
- check input artifacts and eval refs
- check concurrency locks
- create attempt id
- write state as `running` only after authorization
- snapshot workspace before execution
- build AIPD prompt packet
- return validated gate outcome

Codex must not start unless:

```text
symphony_instruction.may_start_codex == true
symphony_instruction.action == dispatch_codex
```

### `attempt_finish`

Responsibilities:

- snapshot workspace after execution
- compute changed files
- run post hook equivalent if retained
- run scope guard
- classify structural blockers
- run verifier
- write `verification_report.json`
- derive `last_verification_digest`
- update runtime state
- update failure log or project memory
- return validated gate outcome

## Start Failure Routing

| Start failure | AIPD issue type | Route to | Symphony action |
| :--- | :--- | :--- | :--- |
| Missing MB markdown | `spec_gap` | `spec_architect` | `release_and_pause` |
| Missing machine spec | `spec_gap` | `spec_architect` | `release_and_pause` |
| Invalid machine spec schema | `spec_gap` | `spec_architect` | `release_and_pause` |
| Parent FB missing or contradictory | `spec_gap` | `spec_architect` | `release_and_pause` |
| Missing input artifact | `review_context_gap` | `current_scene_lead` | `release_and_wait_input` |
| Missing external UI package | `review_context_gap` | `current_scene_lead` | `release_and_wait_input` |
| Missing research or experience prompt artifact | `review_context_gap` | `current_scene_lead` | `release_and_wait_input` |
| Missing eval asset | `quality_evidence_gap` | `builder` | `release_and_pause` |
| Runtime state invalid | `state_drift` | `recovery_coordinator` | `stop_and_route_recovery` |
| Active FB/MB mismatch | `state_drift` | `recovery_coordinator` | `stop_and_route_recovery` |
| Retry limit reached | prior issue type or `implementation_bug` | owning role or `recovery_coordinator` | `stop_and_route_recovery` |
| Human approval missing | `review_context_gap` | `current_scene_lead` | `pause_wait_human` |
| Concurrency lock held | none | none | `defer_retry` |
| Transient workspace IO issue | `environment_issue` if durable | `recovery_coordinator` if durable | `defer_retry` if transient |

An `attempt_start` failure must not automatically consume semantic retry count
unless AIPD classifies it as a durable failed attempt.

## Finish Outcome Routing

| Finish outcome | AIPD decision | Symphony action |
| :--- | :--- | :--- |
| Verifier passed, L1/L2 | `passed` | `release_to_review` |
| Verifier passed, L3 | `passed` | `close_mb` |
| Verifier failed, retry allowed | `implementation_bug` or `quality_evidence_gap` routed to `builder` | `schedule_semantic_retry` |
| Verifier failed, retry limit reached | owning issue type | `stop_and_route_recovery` |
| Scope violation | `state_drift` or protocol violation routed to `recovery_coordinator` | `stop_and_route_recovery` |
| Builder reports `spec_gap` | `spec_gap` routed to `spec_architect` | `stop_and_route_owner` |
| Builder reports `state_drift` | `state_drift` routed to `recovery_coordinator` | `stop_and_route_recovery` |
| Environment failure | `environment_issue` | transient: `defer_retry`; durable: `stop_and_route_recovery` |
| Review context missing | `review_context_gap` | `pause_wait_human` or `stop_and_route_owner` |

## MB Concurrency Contract

Future machine spec fields or derived metadata:

```text
concurrency_group
exclusive_touch
shared_read_artifacts
shared_write_artifacts
blocked_by_mbs
can_run_parallel
parallel_safe_reason
```

Hard rules:

- same `mb_id` must never run concurrently
- same `concurrency_group` defaults to mutually exclusive
- overlapping `exclusive_touch` must not run concurrently
- overlapping `shared_write_artifacts` must not run concurrently
- MBs with unresolved `blocked_by_mbs` must not dispatch
- MBs without `can_run_parallel: yes` default to not parallel-safe
- review, recovery, and spec update MBs default to exclusive execution

Suggested locks:

```text
runtime/locks/mb/<mb_id>.lock
runtime/locks/concurrency_group/<group>.lock
runtime/locks/touch/<hash>.lock
runtime/locks/artifact/<hash>.lock
```

Locks must be acquired before Codex starts and released only through a validated
gate outcome or explicit recovery cleanup.

## Direct MB Scheduling

Final target: Symphony should schedule AIPD MBs directly, not Linear issues that
contain MB IDs.

Design target:

```text
tracker.kind = aipd_mb
```

Normalized Symphony task mapping:

| Symphony field | AIPD source |
| :--- | :--- |
| `id` | `mb_id` |
| `identifier` | `mb_id` |
| `title` | MB goal |
| `description` | AIPD generated prompt summary or MB summary |
| `state` | mapped from `runtime/state/<mb_id>.state.json` |
| `priority` | FB/MB priority |
| `blocked_by` | `blocked_by_mbs` |

Adapter capabilities:

```text
fetch_candidate_mbs()
fetch_mbs_by_states(states)
fetch_mb_states_by_ids(ids)
claim_mb(mb_id)
release_mb(mb_id)
record_gate_outcome(mb_id, outcome)
```

## Implementation Phases

### Phase 0: Boundary Setup

- [x] Keep Symphony outside the AIPD repo.
- [x] Keep demo/runtime roots outside the AIPD repo.
- [x] Use this file as the local plan ledger.

### Phase 1: Download And Pin

- [x] Clone official Symphony upstream to external directory.
- [x] Record remote and commit.
- [x] Confirm AIPD repo remained clean.

### Phase 2: Static Security Audit

- [x] Inspect executable files.
- [x] Inspect workflow hooks.
- [x] Inspect Docker, SSH, GitHub, Linear, and Codex launch paths.
- [x] Record security conclusion.

### Phase 3: Local Test Audit

- [x] Install toolchain with `mise`.
- [x] Download Hex dependencies.
- [x] Run local tests.
- [x] Record flaky timing failures.
- [x] Avoid live e2e, Docker, Linear, SSH worker, and real Codex execution.

### Phase 4: AIPD Contract Design

- [x] Add `schemas/aipd-gate-outcome.schema.json`.
- [x] Add gate outcome examples for start pass, start reject, finish pass, finish retry, finish recovery.
- [x] Add validation helper or guard check for the gate outcome schema.
- [x] Add protocol text requiring Symphony to fail closed on invalid gate outcomes.

Phase 4 completion evidence:

- schema: `schemas/aipd-gate-outcome.schema.json`
- examples: `schemas/examples/aipd-gate-outcome/*.json`
- guard command: `python3 scripts/sdd_guard.py check-gate-outcome <path>`
- protocol rule: `docs/00_lifecycle.md` AIPD Gate Outcome Rule
- validation: `PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/sdd_guard.py`
- validation: `python3 scripts/sdd_guard.py check-protocol`
- validation: `python3 -m unittest tests.test_harness -v`

### Phase 5: Attempt Gate Extraction

- [x] Split current `mb_runner.py` logic into conceptual `attempt_start` and `attempt_finish` units.
- [x] Keep current `mb_runner.py` behavior stable during extraction.
- [x] Add tests for start rejected, finish passed, finish retry, and finish recovery.

Phase 5 completion evidence:

- runner boundaries: `scripts/mb_runner.py` `attempt_start()` and `attempt_finish()`
- start pass evidence: per-attempt `attempt_start_gate_outcome.json`
- start reject evidence: `runtime/gate_outcomes/<mb_id>/attempt_start.json`
- finish evidence: per-attempt `attempt_finish_gate_outcome.json`
- regression coverage: `tests/test_harness.py` validates start reject, finish pass, finish retry, and finish recovery gate outcomes
- validation: `PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/mb_runner.py scripts/sdd_guard.py`
- validation: `python3 scripts/sdd_guard.py check-protocol`
- validation: `python3 -m unittest tests.test_harness -v`

### Phase 6: Concurrency Contract

- [x] Extend or derive MB concurrency metadata.
- [x] Add lock acquisition and release rules.
- [x] Add tests for same MB lock, touch overlap, shared artifact overlap, and dependency blocking.

Phase 6 completion evidence:

- schema: `schemas/mb_machine_spec.schema.json` optional `concurrency` object
- protocol rule: `docs/03_mission_blocks.md` MB Concurrency Contract
- runner locks: `scripts/mb_runner.py` derives lock paths from same MB, `concurrency_group`, `exclusive_touch`, and `shared_write_artifacts`
- runner dependency block: `blocked_by_mbs` blocks `attempt_start` until dependencies have passed runtime state
- lock release: acquired locks are released after `attempt_finish` or pre-execution block
- regression coverage: `tests/test_harness.py` covers same MB lock, exclusive touch overlap, shared write artifact overlap, dependency blocking, and successful lock release
- validation: `PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/mb_runner.py scripts/sdd_guard.py`
- validation: `python3 scripts/sdd_guard.py check-protocol`
- validation: `python3 -m unittest tests.test_harness -v`

### Phase 7: Symphony MB Adapter Design

- [x] Design `tracker.kind: aipd_mb`.
- [x] Define MB state mapping.
- [x] Define claim/release semantics.
- [x] Define dashboard fields for MB status and gate evidence.

Phase 7 completion evidence:

- adapter contract: `docs/09_symphony_mb_adapter_contract.md`
- adapter identity: `tracker.kind = aipd_mb`
- state mapping: AIPD runtime states to Symphony task states
- claim semantics: claim requires validated `attempt_start` gate outcome
- release semantics: release applies only validated `attempt_finish` gate outcome actions
- dashboard fields: MB status, gate decision, Symphony instruction, evidence refs, state ref, and verification digest
- validation: `python3 scripts/sdd_guard.py check-protocol`

### Phase 8: Symphony Fork Runtime Integration

- [x] Create or select external Symphony fork.
- [x] Add AIPD MB tracker adapter.
- [x] Add AIPD gate outcome validator.
- [x] Add runner guard before Codex start.
- [x] Add finish gate after Codex turn.
- [x] Add outcome handler that accepts only known actions.

Phase 8 completion evidence:

- bundled runtime target: `/Users/lihaozheng/Documents/AI/Product-Dev/runtime/symphony`
- original fork source: `/Users/lihaozheng/Documents/AI/external/aipd-symphony-fork`
- source: cloned from `/Users/lihaozheng/Documents/AI/external/openai-symphony`
- adapter: `/Users/lihaozheng/Documents/AI/Product-Dev/runtime/symphony/elixir/lib/symphony_elixir/aipd/adapter.ex`
- gate validator: `/Users/lihaozheng/Documents/AI/Product-Dev/runtime/symphony/elixir/lib/symphony_elixir/aipd/gate_outcome.ex`
- tracker routing: `tracker.kind = aipd_mb` routes through `SymphonyElixir.Tracker`
- runner guard: `AgentRunner` calls AIPD `claim_issue` before workspace creation or Codex start
- finish gate: `AgentRunner` validates AIPD finish outcome after Codex turn completion
- outcome handler: unknown actions and unsafe `may_start_codex` combinations fail closed
- validation: `mise exec -- mix format --check-formatted`
- validation: `mise exec -- mix test test/symphony_elixir/aipd_adapter_test.exs`
- validation: `mise exec -- mix test --max-cases 1`

### Phase 9: External Demo Validation

- [x] Create external demo root.
- [x] Run one MB direct success path.
- [x] Run verification failure and semantic retry path.
- [x] Run start rejection path.
- [x] Run scope violation to recovery path.
- [x] Run concurrency conflict path.

Phase 9 completion evidence:

- demo root: `/Users/lihaozheng/Documents/AI/aipd-symphony-demo-roots/2026-04-25-phase9`
- direct success: `success` root, `fb1-mb1`, finish action `release_to_review`
- semantic retry: `semantic_retry` root, `fb1-mb3`, first finish action `schedule_semantic_retry`, second finish action `release_to_review`
- start rejection: `start_rejection` root, `fb1-mb7`, start action `pause_wait_human`, no attempt directory created
- scope violation: `scope_violation` root, `fb1-mb2`, finish action `stop_and_route_recovery`
- concurrency conflict: `concurrency_conflict` root, `fb1-mb1`, start action `defer_retry`, no attempt directory created
- validation: `python3 scripts/sdd_guard.py check-gate-outcome <demo gate outcome>`

## Test Requirements Before Real Use

Required tests:

- [x] `attempt_start` rejected means Codex is never started.
- [x] `spec_gap` routes to `Spec Architect` and is not Symphony runtime retried.
- [x] `state_drift` routes to `Recovery Coordinator`.
- [x] malformed gate outcome fails closed.
- [x] unknown Symphony action fails closed.
- [x] lock conflict defers without launching Codex.
- [x] same `mb_id` cannot run concurrently.
- [x] overlapping `exclusive_touch` cannot run concurrently.
- [x] `verification_failed` semantic retry prompt includes digest, failure reason, and retry count.
- [x] `scope_violation` routes to recovery.
- [x] passed L1/L2 routes to review.
- [x] passed L3 can close automatically only when explicitly allowed.

## Open Risks

- Upstream Symphony is an engineering preview/prototype, not a hardened runtime.
- Current local test suite has flaky timing assertions around retry/backoff.
- `WORKFLOW.md` hooks are arbitrary shell and must not become AIPD semantic gates.
- Current Symphony is Linear-oriented; direct MB scheduling requires an adapter.
- Remote SSH/Docker worker features are powerful and should stay disabled until explicitly needed.
- Homebrew auto-update reported a third-party tap issue during `mise` installation; this is outside
  Symphony and AIPD but should be cleaned separately if it affects future tooling.

## Update Rule

At the start and end of every future Symphony integration task:

1. Re-open this file.
2. Identify the active phase and task.
3. Update checklist status when work is completed, blocked, split, or superseded.
4. Record validation evidence in this file or in a linked artifact.
5. Do not mark a task complete without a concrete file, schema, test, or command result.

## Single-Repo Delivery Note

The earlier integration design assumed an external AIPD-specific Symphony fork.
The current delivery target is now:

- one public AIPD repository
- bundled runtime at `runtime/symphony`
- bootstrap entrypoints under `bootstrap/`
- external `PROJECT_ROOT` per real product

This changes installation and distribution, but it does not change the semantic
boundary between AIPD decision authority and Symphony execution authority.
