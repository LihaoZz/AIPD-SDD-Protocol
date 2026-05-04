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

provider routing policy 仍然由 AIPD 持有。MB machine spec 可以定义 provider
policy，但 Symphony 只能消费 AIPD 为当前 attempt 选出的具体 provider。

### Claim 语义

Claim 一个 MB，意思是向 AIPD 请求 `attempt_start` gate outcome。

Adapter 必须：

1. 运行或请求 AIPD `attempt_start` gate
2. 用 `schemas/aipd-gate-outcome.schema.json` 校验返回结果
3. 只有当 `symphony_instruction.action` 为 `dispatch_agent` 或兼容旧值 `dispatch_codex` 时才启动执行 provider
4. 只有当 `symphony_instruction.may_start_agent == true` 时才启动执行 provider
5. 当 action 为 `dispatch_agent` 时，必须要求 `symphony_instruction.execution_provider`
6. 其他情况按返回 action 处理，不得自行推断另一条路由

具体 provider 必须由 AIPD 在 `attempt_start` 阶段决定。Symphony 不得自行增加
难度判断、fallback heuristic 或基于 retry 的 provider 切换。

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
- `symphony_instruction.execution_provider`
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
- `may_start_agent` 为 true，但 `action` 既不是 `dispatch_agent` 也不是兼容旧值 `dispatch_codex`
- `dispatch_agent` 已出现，但 `execution_provider` 缺失或非法
- action 未知
- 必需 evidence refs 缺失
- AIPD state 和 adapter state 不一致
