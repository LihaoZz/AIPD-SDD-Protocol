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
- `alignment_notes`:

## Goal

- `goal`:
- `hypothesis`:

## Boundaries

- `allowed_files`:
- `forbidden_files`:
- `change_budget`:
- `risk_level`:

## Baseline

- `user_visible_before`:
- `checks_before`:
- `known_problem_before`:
- `artifact_state_before`:

## Quality Plan

- `quality_profile`:
- `selected_quality_checks`:
- `waived_checks`:
- `required_commands`:
- `regression_rule`:
- `pass_condition`:

## Evidence Required

- `required_test_evidence`:
- `required_artifact_updates`:
- `required_quality_report`:

## Rollback

- `checkpoint`:
- `safe_revert_path`:

## Result

- `changed_files`:
- `outcome`:
- `next_action`:

## Usage Rules

- This `MB` must not invent its own product ontology.
- This `MB` inherits from one parent `FB`.
- `parent_fb_ontology_ref` should point to the parent FB or summarize the exact inherited slice.
- `ontology_elements_in_scope` must name which parent FB ontology elements this MB actively touches.
- `affected_layers_in_scope` must name which parent FB impact-map layers this MB covers now.
- `deferred_ontology_elements` and `deferred_layers` must explicitly record what this MB is not completing yet.
- `selected_quality_checks` must be chosen from `QUALITY_RULEBOOK.md`.
- If a needed quality rule does not exist in the rulebook, stop and request a rulebook update.
- `Baseline` must include all four items:
  `user_visible_before`,
  `checks_before`,
  `known_problem_before`,
  `artifact_state_before`.
- `waived_checks` must include a real reason and replacement evidence.
- This `MB` is complete only when its required quality report exists and all required checks are evaluated.

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
- `alignment_notes`：本次 MB 如何保持与父 FB 对齐

#### 目标

- `goal`：本次改动目标
- `hypothesis`：本次改动假设

#### 边界

- `allowed_files`：允许修改的文件
- `forbidden_files`：禁止修改的文件
- `change_budget`：允许的最大改动面
- `risk_level`：风险等级

#### 基线

- `user_visible_before`：改动前用户可见状态
- `checks_before`：改动前检查状态
- `known_problem_before`：改动前已知问题
- `artifact_state_before`：改动前真理源文件状态

#### 质量计划

- `quality_profile`：质量档位
- `selected_quality_checks`：本次选择的检查项
- `waived_checks`：豁免的检查项
- `required_commands`：必跑命令
- `regression_rule`：回归判定规则
- `pass_condition`：通过条件

#### 必需证据

- `required_test_evidence`：必需测试证据
- `required_artifact_updates`：必需工件更新
- `required_quality_report`：必需质量报告

#### 回滚

- `checkpoint`：检查点
- `safe_revert_path`：安全回滚路径

#### 结果

- `changed_files`：实际改动文件
- `outcome`：结果
- `next_action`：下一步动作

#### 使用规则

- `MB` 不得自行发明产品本体。
- 每个 `MB` 都必须继承自一个父 `FB`。
- `parent_fb_ontology_ref` 应指向父 FB，或简洁概括本次继承的切片。
- `ontology_elements_in_scope` 必须写明本次 MB 真实触及的父 FB 本体元素。
- `affected_layers_in_scope` 必须写明本次 MB 当前覆盖的父 FB 影响层。
- `deferred_ontology_elements` 和 `deferred_layers` 必须明确记录本次暂不完成的部分。
- `selected_quality_checks` 必须从 `QUALITY_RULEBOOK.md` 中选择。
- 如果规则手册中不存在所需质量规则，应停止并请求更新规则手册。
- `Baseline` 必须完整包含四项：
  `user_visible_before`、
  `checks_before`、
  `known_problem_before`、
  `artifact_state_before`。
- `waived_checks` 必须写明真实原因和替代证据。
- 只有在所需质量报告存在且所有必需检查都已评估后，该 `MB` 才算完成。
