# Lifecycle

This document is the only normative lifecycle source in the protocol repository.

## Session Modes

Use one main mode per session.

| Mode | Use When | Required Inputs | Expected Output |
| :--- | :--- | :--- | :--- |
| `greenfield` | Starting a new product or feature set | Business goal, user problem, known constraints | Initial specs, quality setup, and first FB plan |
| `expansion` | Adding one new capability to an existing system | Existing source-of-truth files plus the new goal | Delta spec and detailed FB/MB plan |
| `continue` | Resuming interrupted work | Current session state, active FB, active MB, latest progress or failure notes | Next bounded action |
| `review` | Auditing completed implementation | Diff, evidence, and relevant source-of-truth files | Structured quality report |
| `recovery` | Repairing a broken or confused state | Error evidence, recent changes, and current state | Recovery path with the smallest safe move |

## Preflight Rule

Before `INIT`, the agent must run `Project Preflight` against the working path.

The preflight must classify the project as:

- `ready`
- `bootstrap_required`
- `blocked`

If the result is `bootstrap_required`, initialize safe foundational files before entering the requested scene.

If the result is `blocked`, ask only for the minimum missing context.

## Four Execution Layers

The lifecycle is a four-layer execution model:

| Layer | Purpose | Question It Answers |
| :--- | :--- | :--- |
| `Preflight` | Check whether work can safely begin | Can the requested scene start now? |
| `Scene Path` | Select the required work sequence for one scene | What kind of work must happen next? |
| `Role Handoff` | Transfer responsibility during normal progress | Who should act at this step? |
| `Issue Routing` | Return discovered problems to the correct owner | Who must resolve this problem? |

Always apply them in this order:

1. run `Preflight`
2. enter the requested `Scene Path`
3. activate the correct role through `Role Handoff`
4. if a problem is found, stop forward motion and use `Issue Routing`

## Universal Control Shell

All scenes share the same control shell.

| Stage | Purpose | Exit Criteria |
| :--- | :--- | :--- |
| `PREFLIGHT` | Check startup readiness and classify project state | State is `ready`, `bootstrap_required`, or `blocked` |
| `INIT` | Identify mode, project, active artifacts, and first role | Scene, files, and role are explicit |
| `SCENE_WORK` | Execute the scene-specific required path | Required scene outputs exist or a role handoff is triggered |
| `REVIEW_GATE` | Validate evidence, quality gates, and impact | Pass, fail, rework, or reroute decision exists |
| `CLOSE` | Persist current state for later sessions | Session state and next step are written |

## Scene-Specific Required Paths

| Scene | Required Path | Working Focus | First Role |
| :--- | :--- | :--- | :--- |
| `greenfield` | `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION` | Define product truth, initial quality system, and first FBs | `Spec Architect` |
| `expansion` | `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION` | Define the new feature, impact surface, regression risk, and detailed FB | `Spec Architect` |
| `continue` | `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION` | Reconstruct state and continue the next single safe action | `Builder`, `Spec Architect`, or `Recovery Coordinator` depending on state |
| `review` | `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING` | Audit implementation against FB, MB, artifacts, and evidence | `Reviewer` |
| `recovery` | `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION` | Stop drift, repair state, and choose the smallest safe move | `Recovery Coordinator` |

## Experience Delivery Gate

When the ontology frame and impact map are clear enough for planning, the `Spec Architect` must decide whether the experience layer is Builder-owned or externally delivered.

This decision must be stored in the parent `FB` as `experience_delivery_mode`.

Allowed values:

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

This is a gate inside `SPEC` or `FB_DETAILING`, not a separate scene stage.

If the mode is `external_ui_package` or `hybrid`, the parent `FB` must also record:

- required external input artifacts
- the Builder's allowed integration scope

Any dependent `MB` must remain inactive until those required inputs exist and are readable.

## Research Rule

`Research` is a support capability, not a new scene, role, or stage.

Use it mainly in:

- `Spec Architect` work during `DISCOVERY`, `SPEC`, or `FB_DETAILING`
- `Builder` work inside the active `MB`

Two trigger types are allowed:

- `user_triggered`: the user explicitly asks for search or lookup work
- `system_triggered`: the active role sees a material need for external facts, tools, references, or technical solutions

Execution rule:

- `user_triggered` research may run immediately
- `system_triggered` research requires user approval before any search begins
- do not perform silent network research

Accepted uses include:

- simple market scan or similar-product review during spec work
- searching for mature tools, libraries, services, or open-source projects
- checking official docs, issues, changelogs, or workarounds for a bounded technical problem
- gathering UI references, component directions, rendering approaches, or style precedents

Every research run must be captured in artifacts instead of living only in chat.

At minimum, record:

- `query`
- `trigger_type`
- `why_now`
- `sources`
- `facts`
- `candidates`
- `recommendation`
- `impact_on_fb_or_mb`

Write those results into one or more of:

- `DECISIONS.md`
- the active `FB`
- the active `MB`
- a `RESEARCH_NOTE`

## External Tool Prompt And Intake Rule

When the experience layer is externally delivered, follow this order:

1. gather references or research when needed
2. discuss and resolve the key UI decisions that determine the outcome
3. let the user confirm the adopted references, final visual direction, design core, and major UI decisions
4. generate and persist the external-tool prompt in `experience_prompts/*.md`
5. include a copy-paste-ready final prompt inside that artifact
6. hand off through that prompt artifact and let the user confirm the returned external result
7. treat the approved result as `input_artifacts` for later `MB`s

UI-related research may propose references and recommendations, but it may not finalize visual direction.

Prompt requirements are context-relative rather than globally identical.

Do not generate an external-tool prompt for UI work until the user confirms:

- which references are adopted
- the final visual direction
- the design core
- the intended information density
- the layout direction
- the component style direction
- the color and typography direction
- the interaction and motion direction when relevant
- the responsive or platform priority
- the accessibility constraints
- the references or patterns that should be avoided

If the prompt is for a shared page family, the user and assistant must also align on:

- the `page_family_id`
- the shared shell scope
- what must be preserved across states or later `MB`s
- what variation is allowed
- what drift is explicitly forbidden
- which prior approved prompts or artifacts define the family contract

For Stitch handoff, prefer plain-language, screen-focused prompts. For a new family, establish the canonical shell first; for later work, refine the family screen by screen with tightly scoped edits instead of mixing many structural changes into one prompt.

Do not leave the final external-tool prompt only in chat. Persist it as an artifact so downstream `MB`s and reviews can read the same handoff contract, and include the full copy-paste-ready prompt body inside that artifact.

The default mode is manual handoff:

- the assistant prepares research and prompt inputs
- the user runs the external tool and approves the result
- the approved output returns as `input_artifacts`

If a future connected tool mode exists and the user grants permission, direct tool operation is allowed, but the approved output still remains an input artifact under `FB` and `MB` authority.

## Discovery Exit Rule

When a scene path includes `DISCOVERY`, it ends only when the protocol can write four lists:

1. confirmed facts
2. assumptions being taken
3. unresolved risks
4. intentionally out-of-scope items

If the scene is expected to produce a detailed `FB`, discovery must also cover the `8-element ontology frame`:

1. `Actor`
2. `Goal`
3. `Entity`
4. `Relation`
5. `State`
6. `Event`
7. `Rule`
8. `Evidence`

Each element must be marked as:

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

Do not move into detailed `FB` writing or `MB` planning while ontology elements are still missing.

When the protocol starts `MB` planning, each planned `MB` must declare:

- which parent FB ontology elements are in scope
- which parent FB layers are in scope
- which ontology elements are deferred
- which layers are deferred

If the parent `FB` uses `external_ui_package` or `hybrid`, discovery must also identify:

- which states and branches the external package must cover
- which later `MB`s will consume those artifacts

## Role Handoff Rule

Scene paths define the sequence. Role handoffs define who owns the next step.

Every scene must:

- name the first active role
- define the handoff condition for the next role
- tell the user when a role change happens
- require user confirmation before entering a higher-cost or higher-risk work type

The Builder must not start from raw chat history.

The Builder starts only after reading:

- project constitution
- quality rulebook
- relevant feature or scope spec
- current function block
- current mission block
- required input artifacts when the current `FB` or `MB` depends on them
- current session state

If one of those is missing, the Builder must stop and request the missing artifact rather than infer it.

## Issue Routing Rule

Do not use vague fallback such as "go back one step".

When a problem is found, route it by ownership:

| Issue Type | Meaning | Route To |
| :--- | :--- | :--- |
| `spec_gap` | Goal, scope, acceptance, or contract is unclear or contradictory | `Spec Architect` |
| `implementation_bug` | Specs are clear, but implementation is wrong | `Builder` |
| `quality_evidence_gap` | Required checks, evidence, or quality report items are missing | `Builder` |
| `state_drift` | `SESSION_STATE`, active `FB/MB`, or repository references do not match reality | `Recovery Coordinator` |
| `environment_issue` | Toolchain, dependency, or runtime state blocks safe progress | `Recovery Coordinator` |
| `review_context_gap` | The current actor lacks required context to make a safe judgment | current scene lead role |

This rule applies in:

- `Preflight`
- scene work
- build
- review
- recovery

## Bootstrap Rule

If the user starts with only a repository and a scene, the agent must not ask for the SDD path again.

Instead, the agent must:

1. read the repository bootstrap files
2. run `Project Preflight`
3. map the requested scene path
4. activate the first appropriate role
5. tell the user what happens next

See `README.md` and `docs/06_session_bootstrap.md`.

## 中文翻译

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

### 启动规则

如果用户只给了“仓库 + 场景”，代理不应再要求重复提供 SDD 路径。

代理应当：

1. 读取仓库启动文件
2. 执行 `Project Preflight`
3. 映射请求场景路径
4. 激活第一个合适角色
5. 告诉用户接下来要发生什么

详见 `README.md` 和 `docs/06_session_bootstrap.md`。
