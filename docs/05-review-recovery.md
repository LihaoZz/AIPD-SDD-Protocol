# Review And Recovery

## Review Standard

Reviews must be evidence-based.

The reviewer should verify:

- contract alignment
- scope compliance
- test evidence
- data or API contract drift
- hidden risk introduced by the task

---

## Audit Output

Use a structured format so the result can later be automated.

Store review files under `<PROJECT_ROOT>/reviews/` and validate them against `schemas/audit-result.schema.json`.

```json
{
  "pass": true,
  "risk_level": "low",
  "summary": "Short machine-readable conclusion",
  "checks": {
    "contract_aligned": true,
    "scope_respected": true,
    "tests_verified": true,
    "artifact_drift": false
  },
  "findings": [
    {
      "type": "logic",
      "severity": "medium",
      "file": "src/example.ts",
      "line": 10,
      "description": "Description of the issue"
    }
  ],
  "required_actions": [
    "Fix the null handling branch in src/example.ts"
  ],
  "manual_review_required": false
}
```

---

## Recovery Rule

When the project enters a confused or broken state, do not continue coding by instinct.

Run recovery in this order:

1. identify the active mission block
2. identify the last known good checkpoint
3. classify the failure:
   `spec_gap`, `implementation_bug`, `test_gap`, `environment_issue`, or `state_drift`
4. choose the smallest safe move
5. update `SESSION_STATE.md` before any new implementation begins

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

- 是否符合契约
- 是否遵守范围
- 是否有测试证据
- 是否出现数据或 API 契约漂移
- 任务是否引入了隐藏风险

### 审查输出

审查结果应使用结构化格式，方便后续自动化。

审查文件应该存放在 `<PROJECT_ROOT>/reviews/` 下，并用 `schemas/audit-result.schema.json` 校验。

上面的 JSON 示例表示：

- `pass`：是否通过
- `risk_level`：整体风险等级
- `summary`：简短、机器可读的结论
- `checks`：对齐契约、范围、测试和工件漂移四项检查
- `findings`：具体问题列表
- `required_actions`：如果失败，必须执行的动作
- `manual_review_required`：是否还需要人工进一步审查

### 恢复规则

当项目进入混乱或损坏状态时，不要凭直觉继续写代码。

恢复流程按下面顺序执行：

1. 找到当前激活的 mission block
2. 找到最近一个已知良好的检查点
3. 对失败分类：`spec_gap`、`implementation_bug`、`test_gap`、`environment_issue` 或 `state_drift`
4. 选择最小的安全动作
5. 在开始新的实现前先更新 `SESSION_STATE.md`

### 三振规则

如果同类实现尝试反复失败，不要靠习惯性升级重试。

建议策略：

- 连续 2 次类似失败后，必须写出明确假设
- 连续 3 次类似失败后，停止实现，返回 `DISCOVERY`、`SPEC` 或 `RECOVERY`

重点不在具体次数，而在于停止盲目重试。
