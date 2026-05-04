<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: templates/EXPERIENCE_PROMPT.template.md
Translation source: translations/zh/templates/EXPERIENCE_PROMPT.template.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

### Experience Prompt 模板

#### 元信息

- `prompt_id`：prompt 编号
- `parent_fb_id`：所属父 FB 编号
- `related_mb_ids`：关联的 MB 编号
- `page_family_id`：页面族编号
- `prompt_goal_type`：本次 prompt 目标类型
- `consistency_mode`：一致性模式
- `family_source_refs`：页面族来源工件引用
- `tool_guidance_profile`：工具指引档位
- `target_tool`：目标外部工具
- `status`：prompt 状态
- `source_artifacts`：来源工件

#### 已确认方向

- `adopted_reference_refs`：已采纳参考的本地引用
- `visual_direction`：最终视觉方向
- `design_core`：设计核心
- `information_density`：信息密度
- `layout_direction`：布局方向
- `component_style_direction`：组件风格方向
- `color_direction`：颜色方向
- `typography_direction`：字体与排版方向
- `interaction_direction`：交互方式方向
- `motion_direction`：动效方向
- `responsive_priority`：响应式优先级
- `accessibility_rules`：可访问性规则
- `references_to_avoid`：明确不采用的参考

#### 页面族一致性契约

- `shared_shell_scope`：共享壳子范围
- `must_preserve`：必须保持不变的部分
- `allowed_variation`：允许变化的部分
- `forbidden_drift`：禁止漂移的部分
- `component_contract_expectations`：组件契约要求

#### 范围

- `page_or_component_goal`：页面或组件目标
- `states_and_branches`：必须覆盖的状态与分叉
- `required_flows`：必须覆盖的流程

#### 构建说明

- `style_direction`：风格方向
- `must_do`：必做项
- `must_not_do`：禁止项

#### 期望返回

- `expected_return_artifacts`：期望返回物
- `downstream_intake_notes`：后续 intake 说明

#### Prompt 策略

- `prompt_requirements`：本次 prompt 的任务型要求
- `tool_specific_notes`：工具特定说明

#### 可直接复制提示词

把最终可直接投喂给外部工具的完整提示词放在这里。它应足够详细，尽量让外部工具一次生成接近目标的 UI。

```text
[在这里写最终可复制提示词。应包含页面或组件目标、必须覆盖的状态与分叉、确认后的视觉方向、布局与组件决策、约束条件，以及期望返回物。]
```

#### 使用规则

- 只有在用户确认采纳参考、最终视觉方向、设计核心，以及影响结果的主要 UI 决策后，才能创建这个工件。
- `target_tool` 必须是：`figma`、`stitch` 或 `other` 之一。
- `status` 必须是：`draft`、`approved_for_handoff` 或 `superseded` 之一。
- `prompt_goal_type` 必须是：`canonical_shell`、`state_variant`、`family_extension` 或 `independent_screen` 之一。
- `consistency_mode` 必须是：`same_family_strict`、`same_family_adaptive` 或 `not_applicable` 之一。
- `tool_guidance_profile` 必须是：`stitch_first_pass`、`stitch_iterative_refine`、`figma_structured_handoff` 或 `general_structured_handoff` 之一。
- `source_artifacts` 应使用逗号分隔的项目内相对路径，指向相关 `FB`、`MB`、research note 或其他真理源工件。
- `adopted_reference_refs` 应使用逗号分隔的项目内相对路径指向已批准的本地参考；没有时写 `none`。
- `family_source_refs` 应使用逗号分隔的项目内相对路径，指向先前已批准的 prompt 或其他页面族约束工件；没有时写 `none`。
- 结构化字段用于记录已确认的设计决策；`Copy-Paste Prompt` 部分用于保存最终可直接发送给外部工具的详细提示词。
- prompt 要求是相对任务而定的，不应把所有场景都写成同一种提示词。
- 如果本次 prompt 面向共享页面族，必须填写 `page_family_id`，并通过 `shared_shell_scope`、`must_preserve`、`allowed_variation`、`forbidden_drift` 明确写出共享壳子契约。
- `canonical_shell` 用于首次定义某个页面族的壳子；`state_variant` 用于同一壳子下的不同状态；`family_extension` 用于同一页面族内的局部扩展；`independent_screen` 用于无共享壳子约束的独立页面。
- `same_family_strict` 表示除明确允许变化的部分外，壳子、组件语言和 token 节奏都应保持固定。
- `same_family_adaptive` 表示页面族壳子仍需可识别，但在 prompt 明确允许时，局部区域可以发生更明显变化。
- 如果 `prompt_goal_type` 是 `independent_screen`，则 `page_family_id` 应写 `not_applicable`，`consistency_mode` 应写 `not_applicable`，`family_source_refs` 应写 `none`。
- `stitch_first_pass` 用于 Stitch 的首轮高细节单页 prompt；`stitch_iterative_refine` 用于后续聚焦单页、一次只改一到两个点的迭代；`figma_structured_handoff` 用于交给 Figma 的较完整多状态交接；`general_structured_handoff` 是其他外部工具的保守兜底档位。
- 当 `target_tool` 为 `stitch` 时，优先使用大白话、聚焦单页的 prompt。复杂场景先定页面族壳子，再按 screen-by-screen、局部增量修改去细化。
- 这个工件只用于外部工具交接，不覆盖当前 `FB`、当前 `MB`、业务规则、验收或质量门禁。
