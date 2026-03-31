# Experience Prompt

## Metadata

- `prompt_id`:
- `parent_fb_id`:
- `related_mb_ids`:
- `page_family_id`:
- `prompt_goal_type`:
- `consistency_mode`:
- `family_source_refs`:
- `tool_guidance_profile`:
- `target_tool`:
- `status`:
- `source_artifacts`:

## Confirmed Direction

- `adopted_reference_refs`:
- `visual_direction`:
- `design_core`:
- `information_density`:
- `layout_direction`:
- `component_style_direction`:
- `color_direction`:
- `typography_direction`:
- `interaction_direction`:
- `motion_direction`:
- `responsive_priority`:
- `accessibility_rules`:
- `references_to_avoid`:

## Family Consistency Contract

- `shared_shell_scope`:
- `must_preserve`:
- `allowed_variation`:
- `forbidden_drift`:
- `component_contract_expectations`:

## Scope

- `page_or_component_goal`:
- `states_and_branches`:
- `required_flows`:

## Build Instructions

- `style_direction`:
- `must_do`:
- `must_not_do`:

## Expected Return

- `expected_return_artifacts`:
- `downstream_intake_notes`:

## Prompt Strategy

- `prompt_requirements`:
- `tool_specific_notes`:

## Copy-Paste Prompt

Paste the final tool-ready prompt here. This section should be detailed enough that the external tool can generate the intended UI in one pass.

```text
[Write the final copy-paste prompt here. Include the page or component goal, all required states and branches, confirmed visual direction, layout and component decisions, constraints, and expected return artifacts.]
```

## Usage Rules

- Create this artifact only after the user confirms adopted references, final visual direction, design core, and the major UI decisions that shape the output.
- `target_tool` must be one of: `figma`, `stitch`, or `other`.
- `status` must be one of: `draft`, `approved_for_handoff`, or `superseded`.
- `prompt_goal_type` must be one of: `canonical_shell`, `state_variant`, `family_extension`, or `independent_screen`.
- `consistency_mode` must be one of: `same_family_strict`, `same_family_adaptive`, or `not_applicable`.
- `tool_guidance_profile` must be one of: `stitch_first_pass`, `stitch_iterative_refine`, `figma_structured_handoff`, or `general_structured_handoff`.
- `source_artifacts` should list comma-separated relative paths to governing `FB`, `MB`, research notes, or other source-of-truth artifacts.
- `adopted_reference_refs` should list comma-separated relative paths to approved local references, or `none`.
- `family_source_refs` should list comma-separated relative paths to prior approved prompts or other family-governing artifacts, or `none`.
- Use the structured fields to record confirmed design decisions; use `Copy-Paste Prompt` to store the final detailed prompt text that the user can send directly to the external tool.
- Prompt requirements are context-relative. Do not force the same prompt shape on every task.
- If the prompt targets a shared page family, set `page_family_id` and make the shared shell contract explicit through `shared_shell_scope`, `must_preserve`, `allowed_variation`, and `forbidden_drift`.
- Use `canonical_shell` for the first prompt that defines a page family's shell, `state_variant` for the same shell under different states, `family_extension` for bounded additions inside the same family, and `independent_screen` for unrelated screens.
- `same_family_strict` means the shell, component language, and token rhythm should remain fixed except for the explicitly allowed variation.
- `same_family_adaptive` means the family shell remains recognizable, but bounded regions may change more visibly when the prompt explicitly allows it.
- If `prompt_goal_type` is `independent_screen`, set `page_family_id` to `not_applicable`, `consistency_mode` to `not_applicable`, and `family_source_refs` to `none`.
- `stitch_first_pass` is for the first high-detail screen prompt in Stitch; `stitch_iterative_refine` is for later screen-focused edits with one or two scoped changes; `figma_structured_handoff` is for richer multi-state handoff to Figma; `general_structured_handoff` is the fallback for other tools.
- When `target_tool` is `stitch`, prefer plain-language, screen-focused prompts. For complex work, establish the family shell first, then refine screen by screen with tightly scoped edits.
- This artifact guides external-tool handoff only. It does not override the active `FB`, active `MB`, business rules, acceptance, or quality gates.

---

## 中文翻译

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
