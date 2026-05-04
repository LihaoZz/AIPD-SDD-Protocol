### 审查标准

审查必须以证据为基础。

Reviewer 应该核查：

- 是否符合 function block 的目标
- 是否符合父 FB 的本体框架
- 是否覆盖了父 FB 声明受影响的工程层
- 是否遵守当前 MB 声明的继承切片
- 是否遵守 mission block 的范围
- 当当前 `MB` 采纳了外部事实时，所需 research 工件是否存在
- 当当前 `MB` 依赖交接上下文时，所需 external prompt 工件是否存在
- 当父 FB 的体验层不是由 Builder 直接交付时，是否正确对齐外部 UI 包
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
- `experience_input_alignment`：当相关时，检查批准的外部 UI 输入是否被正确消费
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

如果失败是由缺失的外部 UI 包导致的，不要让 Builder 靠临场设计去补位。应把缺失输入记录清楚、把 handoff 路由给正确责任方，并把下一步动作写明确。

如果失败是由当前 `MB` 依赖的 research note 或 experience prompt 工件缺失导致的，也不要让 Builder 靠聊天记忆去补契约。应把它视为缺失执行上下文并正确路由。

### 三振规则

如果同类实现尝试反复失败，不要靠习惯性升级重试。

建议策略：

- 连续 2 次类似失败后，必须写出明确假设
- 连续 3 次类似失败后，停止实现，返回 `DISCOVERY`、`SPEC` 或 `RECOVERY`

重点不在具体次数，而在于停止盲目重试。
