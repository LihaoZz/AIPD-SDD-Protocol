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

### MB 并发契约

可由机器运行的 MB，可以在 machine spec 中声明可选的 `concurrency` 元数据。

支持字段：

- `concurrency_group`
- `exclusive_touch`
- `shared_read_artifacts`
- `shared_write_artifacts`
- `blocked_by_mbs`
- `can_run_parallel`
- `parallel_safe_reason`

执行规则：

- 同一个 `mb_id` 不得并发运行
- 未完成的 `blocked_by_mbs` 依赖会阻塞 `attempt_start`
- 已存在的 `concurrency_group` 锁会阻塞 `attempt_start`
- 重叠的 `exclusive_touch` 锁会阻塞 `attempt_start`
- 重叠的 `shared_write_artifacts` 锁会阻塞 `attempt_start`
- 锁冲突必须产出 action 为 `defer_retry` 的 start gate outcome
- 依赖冲突必须产出 action 为 `release_and_wait_input` 的 start gate outcome
- 任何锁冲突或依赖冲突都不得启动 Codex，也不得创建 attempt 目录
- 已获取的锁必须在 `attempt_finish` 后释放，或在执行前阻塞时释放

如果没有显式声明 `exclusive_touch`，runner 从 `allowed_touch` 派生。

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

### Research 支持规则

`Research` 可以支持 `FB` 规划或当前激活 `MB` 的执行，但它不会变成新的执行标准。

触发规则：

- `user_triggered` research 可以直接执行
- `system_triggered` research 在搜索开始前必须先得到用户同意

范围规则：

- `Spec Architect` 可以在规格阶段用 research 做市场扫描、工具发现、相似产品查看或外部参考收集
- `Builder` 只能为当前 `MB` 使用 research，例如解决有边界技术问题、查官方文档或参考成熟实现
- research 不能扩大当前 `MB` 的范围

记录规则：

- 可复用结果应写入 `DECISIONS.md`、当前 `FB`、当前 `MB` 或 `RESEARCH_NOTE`
- 采纳后的外部事实不能只停留在聊天记录里

### UI 参考与 Prompt 规则

UI 相关 research 可以提供：

- 风格参考
- 成熟模式
- 组件方向
- 渲染方案
- 相似产品视觉案例

这些 research 可以支持建议，但它们不能拥有最终设计定调权。

在生成任何 UI 外部工具 prompt 前：

- 必须由用户确认采纳哪些参考
- 必须由用户确认最终视觉方向
- 必须由用户确认设计核心
- 必须由用户确认决定生成质量的主要 UI 决策

确认后生成的外部工具 prompt，必须继续来源于：

- 父 `FB`
- 当前或计划中的 `MB`
- 已确认视觉方向
- 必须覆盖的状态和分叉
- 已经定下来的布局、密度、组件、颜色、排版、交互、动效、响应式和可访问性决策

这个 prompt 必须固化到 `experience_prompts/*.md`，并在工件中包含最终可直接复制的提示词正文，再由依赖它的集成 `MB` 通过 `external_tool_prompt_ref` 指向。

外部工具返回产物随后变成后续集成 `MB` 的 `input_artifact`。

如果这个 prompt 面向与更早或更晚工作共享的同一页面族，还必须额外写清：

- `page_family_id`
- 共享壳子的范围
- 哪些 family source refs 定义了这份契约
- 哪些部分在不同状态或同级 `MB` 中必须保持一致
- 哪些部分允许变化
- 禁止发生哪些 drift

同一页面族下的依赖 `MB`，应复用这份交接契约，而不是静默发明新的壳子。

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
