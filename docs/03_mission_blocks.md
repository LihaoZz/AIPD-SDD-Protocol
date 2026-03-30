# Function Blocks And Mission Blocks

## Why The Split Exists

Product work and code change work are not the same unit.

- a `Function Block` (`FB`) represents one product-facing delivery unit
- a `Mission Block` (`MB`) represents one bounded code change attempt under one active FB

This split keeps product context stable while letting implementation move in small, auditable steps.

## Function Blocks

An `FB` should answer:

- what user value is being delivered
- who the actor is
- what goal the actor is trying to complete
- what entities, relations, states, events, and rules define this function
- what evidence proves the function is real
- which engineering layers are affected
- what the acceptance definition is
- what is out of scope
- how the experience layer is delivered when it is affected

The `FB` main body should stay focused on:

- metadata
- product goal
- ontology frame
- impact map
- experience delivery
- scope
- acceptance
- mission plan

If the mode is `external_ui_package` or `hybrid`, the `FB` must also name:

- the required external input artifacts
- the Builder's allowed integration scope

Low-frequency details belong in `Optional Appendix`, not in the main body.

## Mission Blocks

An `MB` should answer:

- what exact code change is being attempted
- which FB it belongs to
- which slice of the parent FB acceptance it advances
- which ontology elements from the parent FB are in scope now
- which affected engineering layers from the parent FB are in scope now
- which ontology elements or layers are explicitly deferred
- which files may be modified
- which quality checks must pass
- what evidence is required
- what happened after execution

The `MB` main body should stay focused on:

- metadata
- parent FB alignment
- goal
- inputs
- boundaries
- quality plan
- evidence required
- result

Conditional rule:

- use `input_artifacts: none` when there is no upstream input dependency
- require `input_ready_check` only when real upstream inputs exist

Low-frequency details belong in `Optional Appendix`, not in the main body.

## External UI Input Rule

Some experience work may be delivered outside the Builder workflow.

In that case:

- the `FB` still owns the product definition
- the external UI package becomes an input to later `MB`s
- a dependent `MB` becomes an integration slice, not a visual redesign task

Authority rule:

- `FB` defines what the function is
- `MB` defines what this bounded implementation slice must do
- the external UI package defines only how the approved experience should be presented
- the external UI package does not override `FB` ontology, `MB` scope, `acceptance_slice`, business rules, or quality gates

Dependency rule:

- only an `MB` that explicitly declares the UI package in `input_artifacts` should wait for that input
- other `MB`s must not be blocked just because the parent `FB` has an external UI package

The Builder should consume the approved input, then connect:

- states
- routing
- validation
- API calls
- the smallest necessary structural adjustments

## Naming Rule

Use compact IDs that make the hierarchy obvious.

Examples:

- `fb2`
- `fb2-mb1`
- `fb2-mb2`
- `fb7-mb3`

## Quality Rule

An `MB` must not invent its own quality standards.

Every `MB` must:

- select checks from `QUALITY_RULEBOOK.md`
- declare which ontology elements and layers from the parent FB are in scope
- list required upstream inputs when they exist
- produce a quality report
- update `SESSION_STATE.md`

If a needed quality rule does not exist yet, stop and request a rulebook update instead of improvising.

## Completion Rule

An `MB` is not complete when the Builder says "done".

It is complete only when all required evidence exists:

- code changes
- required quality checks and results
- required external inputs were consumed when relevant
- the quality report
- scope remained within the allowed boundary
- session state was updated

## 中文翻译

### 为什么要拆成 FB 和 MB

产品交付单元和代码改动单元不是同一种东西。

- `Function Block` (`FB`) 表示一个面向产品交付的单元
- `Mission Block` (`MB`) 表示该 FB 下的一次有边界代码改动尝试

这样拆分后，产品上下文稳定，实现过程可以小步、可审计地推进。

### Function Block

`FB` 要回答：

- 交付什么用户价值
- 谁是 actor
- actor 想完成什么 goal
- 哪些 entity、relation、state、event、rule 定义这个功能
- 什么 evidence 证明这个功能真实成立
- 哪些工程层受影响
- 验收定义是什么
- 什么不在范围内
- 当体验层受影响时，它由谁交付

`FB` 主体应聚焦于：

- 元信息
- 产品目标
- 本体框架
- 影响地图
- 体验交付
- 范围
- 验收
- mission 计划

如果模式是 `external_ui_package` 或 `hybrid`，还必须写明：

- 必需的外部输入工件
- Builder 允许负责的集成范围

低频信息应移入 `Optional Appendix`，不要挤占主体。

### Mission Block

`MB` 要回答：

- 这次具体改什么
- 属于哪个 FB
- 推进父 FB 的哪个验收切片
- 当前涉及哪些父 FB 本体元素
- 当前涉及哪些父 FB 工程层
- 哪些本体元素或工程层被延期
- 允许改哪些文件
- 哪些质量检查必须通过
- 需要什么证据
- 执行后结果是什么

`MB` 主体应聚焦于：

- 元信息
- 父 FB 对齐
- 目标
- 输入
- 边界
- 质量计划
- 必需证据
- 结果

条件规则：

- 没有上游输入依赖时，`input_artifacts` 固定写 `none`
- 只有存在真实输入依赖时，才要求 `input_ready_check`

低频信息应进入 `Optional Appendix`。

### 外部 UI 输入规则

有些体验层工作会在 Builder 工作流之外完成。

这种情况下：

- `FB` 仍然拥有产品定义
- 外部 UI 包会成为后续 `MB` 的输入
- 依赖它的 `MB` 是集成切片，而不是视觉重设计任务

权威规则：

- `FB` 定义这个功能是什么
- `MB` 定义这次有边界的实现切片必须做什么
- 外部 UI 包只定义批准体验应如何呈现
- 外部 UI 包不能覆盖 `FB` 本体、`MB` 边界、`acceptance_slice`、业务规则或质量门禁

依赖规则：

- 只有在 `input_artifacts` 中显式声明依赖该 UI 包的 `MB`，才应该等待这个输入
- 其他 `MB` 不能因为父 `FB` 存在外部 UI 包就被连带阻塞

Builder 负责消费批准输入，并连接：

- 状态
- 路由
- 校验
- API 调用
- 最小必要结构调整

### 命名规则

用一眼就能看出层级的紧凑 ID：

- `fb2`
- `fb2-mb1`
- `fb2-mb2`
- `fb7-mb3`

### 质量规则

`MB` 不得自行发明质量标准。

每个 `MB` 都必须：

- 从 `QUALITY_RULEBOOK.md` 选择检查项
- 声明当前涉及的父 FB 本体元素和工程层
- 在存在时列出必需上游输入
- 产出质量报告
- 更新 `SESSION_STATE.md`

如果规则手册里没有需要的质量规则，就停止并请求更新。

### 完成规则

`MB` 不是 Builder 说“做完了”就算完成。

只有在以下证据都存在时才算完成：

- 代码改动
- 必需质量检查及结果
- 在相关时已正确消费外部输入
- 质量报告
- 范围仍在允许边界内
- 已更新 session state
