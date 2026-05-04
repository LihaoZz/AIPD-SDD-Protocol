<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: templates/QUALITY_RULEBOOK.template.md
Translation source: translations/zh/templates/QUALITY_RULEBOOK.template.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

### 质量规则手册模板

#### 目的

定义所有 mission blocks 唯一允许使用的质量标准。

#### 使用规则

- `MB` 不得自行发明质量标准。
- 每个 `MB` 都必须从本手册中选择检查项。
- 如果本手册中不存在所需检查项，`MB` 必须停止并请求更新手册，而不是临场发挥。
- 豁免检查项只能按照下面的豁免规则执行。

#### 质量档位

- `standard`：
  `scope_boundary`、`fb_ontology_alignment`、`layer_coverage_alignment`、`build`、`lint`、`typecheck`、`related_tests`、`artifact_sync`、`evidence`

- `strict`：
  在 `standard` 基础上额外加入
  `contract`、`smoke`、`rollback_ready`、`human_signoff`

#### 检查项目录

- `scope_boundary`：
  当所有改动文件都位于 `allowed_files` 内、
  没有触碰 `forbidden_files`、
  且未超出 `change_budget` 时通过。

- `fb_ontology_alignment`：
  当本次 MB 没有违背父 FB 中的 actor、goal、entity、relation、state、event、rule 或 evidence 模型，
  或者这些变化已经先通过正确角色更新到父 FB 时通过。
  这项检查应针对 MB 声明的本体切片，而不是和本次无关的 FB 元素。

- `layer_coverage_alignment`：
  当父 FB 中被标记为受影响的每一层，都在本次 MB 中获得对应的实现、工件更新或验证覆盖，
  或者被显式说明延期且给出理由时通过。
  这项检查应针对 MB 声明的层切片和明确延期项。

- `build`：
  当要求的构建命令成功退出时通过。

- `lint`：
  当 lint 成功退出，
  或在批准规则下未引入新的 lint 错误时通过。

- `typecheck`：
  当类型检查成功退出时通过。

- `related_tests`：
  当 MB 中列出的所有相关测试全部通过时通过。

- `artifact_sync`：
  当行为、API、数据模型或范围变化已同步到相关真理源文件时通过。

- `evidence`：
  当质量报告包含改动文件、执行过的检查、检查结果、开放风险和下一步动作时通过。

- `experience_input_alignment`：
  当本次 MB 正确消费父 FB 中声明的外部 UI 包或设计权威来源，
  且没有引入未经批准的视觉重设计时通过。
  这项检查只验证外部体验输入是否被正确消费，
  不能替代 `scope_boundary`、`fb_ontology_alignment`、`layer_coverage_alignment` 或其他必需检查。
  当父 FB 的 `experience_delivery_mode` 为 `external_ui_package` 或 `hybrid`，
  且本次 MB 触及 `experience` 或 `application` 层时，应选择此检查项。

- `contract`：
  当 API 或数据交互变更已根据契约完成验证时通过。

- `smoke`：
  当至少一个关键真实用户路径被端到端验证时通过。

- `rollback_ready`：
  当回滚路径已写清且可执行时通过。

- `human_signoff`：
  当高风险 MB 已获得人工明确复核时通过。

#### 豁免规则

- 只有在项目当前确实不存在该机制时，检查项才可以被豁免。
- 每个被豁免的检查项都必须写明：
  原因、
  替代证据、
  以及是否需要后续补建。
- 不允许的豁免理由包括：
  “改动很小”、
  “看起来没问题”、
  “时间不够”、
  “模型已经检查过了”。

#### 高风险触发条件

当 MB 触碰以下区域时，默认使用 `strict`：

- 认证、权限、支付
- 数据库、schema、迁移
- 公共 API
- 核心状态管理
- 部署、环境、基础设施
- 关键用户路径
