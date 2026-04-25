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

## Claim Semantics

Claiming an MB means asking AIPD for an `attempt_start` gate outcome.

The adapter must:

1. run or request the AIPD `attempt_start` gate
2. validate the returned gate outcome against `schemas/aipd-gate-outcome.schema.json`
3. start Codex only when `symphony_instruction.action == dispatch_codex`
4. start Codex only when `symphony_instruction.may_start_codex == true`
5. otherwise follow the returned action and never infer a different route

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
- `may_start_codex` is true but `action` is not `dispatch_codex`
- the action is unknown
- required evidence refs are missing
- AIPD state and adapter state disagree

## 中文翻译

### 说明

本文定义未来 Symphony tracker adapter 的 AIPD 侧契约。

这里不包含 Symphony runtime 代码。真正的 runtime 实现应放在外部 Symphony fork 或 adapter 工作区。

### Adapter 身份

Adapter 类型固定为：

```text
tracker.kind = aipd_mb
```

这个 adapter 会把 AIPD Mission Block 暴露成 Symphony 可以调度的任务。

### 任务映射

| Symphony 字段 | AIPD 来源 |
| :--- | :--- |
| `id` | `mb_id` |
| `identifier` | `mb_id` |
| `title` | machine spec 的 `goal` |
| `description` | 从 MB markdown 和 machine spec 生成的摘要 |
| `state` | 映射后的 runtime MB 状态 |
| `priority` | 当存在时，来自 FB 或 MB 的优先级元数据 |
| `blocked_by` | machine spec 的 `concurrency.blocked_by_mbs` |

Symphony 不得从 issue 文本里猜测缺失的 AIPD 字段。

### 状态映射

| AIPD runtime 状态 | Symphony 任务状态 |
| :--- | :--- |
| `ready` | `ready` |
| `running` | `in_progress` |
| `verifying` | `in_progress` |
| `failed` | `retry_waiting` |
| `blocked` | `blocked` |
| `routed_to_recovery` | `blocked` |
| `passed` 且需要 review | `review` |
| `passed` 且不需要 review | `done` |

权威状态来源是 `runtime/state/<mb_id>.state.json`。

### 候选任务读取

Adapter 只能从 AIPD 工件读取候选 MB：

- `missions/<mb_id>.md`
- `missions/<mb_id>.machine.json`
- `runtime/state/<mb_id>.state.json`

候选 MB 必须满足：

- mission markdown 有效
- machine spec 有效
- 状态不是终态，或还没有 runtime state
- 没有未解决的 `blocked_by_mbs` 依赖

### Claim 语义

Claim 一个 MB，意思是向 AIPD 请求 `attempt_start` gate outcome。

Adapter 必须：

1. 运行或请求 AIPD `attempt_start` gate
2. 用 `schemas/aipd-gate-outcome.schema.json` 校验返回结果
3. 只有当 `symphony_instruction.action == dispatch_codex` 时才启动 Codex
4. 只有当 `symphony_instruction.may_start_codex == true` 时才启动 Codex
5. 其他情况按返回 action 处理，不得自行推断另一条路由

Claim 不会把语义权威转移给 Symphony。

### Release 语义

Release 一个 MB，意思是应用一个已校验的 `attempt_finish` gate outcome。

Adapter 只接受以下 action：

- `defer_retry`
- `schedule_semantic_retry`
- `release_and_pause`
- `release_and_wait_input`
- `pause_wait_human`
- `release_to_review`
- `close_mb`
- `stop_and_route_owner`
- `stop_and_route_recovery`

未知 action 必须 fail closed。

Adapter 不得只根据进程退出码决定 retry、review、recovery 或 close。

### 证据记录

每个 adapter 可见的状态迁移，都必须保留 AIPD gate outcome 中的 evidence refs。

Dashboard 最少字段：

- `mb_id`
- `parent_fb_id`
- `runtime_state`
- `current_attempt_id`
- `aipd_decision.status`
- `aipd_decision.issue_type`
- `aipd_decision.route_to`
- `symphony_instruction.action`
- `symphony_instruction.retryable`
- `evidence_refs`
- `state_ref`
- `last_verification_digest`

Dashboard 行只是观察层，不能覆盖 AIPD state 文件。

### Fail-Closed 规则

以下情况 Symphony 必须在启动 Codex 前停止：

- gate outcome 文件缺失
- gate outcome 格式错误
- gate outcome 未通过 schema 校验
- `may_start_codex` 为 true，但 `action` 不是 `dispatch_codex`
- action 未知
- 必需 evidence refs 缺失
- AIPD state 和 adapter state 不一致
