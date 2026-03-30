# Source Of Truth Artifacts

## Artifact Set

Each project should maintain the following files.

| Artifact | Purpose | Owner | Required |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | Product intent, architecture boundaries, stack choices, and non-negotiables | Spec Architect | Yes |
| `<PROJECT_ROOT>/SCOPE.md` | Current user-facing scope and acceptance definition | Spec Architect | Yes |
| `<PROJECT_ROOT>/DECISIONS.md` | Important decisions and why alternatives were rejected | Spec Architect | Yes |
| `<PROJECT_ROOT>/SESSION_STATE.md` | Current stage, current FB, current MB, latest blocker, and next action | Builder updates under protocol | Yes |
| `<PROJECT_ROOT>/QUALITY_RULEBOOK.md` | Global quality profiles, checks, and waiver policy | Spec Architect | Yes |
| `<PROJECT_ROOT>/QUALITY_MEMORY.md` | Reusable lessons, repeated failures, and high-risk reminders | Builder and Reviewer | Yes |
| `<PROJECT_ROOT>/DATA_MODEL.md` | Core entities, relationships, and persistence rules | Spec Architect | Usually |
| `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml` | API behavior and payload rules | Spec Architect | If APIs exist |
| `<PROJECT_ROOT>/VERSION_LOG.md` | Important checkpoints and rollback references | Builder | Recommended |
| `<PROJECT_ROOT>/function_blocks/*.md` | Product-level delivery units with ontology frame, impact map, acceptance, and MB plan | Spec Architect | Yes before scene planning finishes |
| `<PROJECT_ROOT>/missions/*.md` | Bounded code change units under one active FB | Spec Architect or Builder | Yes before `BUILD` |
| `<PROJECT_ROOT>/reviews/*.json` | Evidence-based quality reports that match the quality report schema | Reviewer | Yes before `CLOSE` |

## Ownership Rule

The Builder may read all source-of-truth artifacts.

The Builder may not freely rewrite them during implementation. If implementation reveals a mismatch, the Builder must raise a spec conflict instead of silently changing the contract.

Allowed cases for artifact changes:

- the active FB or MB explicitly authorizes the update
- the session is in `SPEC`
- the session is in `recovery` and the recovery plan requires documentation repair
- the session writes a lesson into `QUALITY_MEMORY.md`

When an `FB` uses `external_ui_package` or `hybrid`, the external UI package itself may live outside the standard protocol files, but the authoritative references to that package must be recorded in the parent `FB`, dependent `MB`s, and `SESSION_STATE.md` when relevant.

That external UI package is an implementation input, not a replacement for protocol truth.

The authority order remains:

1. active `FB`
2. active `MB`
3. `QUALITY_RULEBOOK.md`
4. external UI package

The external UI package only governs experience presentation. It does not override ontology, task scope, acceptance, business rules, or quality gates.

## Session State Rule

`<PROJECT_ROOT>/SESSION_STATE.md` is the minimum restart file.

It should always answer:

- which mode the project is in
- which stage the work is in
- which function block is active
- which mission block is active
- what was completed
- what failed
- what the next single action is
- which artifacts must be read first

Without this file, every new conversation wastes time reconstructing context and may drift.

## FB, MB, And Quality Report Storage

Function blocks should live in `<PROJECT_ROOT>/function_blocks/`.

Mission blocks should live in `<PROJECT_ROOT>/missions/`.

Quality reports should live in `<PROJECT_ROOT>/reviews/`.

Each mission block should inherit from its parent FB instead of copying the full ontology frame.

## Function Block Content Rule

An `FB` is the product anchor, not a running log of every code attempt.

Its main body should contain:

- metadata
- product goal
- 8-element ontology frame
- 8-layer impact map
- `experience_delivery_mode`
- scope
- acceptance
- mission plan

Conditional fields:

- if `experience_delivery_mode` is `external_ui_package` or `hybrid`, include `experience_input_artifacts` and `experience_builder_scope`

Optional Appendix:

- dependencies
- related artifacts
- overall risk
- special quality concerns
- release blockers
- completed or failed MB history
- open questions

Use the appendix only when it materially improves execution clarity.

## Mission Block Content Rule

An `MB` is the smallest bounded implementation unit.

Its main body should contain:

- metadata
- parent FB alignment
- goal
- allowed files
- quality plan
- required evidence
- result

Conditional fields:

- `input_artifacts` only when upstream inputs are required; otherwise use `none`
- `input_ready_check` only when `input_artifacts` is not `none`

Optional Appendix:

- extra boundary notes
- baseline details
- rollback details
- waived checks
- change budget and risk notes

Keep the main body small enough that the Builder can execute it without hunting through low-value fields.

The `input_artifacts` field records execution dependencies only. It does not replace the parent `FB` or the active `MB` as the task authority.

## 中文翻译

### 真理源文件集合

每个项目都应该维护这些文件：

- `CONSTITUTION.md`
- `SCOPE.md`
- `DECISIONS.md`
- `SESSION_STATE.md`
- `QUALITY_RULEBOOK.md`
- `QUALITY_MEMORY.md`
- 需要时的 `DATA_MODEL.md`
- 需要时的 `API_CONTRACT.md` 或 `openapi.yaml`
- 推荐的 `VERSION_LOG.md`
- `function_blocks/*.md`
- `missions/*.md`
- `reviews/*.json`

它们都放在真实项目的 `PROJECT_ROOT` 下。

### 所有权规则

Builder 可以读取所有真理源文件，但不能在实现过程中随意改写。

如果实现暴露出不匹配，应该提出规格冲突，而不是静默改契约。

允许更新工件的情况只有：

- 当前 FB 或 MB 明确授权
- 当前处于 `SPEC`
- 当前处于 `recovery` 且恢复计划要求修正文档
- 当前需要把经验写入 `QUALITY_MEMORY.md`

如果 `FB` 使用 `external_ui_package` 或 `hybrid`，外部 UI 包本体可以放在协议文件之外，但对它的权威引用必须写进 `FB`、相关 `MB`，以及必要时的 `SESSION_STATE.md`。

这个外部 UI 包属于实现输入，不属于协议真相来源本身。

权威顺序保持为：

1. 当前激活的 `FB`
2. 当前激活的 `MB`
3. `QUALITY_RULEBOOK.md`
4. 外部 UI 包

外部 UI 包只负责体验效果呈现，不覆盖本体、任务边界、验收、业务规则和质量门禁。

### Session State 规则

`SESSION_STATE.md` 是最小可恢复文件。

它必须回答：

- 当前模式
- 当前阶段
- 当前 FB
- 当前 MB
- 已完成什么
- 已失败什么
- 下一个唯一动作
- 接手前必须先读哪些工件

### FB 内容规则

`FB` 的主体只保留高价值内容：

- 元信息
- 产品目标
- 8 元素本体框架
- 8 层影响地图
- `experience_delivery_mode`
- 范围
- 验收
- mission 计划

条件字段：

- 当 `experience_delivery_mode` 为 `external_ui_package` 或 `hybrid` 时，必须补 `experience_input_artifacts` 和 `experience_builder_scope`

可选附录 `Optional Appendix`：

- 依赖项
- 相关工件
- 整体风险
- 特殊质量关注点
- 发布阻塞项
- 已完成或失败的 MB 历史
- 未决问题

只有这些信息真的能帮助执行时，才放进附录。

### MB 内容规则

`MB` 是最小有边界实现单元。

主体应包含：

- 元信息
- 父 FB 对齐
- 目标
- 允许改动文件
- 质量计划
- 必需证据
- 结果

条件字段：

- 只有存在上游输入依赖时才写 `input_artifacts`，否则固定写 `none`
- 只有 `input_artifacts != none` 时才写 `input_ready_check`

可选附录 `Optional Appendix`：

- 额外边界说明
- 基线细节
- 回滚细节
- 豁免检查
- 改动预算和风险备注

主体必须小到让 Builder 不需要翻大量低价值字段也能执行。

`input_artifacts` 字段只记录执行依赖输入，不替代父 `FB` 或当前 `MB` 的任务权威。
