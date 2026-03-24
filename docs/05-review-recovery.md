# Review And Recovery

## Review Standard

Reviews must be evidence-based.

The reviewer should verify:

- function block alignment
- FB ontology frame alignment
- FB impact map coverage alignment
- active MB inheritance-slice compliance
- mission block scope compliance
- required quality checks
- data or API contract drift
- hidden risk introduced by the task

The reviewer must classify every finding by ownership instead of using vague fallback.

---

## Issue Routing By Ownership

Use the same routing rule in review, recovery, builder execution, and preflight.

| Issue Type | Meaning | Route To |
| :--- | :--- | :--- |
| `spec_gap` | Goal, scope, acceptance, or contract is unclear, missing, or contradictory | `Spec Architect` |
| `implementation_bug` | The written artifacts are clear, but the code does not match them | `Builder` |
| `quality_evidence_gap` | Required checks, evidence, or report fields are missing | `Builder` |
| `state_drift` | `SESSION_STATE`, active `FB/MB`, or file references do not match reality | `Recovery Coordinator` |
| `environment_issue` | Environment, dependency, or runtime state blocks safe progress | `Recovery Coordinator` |
| `review_context_gap` | The current actor lacks enough context to safely decide | current scene lead role |

The `Reviewer` does not fix problems.

The `Reviewer` must:

1. classify the issue
2. point to the correct owner
3. require the next action in the quality report

---

## Quality Report Output

Use a structured format so the result can later be automated.

Store review files under `<PROJECT_ROOT>/reviews/` and validate them against `schemas/quality-report.schema.json`.

```json
{
  "fb_id": "fb2",
  "mb_id": "fb2-mb3",
  "quality_profile": "standard",
  "result": "pass",
  "risk_level": "low",
  "baseline_summary": "Short machine-readable baseline summary",
  "changed_files": ["src/example.ts"],
  "scope_respected": true,
  "checks": {
    "scope_boundary": {
      "required": true,
      "status": "pass",
      "evidence": "changed files remained in scope",
      "note": ""
    },
    "fb_ontology_alignment": {
      "required": true,
      "status": "pass",
      "evidence": "implementation still matched the parent FB ontology frame",
      "note": ""
    },
    "layer_coverage_alignment": {
      "required": true,
      "status": "pass",
      "evidence": "affected layers in the FB were covered or explicitly deferred",
      "note": ""
    }
  },
  "regression_found": false,
  "open_risks": [],
  "lessons": [],
  "required_actions": [],
  "manual_review_required": false
}
```

If the review fails, `required_actions` should make the ownership explicit.

Examples:

- `Spec Architect: clarify acceptance for fb2 before the next MB`
- `Builder: add missing regression coverage for fb2-mb3`
- `Recovery Coordinator: repair session state reference to active_mission_block`

---

## Recovery Rule

When the project enters a confused or broken state, do not continue coding by instinct.

Run recovery in this order:

1. identify the active function block and mission block
2. identify the last known good checkpoint
3. classify the failure:
   `spec_gap`, `implementation_bug`, `quality_evidence_gap`, `environment_issue`, `state_drift`, or `review_context_gap`
4. route the failure to the owning role
5. choose the smallest safe move
6. update `SESSION_STATE.md` before any new implementation begins

---

## Three-Strike Rule

If the same implementation attempt fails repeatedly, stop escalation by habit.

Suggested policy:

- after 2 similar failures, require a written hypothesis
- after 3 similar failures, stop implementation and return to `DISCOVERY`, `SPEC`, or `RECOVERY`

The point is not the number. The point is to stop blind retries.

---

## 中文翻译

### 审查标准

审查必须以证据为基础。

Reviewer 应该核查：

- 是否符合 function block 的目标
- 是否符合父 FB 的本体框架
- 是否覆盖了父 FB 声明受影响的工程层
- 是否遵守当前 MB 声明的继承切片
- 是否遵守 mission block 的范围
- 是否完成必需的质量检查
- 是否出现数据或 API 契约漂移
- 任务是否引入了隐藏风险

Reviewer 不得用模糊的“退回上一步”来描述问题。

### 按责任归因的问题路由

在 review、recovery、builder 执行和 preflight 中，统一使用同一套问题路由规则。

| 问题类型 | 含义 | 路由到 |
| :--- | :--- | :--- |
| `spec_gap` | 目标、范围、验收或契约不清晰、缺失或互相矛盾 | `Spec Architect` |
| `implementation_bug` | 书面工件清楚，但代码实现不符合要求 | `Builder` |
| `quality_evidence_gap` | 缺少必需检查、证据或报告字段 | `Builder` |
| `state_drift` | `SESSION_STATE`、当前 `FB/MB` 或文件引用与现实不一致 | `Recovery Coordinator` |
| `environment_issue` | 环境、依赖或运行状态阻碍安全推进 | `Recovery Coordinator` |
| `review_context_gap` | 当前执行者缺少足够上下文，无法做安全判断 | 当前场景主导角色 |

`Reviewer` 不负责修复问题。

`Reviewer` 必须：

1. 先分类问题
2. 指向正确责任角色
3. 在质量报告中写出后续必需动作

### 质量报告输出

审查结果应使用结构化格式，方便后续自动化。

审查文件应该存放在 `<PROJECT_ROOT>/reviews/` 下，并用 `schemas/quality-report.schema.json` 校验。

上面的 JSON 示例表示：

- `fb_id`：所属 function block
- `mb_id`：所属 mission block
- `quality_profile`：质量档位
- `result`：结果
- `risk_level`：整体风险等级
- `baseline_summary`：简短、机器可读的基线摘要
- `checks`：本次 MB 实际要求的检查项及结果
- `required_actions`：如果失败，必须执行的动作
- `manual_review_required`：是否还需要人工进一步审查

如果审查失败，`required_actions` 应显式写出责任归属。

例如：

- `Spec Architect: 在下一个 MB 之前澄清 fb2 的验收标准`
- `Builder: 为 fb2-mb3 补齐缺失的回归覆盖`
- `Recovery Coordinator: 修复 active_mission_block 的 session state 引用`

### 恢复规则

当项目进入混乱或损坏状态时，不要凭直觉继续写代码。

恢复流程按下面顺序执行：

1. 找到当前激活的 function block 和 mission block
2. 找到最近一个已知良好的检查点
3. 对失败分类：`spec_gap`、`implementation_bug`、`quality_evidence_gap`、`environment_issue`、`state_drift` 或 `review_context_gap`
4. 把失败路由给对应责任角色
5. 选择最小的安全动作
6. 在开始新的实现前先更新 `SESSION_STATE.md`

### 三振规则

如果同类实现尝试反复失败，不要靠习惯性升级重试。

建议策略：

- 连续 2 次类似失败后，必须写出明确假设
- 连续 3 次类似失败后，停止实现，返回 `DISCOVERY`、`SPEC` 或 `RECOVERY`

重点不在具体次数，而在于停止盲目重试。
