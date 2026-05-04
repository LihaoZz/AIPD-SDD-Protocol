<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: docs/00_lifecycle.md
Translation source: translations/zh/docs/00_lifecycle.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

### 说明

这个文件是协议仓库里唯一的生命周期权威来源。

### 会话模式

每次会话只使用一种主模式。

| 模式 | 何时使用 | 必需输入 | 预期输出 |
| :--- | :--- | :--- | :--- |
| `greenfield` | 从零开始一个新产品或新功能集 | 业务目标、用户问题、已知约束 | 初始规格、质量制度和首批 FB 计划 |
| `expansion` | 给现有系统增加一个新能力 | 现有真理源文件加上新的目标 | 差异规格和详细的 FB/MB 计划 |
| `continue` | 继续中断的工作 | 当前会话状态、当前 FB、当前 MB、最近进展或失败记录 | 下一个有边界的动作 |
| `review` | 审查已经完成的实现 | diff、证据和相关真理源文件 | 结构化质量报告 |
| `recovery` | 修复损坏或混乱状态 | 错误证据、最近变更和当前状态 | 最小安全恢复路径 |

### Preflight 规则

进入 `INIT` 前，必须先执行 `Project Preflight`。

结果只能是：

- `ready`
- `bootstrap_required`
- `blocked`

如果是 `bootstrap_required`，先补齐安全基础文件再进入场景。

如果是 `blocked`，只询问最小必要缺失信息。

### 四层执行模型

生命周期由四层组成：

- `Preflight`
- `Scene Path`
- `Role Handoff`
- `Issue Routing`

顺序固定为：

1. 先跑 `Preflight`
2. 再进入场景路径
3. 再激活正确角色
4. 一旦发现问题，停止正向推进并进入问题路由

### 通用控制外壳

所有场景共用：

- `PREFLIGHT`
- `INIT`
- `SCENE_WORK`
- `REVIEW_GATE`
- `CLOSE`

### 场景专属必经路径

| 场景 | 必经路径 | 工作重心 | 第一个角色 |
| :--- | :--- | :--- | :--- |
| `greenfield` | `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION` | 定义产品真理源、初始质量制度和首批 FB | `Spec Architect` |
| `expansion` | `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION` | 定义新功能、影响面、回归风险和详细 FB | `Spec Architect` |
| `continue` | `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION` | 重建状态并继续下一个唯一安全动作 | 取决于状态，可为 `Builder`、`Spec Architect` 或 `Recovery Coordinator` |
| `review` | `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING` | 对照 FB、MB、工件和证据做审计 | `Reviewer` |
| `recovery` | `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION` | 停止漂移、修复状态、选择最小安全动作 | `Recovery Coordinator` |

### 体验交付 Gate

当本体框架和影响地图已经足够清楚、可以进入规划时，`Spec Architect` 必须决定体验层由谁交付。

这个决定要写进父 `FB` 的 `experience_delivery_mode`。

允许值：

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

它是 `SPEC` 或 `FB_DETAILING` 内的必经 gate，不再是独立 stage。

如果模式是 `external_ui_package` 或 `hybrid`，父 `FB` 还必须写明：

- 必需的外部输入工件
- Builder 被允许的集成范围

所有依赖这些输入的 `MB`，在输入未就绪前不得激活。

### Research 规则

`Research` 是受控辅助能力，不是新的场景、角色或阶段。

它主要发生在：

- `Spec Architect` 的 `DISCOVERY`、`SPEC`、`FB_DETAILING`
- `Builder` 当前激活 `MB` 的执行过程中

允许两种触发类型：

- `user_triggered`：用户明确要求进行搜索或检索
- `system_triggered`：当前角色判断需要外部事实、工具、参考或技术解法

执行规则：

- `user_triggered` research 可以直接执行
- `system_triggered` research 在任何搜索开始前都必须先得到用户同意
- 不允许静默联网 research

适用场景包括：

- 规格阶段的简易市场研究或相似产品查看
- 搜索成熟工具、库、服务或开源项目
- 为当前有边界技术问题查官方文档、issue、changelog 或 workaround
- 搜索 UI 参考、组件方向、渲染方案或风格先例

每次 research 都必须沉淀进工件，不能只停留在聊天里。

最少记录：

- `query`
- `trigger_type`
- `why_now`
- `sources`
- `facts`
- `candidates`
- `recommendation`
- `impact_on_fb_or_mb`

这些结果必须写入以下一种或多种工件：

- `DECISIONS.md`
- 当前激活的 `FB`
- 当前激活的 `MB`
- `RESEARCH_NOTE`

### 外部工具 Prompt 与回流规则

当体验层由外部交付时，顺序固定为：

1. 先在需要时收集参考或做 research
2. 先把决定结果的关键 UI 细节讨论清楚
3. 由用户确认采纳的参考、最终视觉方向、设计核心，以及主要 UI 决策
4. 把基于确认方向生成的外部工具 prompt 固化到 `experience_prompts/*.md`
5. 在该工件中写入可直接复制给外部工具的完整提示词
6. 通过这个 prompt 工件完成交接，并由用户确认外部工具返回结果
7. 把批准结果作为后续 `MB` 的 `input_artifacts`

UI 相关 research 只能提供参考和建议，不能直接定视觉方向。

在生成任何 UI 外部工具 prompt 前，必须先由用户确认：

- 哪些参考被采纳
- 最终视觉方向是什么
- 设计核心是什么
- 信息密度
- 布局方向
- 组件风格方向
- 颜色和排版方向
- 交互与动效方向（相关时）
- 响应式或平台优先级
- 可访问性约束
- 明确不采用的参考或模式

最终外部工具 prompt 不能只停留在聊天里，必须固化为工件，并在工件中保留一份可直接复制使用的完整提示词，供后续 `MB` 和 review 读取同一份交接契约。

默认模式是手动交接：

- assistant 负责准备 research 和 prompt 输入
- 用户执行外部工具并确认结果
- 批准输出再作为 `input_artifacts` 回流

如果未来存在可连接工具模式，且用户明确授权，允许直接操作工具；但即使如此，回流产物仍然只是受 `FB` 与 `MB` 约束的输入工件。

### Discovery 退出规则

包含 `DISCOVERY` 的场景，只有在协议能写出以下四类内容时才算结束：

1. 已确认事实
2. 当前采用的假设
3. 未解决风险
4. 明确范围外事项

如果要产出详细 `FB`，还必须覆盖 8 元素本体框架：

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

每个元素都必须标记为：

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

只要本体元素仍缺失，就不能进入详细 `FB` 编写或 `MB` 规划。

开始 `MB` 规划后，每个 `MB` 都必须声明：

- 当前涉及哪些父 FB 本体元素
- 当前涉及哪些父 FB 工程层
- 哪些本体元素延期
- 哪些工程层延期

如果父 `FB` 使用 `external_ui_package` 或 `hybrid`，还必须识别：

- 外部包必须覆盖哪些状态和分叉
- 后续哪些 `MB` 会消费这些工件

### 角色交接规则

场景路径定义顺序，角色交接定义谁拥有下一步责任。

每个场景都必须：

- 指定第一个激活角色
- 定义切换条件
- 在切换时告诉用户
- 进入更高成本或风险工作前请求用户确认

Builder 不能从原始聊天记录直接开工。

Builder 开工前必须读取：

- 项目宪章
- 质量规则手册
- 相关规格或范围文档
- 当前 function block
- 当前 mission block
- 当前依赖的输入工件
- 当前 session state

任意一个缺失，都必须停下并要求补齐。

### 问题路由规则

不要使用“退回上一步”这种模糊说法。

发现问题后，必须按责任归因路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` -> `Recovery Coordinator`
- `environment_issue` -> `Recovery Coordinator`
- `review_context_gap` -> 当前场景主导角色

### AIPD Gate Outcome 规则

当外部执行运行时（例如 Symphony）运行一个 `MB` 时，AIPD 仍然是语义权威。

运行时可以调度任务、持有锁、启动 Codex、重试、暂停、交给 review 或关闭 `MB`，但只能依据一个已经校验通过的 AIPD gate outcome 执行。

Gate outcome 必须先通过 `schemas/aipd-gate-outcome.schema.json` 校验，运行时才可以执行其中的指令。

存在两个 gate：

- `attempt_start`：决定某次 `MB` attempt 是否可以启动 Codex
- `attempt_finish`：在 attempt 证据产生后，决定下一步怎么处理

Fail-closed 规则：

- gate outcome 缺失时，Symphony 不得启动 Codex
- gate outcome 格式错误时，Symphony 不得启动 Codex
- `symphony_instruction.action` 未知时，Symphony 不得启动 Codex
- 只有当 `action` 是 `dispatch_codex` 时，`may_start_codex` 才可以为 `true`
- 不能只根据进程退出码决定 retry、review、recovery 或 close

如果 gate outcome 无效、有歧义，或缺少必需证据，应根据具体失败归类为 `state_drift`、`quality_evidence_gap` 或 `review_context_gap`。

### 启动规则

如果用户只给了“仓库 + 场景”，代理不应再要求重复提供 SDD 路径。

代理应当：

1. 读取仓库启动文件
2. 执行 `Project Preflight`
3. 映射请求场景路径
4. 激活第一个合适角色
5. 告诉用户接下来要发生什么

详见 `README.md` 和 `docs/06_session_bootstrap.md`。
