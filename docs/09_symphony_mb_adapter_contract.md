# Symphony MB Adapter Contract

This document defines the AIPD-side contract for a future Symphony tracker
adapter.

It does not contain Symphony runtime code. Runtime implementation belongs in an
external Symphony fork or adapter workspace.

## Adapter Identity

The adapter kind is:

```text
tracker.kind = aipd_mb
```

The adapter exposes AIPD Mission Blocks as schedulable Symphony tasks.

## Task Mapping

| Symphony Field | AIPD Source |
| :--- | :--- |
| `id` | `mb_id` |
| `identifier` | `mb_id` |
| `title` | machine spec `goal` |
| `description` | generated summary from MB markdown and machine spec |
| `state` | mapped runtime MB state |
| `priority` | optional FB or MB priority metadata when present |
| `blocked_by` | machine spec `concurrency.blocked_by_mbs` |

Symphony must not infer missing AIPD fields from issue text.

## State Mapping

| AIPD Runtime State | Symphony Task State |
| :--- | :--- |
| `ready` | `ready` |
| `running` | `in_progress` |
| `verifying` | `in_progress` |
| `failed` | `retry_waiting` |
| `blocked` | `blocked` |
| `routed_to_recovery` | `blocked` |
| `passed` with review required | `review` |
| `passed` without review required | `done` |

The authoritative state source is `runtime/state/<mb_id>.state.json`.

## Candidate Fetch

The adapter may fetch candidate MBs only from AIPD artifacts:

- `missions/<mb_id>.md`
- `missions/<mb_id>.machine.json`
- `runtime/state/<mb_id>.state.json`

Candidate MBs must have:

- a valid mission markdown file
- a valid machine spec
- a non-terminal state, or no runtime state yet
- no unresolved `blocked_by_mbs` dependency

Provider routing policy remains AIPD-owned. MB machine specs may define a
provider policy, but Symphony must consume only the concrete provider selected
by AIPD for the current attempt.

## Claim Semantics

Claiming an MB means asking AIPD for an `attempt_start` gate outcome.

The adapter must:

1. run or request the AIPD `attempt_start` gate
2. validate the returned gate outcome against `schemas/aipd-gate-outcome.schema.json`
3. start an execution provider only when `symphony_instruction.action` is `dispatch_agent` or legacy `dispatch_codex`
4. start the execution provider only when `symphony_instruction.may_start_agent == true`
5. when `dispatch_agent` is used, require `symphony_instruction.execution_provider`
6. otherwise follow the returned action and never infer a different route

AIPD decides the concrete provider at `attempt_start`. Symphony must not add its
own difficulty heuristic, fallback heuristic, or retry-based provider switch.

Claiming does not transfer semantic authority to Symphony.

## Release Semantics

Releasing an MB means applying a validated `attempt_finish` gate outcome.

The adapter must accept only these actions:

- `defer_retry`
- `schedule_semantic_retry`
- `release_and_pause`
- `release_and_wait_input`
- `pause_wait_human`
- `release_to_review`
- `close_mb`
- `stop_and_route_owner`
- `stop_and_route_recovery`

Unknown actions fail closed.

The adapter must not use process exit alone to decide retry, review, recovery,
or closure.

## Evidence Recording

Every adapter-visible state transition must retain evidence refs from the AIPD
gate outcome.

Minimum dashboard fields:

- `mb_id`
- `parent_fb_id`
- `runtime_state`
- `current_attempt_id`
- `aipd_decision.status`
- `aipd_decision.issue_type`
- `aipd_decision.route_to`
- `symphony_instruction.action`
- `symphony_instruction.execution_provider`
- `symphony_instruction.retryable`
- `evidence_refs`
- `state_ref`
- `last_verification_digest`

Dashboard rows are observational only. They do not override AIPD state files.

## Fail-Closed Rules

Symphony must stop before Codex launch when:

- the gate outcome file is missing
- the gate outcome is malformed
- the gate outcome fails schema validation
- `may_start_agent` is true but `action` is neither `dispatch_agent` nor legacy `dispatch_codex`
- `dispatch_agent` is present but `execution_provider` is missing or unknown
- the action is unknown
- required evidence refs are missing
- AIPD state and adapter state disagree
