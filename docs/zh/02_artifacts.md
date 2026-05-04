<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: docs/02_artifacts.md
Translation source: translations/zh/docs/02_artifacts.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

### Experience Prompt 规则

当 assistant 要为 Figma、Stitch 或其他可接收 prompt 的外部体验工具准备交接 prompt 时，应使用 `EXPERIENCE_PROMPT` 工件。

`EXPERIENCE_PROMPT` 至少要记录：

- 对应的父 `FB` 和相关 `MB`
- 如果属于共享页面族，则记录 `page_family_id`
- 用 `prompt_goal_type` 和 `consistency_mode` 说明这次 prompt 的结构目标和一致性要求
- 用 `family_source_refs` 指向既有页面族契约
- 已确认的视觉方向和设计核心
- 会显著影响输出质量的 UI 决策
- 当同页族一致性重要时，记录共享壳子契约，包括必须保持的部分、允许变化的部分、以及禁止漂移的部分
- 已采纳参考
- 页面或组件目标
- 必须覆盖的状态、分叉和流程
- 必做项、禁止项
- `prompt_requirements` 和 `tool_specific_notes`
- 期望回流的返回物
- 最终可直接复制给外部工具的 prompt 正文

不要把所有 prompt 都当成一种形状。应按任务选择策略：

- `canonical_shell`：首次定义某个页面族的壳子
- `state_variant`：保持同一壳子，补充不同状态
- `family_extension`：在同一页面族内做局部扩展
- `independent_screen`：没有共享壳子约束的独立页面

把 prompt 策略理解成两个轴：

- `prompt_goal_type`：这次 prompt 的结构目标是什么
- `tool_guidance_profile`：针对当前工具，prompt 应该怎么写

推荐的 `tool_guidance_profile`：

- `stitch_first_pass`：用于 Stitch 的首轮高细节单页或页面族壳子生成
- `stitch_iterative_refine`：用于 Stitch 的后续迭代，要求聚焦单页、边界清晰
- `figma_structured_handoff`：用于 Figma 的较完整、较结构化交接
- `general_structured_handoff`：其他工具下的保守兜底档位

当壳子和组件语言除明确例外外都应保持固定时，使用 `same_family_strict`。

当同一页面族仍需保持可识别，但局部区域允许明显变化时，使用 `same_family_adaptive`。

对于 Stitch，应优先使用大白话，并按 screen-by-screen 方式细化。同页族 prompt 必须明确要求保持共享壳子，不能指望工具自己推断出来。

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
- 在使用 research 时可选的 `research/*.md`
- 在使用外部体验 prompt 交接时可选的 `experience_prompts/*.md`
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

Research 工件也遵循同样的权威关系。

它们可以为决策、规格或实现备注提供事实输入，但不能替代：

1. 当前激活的 `FB`
2. 当前激活的 `MB`
3. `QUALITY_RULEBOOK.md`

如果 research 改变了产品真相、工具选择或实现方向，必须把采纳结果写回项目工件，而不是只停留在聊天里。

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

本轮新增的可选附录字段：

- `research_needed`
- `research_questions`
- `experience_prompt_needed`

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

如果当前切片需要 research，应当记录以下两种之一：

- 把已采纳的 research 结论写进当前 `MB`
- 或引用对应的 `RESEARCH_NOTE`

本轮新增的可选附录字段：

- `research_inputs`
- `external_tool_prompt_ref`

引用规则：

- `research_inputs` 应使用逗号分隔的相对路径，指向 `research/*.md`
- `external_tool_prompt_ref` 应指向 `experience_prompts/*.md` 下的单个相对路径

### Research Note 规则

当一次搜索产出了值得复用的事实、候选工具、UI 参考或技术结论，并且不应随着聊天结束而丢失时，应使用 `RESEARCH_NOTE`。

`RESEARCH_NOTE` 应至少记录：

- 触发类型
- 哪个角色拥有这次搜索
- 搜索问题以及为什么现在要查
- 收集到的来源与事实
- 考虑过的候选项
- 推荐结论
- 对当前 `FB` 或 `MB` 的影响
- 是否需要用户批准，以及批准状态

UI 相关 research 可以支持风格探索，但不能直接定最终视觉方向。

在生成任何 UI 外部工具 prompt 前，必须先由用户确认：

- 采纳哪些参考
- 最终视觉方向
- 设计核心

### Experience Prompt 规则

当 assistant 要为 Figma、Stitch 或其他接受 prompt 的外部体验工具生成交接 prompt 时，应使用 `EXPERIENCE_PROMPT` 工件。

`EXPERIENCE_PROMPT` 至少应记录：

- 父 `FB` 和相关 `MB`
- 已确认的视觉方向和设计核心
- 会显著影响生成质量的已确认 UI 决策
- 已采纳的参考集
- 页面或组件目标
- 必须覆盖的状态、分叉和流程
- 必做项与禁止项
- 供 intake 使用的期望返回物
- 最终可直接复制给外部工具的提示词正文

这个 prompt 工件属于真理源交接上下文，不能只停留在聊天里；如果只有方向说明、没有最终提示词正文，也不算完整。
