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

## Experience Delivery

- `experience_delivery_mode`:
- `experience_input_artifacts`:
- `experience_builder_scope`:

## Scope

- `in_scope`:
- `out_of_scope`:

## Acceptance

- `acceptance_criteria`:

## Mission Plan

- `planned_mbs`:
- `next_recommended_mb`:

## Optional Appendix

- `dependencies`:
- `related_artifacts`:
- `overall_risk`:
- `special_quality_concerns`:
- `release_blockers`:
- `completed_mbs`:
- `failed_mbs`:
- `open_questions`:

## Usage Rules

- One `FB` may contain multiple `MB`s.
- `FB` defines the product goal and final acceptance.
- Do not enter detailed planning until all 8 ontology elements are covered.
- Each ontology status must be one of: `confirmed`, `assumed`, `risk`, or `out_of_scope`.
- Each `*_layer` field should use: `affected=...; why=...; artifact_updates=...; validation_needed=...`.
- `experience_delivery_mode` must be one of: `builder_generated`, `external_ui_package`, `hybrid`, or `not_applicable`.
- `experience_input_artifacts` and `experience_builder_scope` are required only when the mode is `external_ui_package` or `hybrid`.
- `Optional Appendix` may be omitted entirely when it adds no useful clarity.

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

#### 体验交付

- `experience_delivery_mode`：体验层交付方式
- `experience_input_artifacts`：外部 UI 输入工件
- `experience_builder_scope`：Builder 可负责的集成范围

#### 范围

- `in_scope`：范围内内容
- `out_of_scope`：范围外内容

#### 验收

- `acceptance_criteria`：验收标准

#### Mission 计划

- `planned_mbs`：计划中的 mission blocks
- `next_recommended_mb`：建议的下一个 MB

#### 可选附录

- `dependencies`：依赖项
- `related_artifacts`：相关真理源文件
- `overall_risk`：整体风险
- `special_quality_concerns`：特殊质量关注点
- `release_blockers`：发布阻塞项
- `completed_mbs`：已完成的 mission blocks
- `failed_mbs`：失败的 mission blocks
- `open_questions`：未决问题

#### 使用规则

- 一个 `FB` 可以包含多个 `MB`。
- `FB` 负责定义产品目标和最终验收。
- 在 8 个本体元素全部被覆盖之前，不得进入详细规划。
- 每个本体元素状态只能是：`confirmed`、`assumed`、`risk` 或 `out_of_scope`。
- 每个 `*_layer` 字段都应使用这种格式：`affected=...; why=...; artifact_updates=...; validation_needed=...`。
- `experience_delivery_mode` 必须是：`builder_generated`、`external_ui_package`、`hybrid` 或 `not_applicable` 之一。
- 只有当模式为 `external_ui_package` 或 `hybrid` 时，才要求填写 `experience_input_artifacts` 和 `experience_builder_scope`。
- `Optional Appendix` 在没有额外价值时可以整段省略。
