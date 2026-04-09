# Mission Block

## Metadata

- `mb_id`:
- `parent_fb_id`:
- `status`:
- `change_type`:

## Parent FB Alignment

- `parent_fb_ontology_ref`:
- `acceptance_slice`:
- `ontology_elements_in_scope`:
- `affected_layers_in_scope`:
- `deferred_ontology_elements`:
- `deferred_layers`:

## Goal

- `goal`:

## Inputs

- `input_artifacts`:
- `input_ready_check`:

## Boundaries

- `allowed_files`:

## Quality Plan

- `quality_profile`:
- `selected_quality_checks`:
- `required_commands`:
- `pass_condition`:

## Evidence Required

- `required_test_evidence`:
- `required_artifact_updates`:
- `required_quality_report`:

## Result

- `outcome`:
- `next_action`:

## Machine Spec

- `machine_spec_ref`:
- `machine_spec_eval_refs`: none
- `machine_spec_memory_policy`: default
- `machine_spec_autonomy_level`: L2_auto_with_review

## Optional Appendix

- `hypothesis`:
- `alignment_notes`:
- `research_inputs`:
- `external_tool_prompt_ref`:
- `forbidden_files`:
- `change_budget`:
- `risk_level`:
- `user_visible_before`:
- `checks_before`:
- `known_problem_before`:
- `artifact_state_before`:
- `waived_checks`:
- `regression_rule`:
- `checkpoint`:
- `safe_revert_path`:
- `changed_files`:

## Usage Rules

- This `MB` inherits from one parent `FB`.
- `ontology_elements_in_scope`, `affected_layers_in_scope`, `deferred_ontology_elements`, and `deferred_layers` must make the slice explicit.
- Use `input_artifacts: none` when there is no upstream dependency.
- `input_ready_check` is required only when `input_artifacts` is not `none`.
- `input_artifacts` records execution dependencies only. It does not override the parent `FB`, the active `MB`, business rules, acceptance, or quality gates.
- If the parent `FB` uses `external_ui_package` or `hybrid`, this `MB` is an integration slice, not a visual redesign task.
- `selected_quality_checks` must be chosen from `QUALITY_RULEBOOK.md`.
- This `MB` is complete only when its required quality report exists and all required checks are evaluated.
- `required_artifact_updates` is only for source-of-truth artifacts that the Builder must update directly.
- Do not list `SESSION_STATE.md` in `required_artifact_updates` for a runnable `MB`; the harness runtime syncs session state automatically.
- Each runnable `MB` must have one machine sidecar with the same base id at `missions/<mb_id>.machine.json`.
- `machine_spec_ref` should point to that sidecar using one relative path, or `none` only when the mission is explicitly non-runnable.
- The machine sidecar should declare reusable `eval_refs`, `memory_policy`, and `autonomy_level` when the harness loop depends on them.
- `Optional Appendix` may be omitted entirely when it adds no useful clarity.
- Use `research_inputs` and `external_tool_prompt_ref` only when the active `MB` depends on research or an external-tool prompt artifact.
- `research_inputs` should use comma-separated relative paths under `research/`, or `none`.
- `external_tool_prompt_ref` should use one relative path under `experience_prompts/`, or `none`.

---

## 中文翻译

### Mission Block 模板

#### 元信息

- `mb_id`：mission block 编号
- `parent_fb_id`：所属 function block 编号
- `status`：状态
- `change_type`：改动类型

#### 父 FB 对齐

- `parent_fb_ontology_ref`：父 FB 本体引用
- `acceptance_slice`：本次 MB 覆盖的父 FB 验收切片
- `ontology_elements_in_scope`：本次 MB 触及的父 FB 本体元素
- `affected_layers_in_scope`：本次 MB 当前覆盖的父 FB 影响层
- `deferred_ontology_elements`：明确延期的本体元素
- `deferred_layers`：明确延期的工程层

#### 目标

- `goal`：本次改动目标

#### 输入

- `input_artifacts`：本次依赖的输入工件
- `input_ready_check`：输入已就绪的判定方式

#### 边界

- `allowed_files`：允许修改的文件

#### 质量计划

- `quality_profile`：质量档位
- `selected_quality_checks`：本次选择的检查项
- `required_commands`：必跑命令
- `pass_condition`：通过条件

#### 必需证据

- `required_test_evidence`：必需测试证据
- `required_artifact_updates`：Builder 需要直接更新的必需真理源工件
- `required_quality_report`：必需质量报告

#### 结果

- `outcome`：结果
- `next_action`：下一步动作

#### 机器规格

- `machine_spec_ref`：当前 MB 对应的 machine sidecar 路径

#### 可选附录

- `hypothesis`：本次改动假设
- `alignment_notes`：本次 MB 如何保持与父 FB 对齐
- `research_inputs`：当前 MB 使用的 research 输入或引用
- `external_tool_prompt_ref`：外部工具 prompt 的引用或编号
- `forbidden_files`：禁止修改的文件
- `change_budget`：允许的最大改动面
- `risk_level`：风险等级
- `user_visible_before`：改动前用户可见状态
- `checks_before`：改动前检查状态
- `known_problem_before`：改动前已知问题
- `artifact_state_before`：改动前真理源文件状态
- `waived_checks`：豁免的检查项
- `regression_rule`：回归判定规则
- `checkpoint`：检查点
- `safe_revert_path`：安全回滚路径
- `changed_files`：实际改动文件

#### 使用规则

- 每个 `MB` 都必须继承自一个父 `FB`。
- `ontology_elements_in_scope`、`affected_layers_in_scope`、`deferred_ontology_elements` 和 `deferred_layers` 必须把切片说清楚。
- 没有上游依赖时，`input_artifacts` 固定写 `none`。
- 只有 `input_artifacts != none` 时，才要求 `input_ready_check`。
- `input_artifacts` 只记录执行依赖输入，不覆盖父 `FB`、当前 `MB`、业务规则、验收或质量门禁。
- 如果父 `FB` 使用 `external_ui_package` 或 `hybrid`，这个 `MB` 是集成切片，不是视觉重设计任务。
- `selected_quality_checks` 必须从 `QUALITY_RULEBOOK.md` 中选择。
- 只有在所需质量报告存在且所有必需检查都已评估后，该 `MB` 才算完成。
- `required_artifact_updates` 只用于 Builder 需要直接更新的真理源工件。
- 对于可执行的 `MB`，不要把 `SESSION_STATE.md` 写进 `required_artifact_updates`；session state 由 harness runtime 自动同步。
- 每个可执行的 `MB` 都必须在 `missions/` 目录下拥有同名 machine sidecar，例如 `fb1-mb1.machine.json`。
- `machine_spec_ref` 应使用单个相对路径指向该 sidecar；只有明确不可运行的 mission 才能写 `none`。
- `Optional Appendix` 在没有额外价值时可以整段省略。
- 只有当前 `MB` 依赖 research 或外部工具 prompt 工件时，才填写 `research_inputs` 和 `external_tool_prompt_ref`。
- `research_inputs` 应使用逗号分隔的相对路径，指向 `research/` 下的文件；没有时写 `none`。
- `external_tool_prompt_ref` 应使用单个相对路径，指向 `experience_prompts/` 下的文件；没有时写 `none`。
