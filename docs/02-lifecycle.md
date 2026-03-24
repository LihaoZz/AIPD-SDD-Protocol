# Lifecycle

## Session Modes

Use one mode per session.

| Mode | Use When | Required Inputs | Expected Output |
| :--- | :--- | :--- | :--- |
| `greenfield` | Starting a new product or feature set | Business goal, user problem, constraints if known | Initial specs, quality setup, and first FB plan |
| `expansion` | Adding a new capability to an existing system | Existing source-of-truth docs plus the new goal | Delta spec and detailed FB/MB plan |
| `continue` | Resuming interrupted work | Current session state, active FB, active MB, failure or progress notes | Next bounded action |
| `review` | Auditing completed implementation | Diff, quality evidence, and relevant source-of-truth docs | Structured quality report |
| `recovery` | Fixing a broken or confused state | Error evidence, recent changes, and session state | Recovery path with smallest safe move |

---

## Preflight Rule

Before `INIT`, the agent must run `Project Preflight` against the working path.

The preflight must classify the project as:

- `ready`
- `bootstrap_required`
- `blocked`

If the result is `bootstrap_required`, the agent should initialize safe foundational files before entering the requested scene.

If the result is `blocked`, the agent should ask only for the minimum missing context.

---

## Four Execution Layers

The lifecycle is not one identical path for every scene.

It is a four-layer execution model:

| Layer | Purpose | Question It Answers |
| :--- | :--- | :--- |
| `Preflight` | Check whether work can safely begin | Can the requested scene start now? |
| `Scene Path` | Select the required work sequence for one scene | What kind of work must happen next? |
| `Role Handoff` | Transfer responsibility between roles during normal progress | Who should act at this step? |
| `Issue Routing` | Return discovered problems to the correct owner | Who must resolve this problem? |

These layers work in order:

1. run `Preflight`
2. enter the requested `Scene Path`
3. activate the correct role through `Role Handoff`
4. if a problem is found, stop forward motion and use `Issue Routing`

---

## Universal Control Shell

All scenes share the same control shell.

| Stage | Purpose | Exit Criteria |
| :--- | :--- | :--- |
| `PREFLIGHT` | Check startup readiness and classify the project state | State is `ready`, `bootstrap_required`, or `blocked` |
| `INIT` | Identify mode, project, active artifacts, and first role | Scene, files, and role are explicit |
| `SCENE_WORK` | Execute the scene-specific required path | Required scene outputs exist or a role handoff is triggered |
| `REVIEW_GATE` | Validate evidence, quality gates, and impact | Pass, fail, rework, or reroute decision exists |
| `CLOSE` | Persist current state for later sessions | Session state and next step are written |

---

## Scene Path Rule

Each scene must define its own:

- required path
- working focus
- required outputs
- first role
- allowed handoffs
- stop conditions

The universal control shell must not be mistaken for one fixed work path.

---

## Scene-Specific Required Paths

| Scene | Required Path | Working Focus | First Role |
| :--- | :--- | :--- | :--- |
| `greenfield` | `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION` | Define product truth, initial quality system, and first FBs | `Spec Architect` |
| `expansion` | `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION` | Define the new feature, impact surface, regression risk, and detailed FB | `Spec Architect` |
| `continue` | `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION` | Reconstruct state and continue the next single safe action | `Builder`, `Spec Architect`, or `Recovery Coordinator` depending on state |
| `review` | `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING` | Audit implementation against FB, MB, artifacts, and evidence | `Reviewer` |
| `recovery` | `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION` | Stop drift, repair state, and choose the smallest safe move | `Recovery Coordinator` |

---

## Discovery Exit Rule

When a scene path includes `DISCOVERY`, it does not end when the model has asked "enough questions."

It ends when the protocol can write four lists:

1. confirmed facts
2. assumptions being taken
3. unresolved risks
4. items intentionally out of scope

If those four lists are weak, more questions are needed.

If the scene is expected to produce a detailed `FB`, discovery also must cover the `8-element ontology frame`:

1. `Actor`
2. `Goal`
3. `Entity`
4. `Relation`
5. `State`
6. `Event`
7. `Rule`
8. `Evidence`

Each element must be marked as one of:

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

---

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
- current session state

If one of those is missing, the Builder must stop and ask for the missing artifact rather than infer it.

---

## Issue Routing Rule

Do not use vague fallback such as "go back one step."

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

---

## Bootstrap Rule

If the user starts with only a repository and a scene, the agent must not ask for the SDD path again.

Instead, the agent must:

1. read the repository bootstrap files
2. run `Project Preflight`
3. map the requested scene path
4. activate the first appropriate role
5. tell the user what happens next

See `README.md` and `docs/08-session-bootstrap.md`.

---

## 中文翻译

### 会话模式

每次会话只使用一种主模式。

| 模式 | 何时使用 | 必需输入 | 预期输出 |
| :--- | :--- | :--- | :--- |
| `greenfield` | 从零开始一个新产品或新功能集 | 业务目标、用户问题，以及已知约束 | 初始规格、质量制度和首批 FB 计划 |
| `expansion` | 给现有系统增加新能力 | 现有真理源文档加上新的目标 | 差异规格和详细的 FB/MB 计划 |
| `continue` | 继续中断的工作 | 当前会话状态、当前 FB、当前 MB、失败或进展记录 | 下一个有边界的动作 |
| `review` | 审查已经完成的实现 | diff、质量证据和相关真理源文档 | 结构化质量报告 |
| `recovery` | 修复损坏或混乱状态 | 错误证据、最近变更和会话状态 | 最小安全恢复路径 |

### Preflight 规则

在进入 `INIT` 之前，代理必须先对当前工作路径执行 `Project Preflight`。

Preflight 的结果只允许三类：

- `ready`
- `bootstrap_required`
- `blocked`

如果结果是 `bootstrap_required`，代理应先自动补齐安全的基础制度文件，再进入请求场景。

如果结果是 `blocked`，代理只应询问最小必要缺失信息。

### 四层执行模型

生命周期并不是所有场景都相同的一条路径。

它是一个四层执行模型：

| 层级 | 作用 | 回答的问题 |
| :--- | :--- | :--- |
| `Preflight` | 判断是否可以安全开始工作 | 现在能不能进入请求场景？ |
| `Scene Path` | 选择某个场景的必经工作序列 | 接下来必须做什么类型的工作？ |
| `Role Handoff` | 在正常推进中切换责任角色 | 当前这一步该由谁执行？ |
| `Issue Routing` | 把发现的问题回流给正确责任方 | 这个问题该由谁解决？ |

这四层按顺序工作：

1. 先运行 `Preflight`
2. 再进入请求场景的 `Scene Path`
3. 通过 `Role Handoff` 激活正确角色
4. 如果发现问题，停止正向推进并进入 `Issue Routing`

### 通用控制外壳

所有场景共用同一个控制外壳。

| 阶段 | 目的 | 退出条件 |
| :--- | :--- | :--- |
| `PREFLIGHT` | 检查启动就绪状态并分类项目状态 | 状态已被归类为 `ready`、`bootstrap_required` 或 `blocked` |
| `INIT` | 确认模式、项目、当前工件和首个角色 | 场景、文件集合和角色都已明确 |
| `SCENE_WORK` | 执行当前场景的必经路径 | 已产出场景要求的结果，或已触发角色交接 |
| `REVIEW_GATE` | 验证证据、质量门禁和系统影响 | 已得到通过、失败、返工或回流决定 |
| `CLOSE` | 为后续会话保存当前状态 | 会话状态和下一步已写下 |

### 场景路径规则

每个场景都必须单独定义：

- 必经路径
- 工作重心
- 必需产物
- 第一个角色
- 允许的角色交接
- 停止条件

不能把通用控制外壳误解为一条固定不变的工作流。

### 场景专属必经路径

| 场景 | 必经路径 | 工作重心 | 第一个角色 |
| :--- | :--- | :--- | :--- |
| `greenfield` | `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION` | 定义产品真理源、初始质量制度和首批 FB | `Spec Architect` |
| `expansion` | `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION` | 定义新功能、影响面、回归风险和详细 FB | `Spec Architect` |
| `continue` | `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION` | 重建状态并继续下一个唯一安全动作 | 取决于状态，可为 `Builder`、`Spec Architect` 或 `Recovery Coordinator` |
| `review` | `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING` | 对照 FB、MB、工件和证据做审计 | `Reviewer` |
| `recovery` | `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION` | 停止漂移、修复状态、选择最小安全动作 | `Recovery Coordinator` |

### Discovery 的退出规则

当某个场景路径包含 `DISCOVERY` 时，`DISCOVERY` 不是在模型觉得“问题问够了”时结束。

它结束于协议能够写出四张清单：

1. 已确认事实
2. 当前采用的假设
3. 未解决风险
4. 明确不做的范围外事项

如果这四张清单写得很弱，就说明还需要继续提问。

如果当前场景需要产出一个详细的 `FB`，discovery 还必须覆盖 `8 元素本体框架`：

1. `Actor`
2. `Goal`
3. `Entity`
4. `Relation`
5. `State`
6. `Event`
7. `Rule`
8. `Evidence`

每个元素都必须标记为以下状态之一：

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

只要本体元素仍有缺口，就不得进入详细 `FB` 编写或 `MB` 规划。

当协议开始进入 `MB` 规划时，每个计划中的 `MB` 都必须声明：

- 当前涉及父 FB 的哪些本体元素
- 当前涉及父 FB 的哪些工程层
- 哪些本体元素被延期
- 哪些工程层被延期

### 角色交接规则

场景路径定义顺序，角色交接定义谁拥有下一步责任。

每个场景都必须：

- 指定第一个激活角色
- 定义切换到下一个角色的条件
- 在切换发生时告诉用户
- 在进入更高成本或更高风险工作类型前请求用户确认

Builder 不能从原始聊天记录直接开工。

Builder 只有在读过以下内容后才能开始：

- 项目宪章
- 质量规则手册
- 相关功能规格或范围文档
- 当前 function block
- 当前 mission block
- 当前会话状态

如果其中任意一个缺失，Builder 必须停下并要求补齐，而不是自行推断。

### 问题路由规则

不要使用“退回上一步”这种模糊说法。

发现问题后，必须按责任归因路由：

| 问题类型 | 含义 | 路由到 |
| :--- | :--- | :--- |
| `spec_gap` | 目标、范围、验收或契约不清晰或相互矛盾 | `Spec Architect` |
| `implementation_bug` | 规格清楚，但实现有误 | `Builder` |
| `quality_evidence_gap` | 缺少必需检查、证据或质量报告内容 | `Builder` |
| `state_drift` | `SESSION_STATE`、当前 `FB/MB` 或仓库引用与现实不一致 | `Recovery Coordinator` |
| `environment_issue` | 工具链、依赖或运行环境阻碍安全推进 | `Recovery Coordinator` |
| `review_context_gap` | 当前执行者缺少安全判断所需上下文 | 当前场景主导角色 |

这条规则适用于：

- `Preflight`
- 场景执行
- build
- review
- recovery

### 启动规则

如果用户开场时只给了“仓库”和“场景”，代理不应再要求重复提供 SDD 路径。

代理应当：

1. 读取仓库启动文件
2. 执行 `Project Preflight`
3. 映射请求场景的路径
4. 激活第一个合适角色
5. 告诉用户接下来要发生什么

详见 `README.md` 和 `docs/08-session-bootstrap.md`。
