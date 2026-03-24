# Function Block

## Metadata

- `fb_id`:
- `title`:
- `status`:

## Product Goal

- `business_objective`:
- `user_value`:
- `success_definition`:

## Ontology Frame

- `actor_status`:
- `actor_description`:
- `goal_status`:
- `goal_description`:
- `entity_status`:
- `entity_description`:
- `relation_status`:
- `relation_description`:
- `state_status`:
- `state_description`:
- `event_status`:
- `event_description`:
- `rule_status`:
- `rule_description`:
- `evidence_status`:
- `evidence_description`:

## Impact Map

- `business_layer`:
- `domain_layer`:
- `flow_layer`:
- `experience_layer`:
- `application_layer`:
- `service_layer`:
- `data_layer`:
- `quality_layer`:

## Scope

- `in_scope`:
- `out_of_scope`:
- `dependencies`:
- `related_artifacts`:

## Quality Context

- `overall_risk`:
- `quality_rulebook`: `<PROJECT_ROOT>/QUALITY_RULEBOOK.md`
- `special_quality_concerns`:

## Acceptance

- `acceptance_criteria`:
- `release_blockers`:

## Mission Plan

- `planned_mbs`:
- `completed_mbs`:
- `failed_mbs`:

## Notes

- `open_questions`:
- `next_recommended_mb`:

## Usage Rules

- One `FB` may contain multiple `MB`s.
- `FB` defines the product goal and final acceptance.
- `FB` must not enter detailed planning until all 8 ontology elements are covered.
- Each ontology status must be one of: `confirmed`, `assumed`, `risk`, or `out_of_scope`.
- `Impact Map` explains where this function lands in engineering, not what the function is.
- Each `*_layer` field should include: `affected=...; why=...; artifact_updates=...; validation_needed=...`.
- `MB` defines one independent code change attempt under this `FB`.
- Use compact IDs such as `fb2-mb1`, `fb2-mb2`, and `fb2-mb3`.
- The `FB` should track MB history so quality issues can be traced back to the exact feature effort.

---

## 中文翻译

### Function Block 模板

#### 元信息

- `fb_id`：功能块编号
- `title`：功能块标题
- `status`：状态

#### 产品目标

- `business_objective`：业务目标
- `user_value`：用户价值
- `success_definition`：成功定义

#### 本体框架

- `actor_status`：角色元素状态
- `actor_description`：谁在使用这个功能
- `goal_status`：目标元素状态
- `goal_description`：用户希望完成什么
- `entity_status`：实体元素状态
- `entity_description`：涉及哪些核心对象
- `relation_status`：关系元素状态
- `relation_description`：这些对象之间如何关联
- `state_status`：状态元素状态
- `state_description`：对象或流程有哪些关键状态
- `event_status`：事件元素状态
- `event_description`：什么动作或条件触发变化
- `rule_status`：规则元素状态
- `rule_description`：变化受哪些规则约束
- `evidence_status`：证据元素状态
- `evidence_description`：怎样证明这个功能真的完成

#### 影响地图

- `business_layer`：业务层影响
- `domain_layer`：领域层影响
- `flow_layer`：流程层影响
- `experience_layer`：体验层影响
- `application_layer`：应用层影响
- `service_layer`：服务层影响
- `data_layer`：数据层影响
- `quality_layer`：质量层影响

#### 范围

- `in_scope`：范围内内容
- `out_of_scope`：范围外内容
- `dependencies`：依赖项
- `related_artifacts`：相关真理源文件

#### 质量上下文

- `overall_risk`：整体风险
- `quality_rulebook`：质量规则手册路径
- `special_quality_concerns`：特殊质量关注点

#### 验收

- `acceptance_criteria`：验收标准
- `release_blockers`：发布阻塞项

#### Mission 计划

- `planned_mbs`：计划中的 mission blocks
- `completed_mbs`：已完成的 mission blocks
- `failed_mbs`：失败的 mission blocks

#### 备注

- `open_questions`：未决问题
- `next_recommended_mb`：建议的下一个 MB

#### 使用规则

- 一个 `FB` 可以包含多个 `MB`。
- `FB` 负责定义产品目标和最终验收。
- 在 8 个本体元素全部被覆盖之前，`FB` 不得进入详细规划。
- 每个本体元素状态只能是：`confirmed`、`assumed`、`risk` 或 `out_of_scope`。
- `Impact Map` 用来说明这个功能会落到哪些工程层，不是重复描述功能本身。
- 每个 `*_layer` 字段都应使用这种格式：`affected=...; why=...; artifact_updates=...; validation_needed=...`。
- `MB` 负责定义该 `FB` 下的一次独立代码改动尝试。
- 使用精简命名，例如 `fb2-mb1`、`fb2-mb2`、`fb2-mb3`。
- `FB` 应记录 MB 历史，方便把质量问题追溯到具体功能开发过程。
