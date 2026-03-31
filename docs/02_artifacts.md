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
| `<PROJECT_ROOT>/research/*.md` | Structured research runs, external references, and approved recommendations | Spec Architect or Builder | Optional when research is used |
| `<PROJECT_ROOT>/experience_prompts/*.md` | Approved external-tool handoff prompts with confirmed visual direction and return contract | Spec Architect or Builder | Optional when external UI prompt handoff is used |
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

Research artifacts follow the same authority model.

They may inform decisions, specs, and implementation notes, but they do not replace:

1. active `FB`
2. active `MB`
3. `QUALITY_RULEBOOK.md`

If research changes product truth, tool choice, or implementation direction, record the adopted result in project artifacts rather than leaving it only in chat.

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

Optional Appendix additions:

- `research_needed`
- `research_questions`
- `experience_prompt_needed`

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

If research is needed for the active slice, record either:

- the adopted research result in the active `MB`
- or a reference to the relevant `RESEARCH_NOTE`

Optional Appendix additions:

- `research_inputs`
- `external_tool_prompt_ref`

Reference rule:

- `research_inputs` should list comma-separated relative paths to `research/*.md`
- `external_tool_prompt_ref` should point to one relative path under `experience_prompts/*.md`

## Research Note Rule

Use a `RESEARCH_NOTE` when a search run produces reusable facts, candidate tools, UI references, or technical guidance that should survive the chat session.

A `RESEARCH_NOTE` should capture:

- the trigger type
- the role that owns the search
- the query and why it is needed now
- the sources and facts collected
- the candidates considered
- the recommendation
- the impact on the current `FB` or `MB`
- whether user approval was required and whether it was granted

UI-related research may support style exploration, but it does not finalize visual direction.

Before any external-tool UI prompt is generated, the user must confirm:

- which references are adopted
- the final visual direction
- the design core

## Experience Prompt Rule

Use an `EXPERIENCE_PROMPT` artifact when the assistant prepares a handoff prompt for Figma, Stitch, or another prompt-driven external experience tool.

An `EXPERIENCE_PROMPT` should capture:

- the parent `FB` and related `MB`s
- the `page_family_id` when the prompt belongs to a shared page family
- the `prompt_goal_type` and `consistency_mode` that explain what this prompt is trying to do
- any `family_source_refs` that define the existing family contract
- the confirmed visual direction and design core
- the confirmed UI decisions that materially affect output quality
- the shared shell contract when same-family consistency matters, including what must be preserved, what may vary, and what drift is forbidden
- the approved reference set
- the page or component goal
- the states, branches, and flows that must be covered
- the must-do and must-not-do constraints
- the prompt requirements and tool-specific notes that shape how the external tool should be instructed
- the expected returned artifacts for intake
- the final copy-paste-ready prompt text for the external tool

This prompt artifact is part of source-of-truth handoff context. It should not live only in chat, and it is not complete if it contains only direction notes without the final prompt body.

Do not treat every prompt as the same shape. Choose the prompt strategy that matches the task:

- `canonical_shell` when defining a page family shell for the first time
- `state_variant` when keeping the same shell and generating additional states
- `family_extension` when extending the same family with a bounded new region or capability
- `independent_screen` when the screen does not share a shell contract with other work

Treat prompt strategy as two axes:

- `prompt_goal_type` explains the structural goal of the prompt
- `tool_guidance_profile` explains how the target tool should be guided

Recommended `tool_guidance_profile` values:

- `stitch_first_pass` for the first high-detail Stitch generation of one screen or family shell
- `stitch_iterative_refine` for later Stitch edits that should stay screen-focused and tightly scoped
- `figma_structured_handoff` for richer, more complete Figma handoff prompts
- `general_structured_handoff` for other tools when no stronger profile exists

Use `same_family_strict` when the shell and component language should remain fixed except for explicitly named variation.

Use `same_family_adaptive` when the same page family should stay recognizable but a bounded region is allowed to change more visibly.

For Stitch, prefer plain-language prompts and screen-by-screen refinement. Same-family prompts should explicitly preserve the shared shell instead of trusting the tool to infer it.

## 中文翻译

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
