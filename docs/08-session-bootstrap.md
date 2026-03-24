# Session Bootstrap

## Purpose

This document defines how an agent should begin work when the user provides only a repository and a scene.

The goal is to remove setup friction for a non-technical user.

The user should not need to remember:

- internal file paths
- which role goes first
- which scene path applies
- which files belong to which scene
- which stage comes next

---

## Bootstrap Rule

When a new conversation starts, the agent should interpret the repository root or repository link as the source of authority.

The user does not need to provide the SDD path again.

The user may start with only:

- repository link or repository root
- scene

The agent must then:

1. run `Project Preflight`
2. classify the startup result
3. map the scene path
4. choose the first active role
5. tell the user what it is doing
6. ask only the next necessary questions

---

## Global Bootstrap Files

For every scene, read these first:

- `README.md`
- `docs/02-lifecycle.md`
- `docs/06-operating-playbook.md`

These files define:

- the protocol purpose
- the four execution layers
- the scene-specific operating flow
- the repository bootstrap rule described by `README.md`

---

## Project Preflight

After reading the global bootstrap files, the agent must run `Project Preflight` before entering the requested scene.

The preflight must check:

- foundational files
- foundational directories
- state references such as the active FB and active MB
- scene-specific requirements

The preflight must return a short summary with:

1. requested scene
2. project root
3. preflight result
4. whether the scene can start now
5. active role
6. scene path
7. missing items
8. automatic actions
9. blocking items, if any

Allowed results:

- `ready`
- `bootstrap_required`
- `blocked`

If the result is `bootstrap_required`, the agent should initialize safe foundational files before continuing.

If the result is `blocked`, the agent should ask only for the minimum missing context.

After preflight, the agent must not jump straight into implementation.

It must continue in this order:

1. choose the scene-specific path
2. activate the first role
3. use role handoff when work type changes
4. use issue routing if a problem is found

Use `templates/PREFLIGHT_RESULT.template.md` as the structure for this summary.

---

## Scene-Specific Reading Paths

### `greenfield`

After the global bootstrap files, read:

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/03-artifacts.md`
- `templates/CONSTITUTION.template.md`
- `templates/SCOPE.template.md`
- `templates/DECISIONS.template.md`
- `templates/FUNCTION_BLOCK.template.md`
- `templates/MISSION_BLOCK.template.md`
- `templates/QUALITY_RULEBOOK.template.md`
- `templates/QUALITY_MEMORY.template.md`
- `templates/QUALITY_REPORT.template.json`
- `templates/SESSION_STATE.template.md`

Read these too when relevant:

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

First role:

- `Spec Architect`

Required path:

- `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION`

Next action:

- ask product questions in plain language until the 8 ontology elements and affected layers can be written

Do not:

- start coding
- ask the user to choose technical stack too early

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

### `expansion`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `<PROJECT_ROOT>/QUALITY_RULEBOOK.md`
- `<PROJECT_ROOT>/QUALITY_MEMORY.md`

Read these too when relevant:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

First role:

- `Spec Architect`

Required path:

- `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION`

Next action:

- identify what this feature changes, what current assumption it may break, and what ontology or impact-map detail must appear in the FB

Do not:

- start implementing before specs are updated

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

### `continue`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current function block
- current mission block
- every file listed in required reads

Also read when needed:

- `docs/05-review-recovery.md`

First role:

- `Builder` if the state is healthy
- `Spec Architect` or `Recovery Coordinator` if the state is blocked or drifting

Required path:

- `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION`

Next action:

- name the current stage and the next single action

Do not:

- restart the whole project from zero

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

### `review`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- relevant function block
- relevant mission block
- relevant contract files
- `docs/05-review-recovery.md`
- `schemas/quality-report.schema.json`

First role:

- `Reviewer`

Required path:

- `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING`

Next action:

- audit against written artifacts and evidence

Do not:

- patch code during the review pass unless the user explicitly changes the task

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

### `recovery`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current function block if it exists
- current mission block if it exists
- `<PROJECT_ROOT>/VERSION_LOG.md` if it exists
- `<PROJECT_ROOT>/QUALITY_MEMORY.md` if it exists
- `docs/05-review-recovery.md`
- relevant broken-area artifacts

First role:

- `Recovery Coordinator`

Required path:

- `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION`

Next action:

- classify the failure and choose the smallest safe move

Do not:

- continue implementation by instinct

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## First Reply Template

After bootstrapping, the first real reply should contain:

1. selected scene
2. preflight result
3. whether the scene can start now
4. active role
5. scene path
6. files read
7. files missing, if any
8. next questions or next action

That reply should be short and operational.

---

## Minimal User Messages

The repository is designed so the user can start with messages like:

- `Repo: <repo-link>\nScene: greenfield`
- `Repo: <repo-link>\nScene: expansion`
- `Repo: <repo-link>\nScene: continue`
- `Repo: <repo-link>\nScene: review`
- `Repo: <repo-link>\nScene: recovery`

Optional third line:

- a product idea
- a feature request
- a blocker
- a review target

---

## Important Limitation

This rule works only if the model or tool can actually read the repository contents from the link or local root.

If the tool cannot access the repository, the user must provide access by:

- giving the local path
- uploading the files
- or using a tool that can browse the repository

---

## 中文翻译

## 会话启动手册

### 目的

这个文档定义了：当用户只提供“仓库”和“场景”时，代理应该如何开始工作。

目标是降低非技术用户的启动摩擦。

用户不应该需要记住：

- 内部文件路径
- 哪个角色先开始
- 当前应该走哪条场景路径
- 哪些文件属于哪个场景
- 下一步应该进入哪个阶段

### 启动规则

当新对话开始时，代理应该把仓库根目录或仓库链接视为权威来源。

用户不需要再次提供 SDD 路径。

用户只需要给：

- 仓库链接或仓库根目录
- 场景

然后代理必须：

1. 先执行 `Project Preflight`
2. 对启动结果分类
3. 映射场景路径
4. 选择第一个激活角色
5. 告诉用户自己正在做什么
6. 只问下一轮真正必要的问题

### 全局启动文件

无论什么场景，都先读取这些文件：

- `README.md`
- `docs/02-lifecycle.md`
- `docs/06-operating-playbook.md`

这些文件定义了：

- 协议目的
- 四层执行模型
- 场景对应的操作流程
- 仓库启动规则

### Project Preflight

读完全局启动文件后，在进入请求场景之前，代理必须先执行 `Project Preflight`。

Preflight 必须检查：

- 基础文件
- 基础目录
- 当前激活的 FB 和 MB 等状态引用
- 场景专属要求

Preflight 必须返回一份简短总结，至少包含：

1. 用户请求的场景
2. 项目根目录
3. preflight 结果
4. 该场景现在是否可以开始
5. 当前激活角色
6. 场景路径
7. 缺失项
8. 自动动作
9. 阻塞项（如果有）

允许的结果只有：

- `ready`
- `bootstrap_required`
- `blocked`

如果结果是 `bootstrap_required`，代理应先自动补齐安全的基础制度文件，再继续。

如果结果是 `blocked`，代理只应询问最小必要缺失信息。

完成 preflight 后，代理不能直接跳进实现。

它必须继续按下面顺序推进：

1. 选择该场景的专属路径
2. 激活第一个角色
3. 当工作类型变化时使用 role handoff
4. 一旦发现问题，使用 issue routing

生成这份总结时，应使用 `templates/PREFLIGHT_RESULT.template.md` 作为结构。

### 场景专属阅读路径

#### `greenfield`

读取全局启动文件后，再读：

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/03-artifacts.md`
- `templates/CONSTITUTION.template.md`
- `templates/SCOPE.template.md`
- `templates/DECISIONS.template.md`
- `templates/FUNCTION_BLOCK.template.md`
- `templates/MISSION_BLOCK.template.md`
- `templates/QUALITY_RULEBOOK.template.md`
- `templates/QUALITY_MEMORY.template.md`
- `templates/QUALITY_REPORT.template.json`
- `templates/SESSION_STATE.template.md`

如果相关，再补读：

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

第一个角色：

- `Spec Architect`

必经路径：

- `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION`

下一步动作：

- 用大白话持续提问，直到 8 个本体元素和受影响工程层都能写出来

不要：

- 直接开始编码
- 太早逼用户做技术栈选择

问题路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

#### `expansion`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `<PROJECT_ROOT>/QUALITY_RULEBOOK.md`
- `<PROJECT_ROOT>/QUALITY_MEMORY.md`

如果相关，再补读：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

第一个角色：

- `Spec Architect`

必经路径：

- `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION`

下一步动作：

- 找出这个功能会改变什么、可能打破哪个现有假设，以及 FB 里还缺哪些本体或影响地图信息

不要：

- 在规格更新前就开始实现

问题路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

#### `continue`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 当前 function block
- 当前 mission block
- required reads 里列出的每个文件

必要时再读：

- `docs/05-review-recovery.md`

第一个角色：

- 如果状态健康，先由 `Builder` 接手
- 如果状态阻塞或漂移，先由 `Spec Architect` 或 `Recovery Coordinator` 接手

必经路径：

- `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION`

下一步动作：

- 明确当前阶段和下一个唯一动作

不要：

- 把整个项目重新从零开始

问题路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

#### `review`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- 相关 function block
- 相关 mission block
- 相关契约文件
- `docs/05-review-recovery.md`
- `schemas/quality-report.schema.json`

第一个角色：

- `Reviewer`

必经路径：

- `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING`

下一步动作：

- 对照书面工件和证据做审查

不要：

- 除非用户明确改变任务，否则不要在 review 阶段直接修代码

问题路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

#### `recovery`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 如果存在，读取当前 function block
- 如果存在，读取当前 mission block
- 如果存在，读取 `<PROJECT_ROOT>/VERSION_LOG.md`
- 如果存在，读取 `<PROJECT_ROOT>/QUALITY_MEMORY.md`
- `docs/05-review-recovery.md`
- 与问题区域最相关的真理源文件

第一个角色：

- `Recovery Coordinator`

必经路径：

- `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION`

下一步动作：

- 分类失败并选择最小安全动作

不要：

- 凭直觉继续实现

问题路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### 第一条回复模板

完成启动后，第一条正式回复应该包含：

1. 选中的场景
2. preflight 结果
3. 当前请求场景是否现在可以开始
4. 当前激活角色
5. 场景路径
6. 已读取文件
7. 缺失文件（如果有）
8. 下一轮问题或下一步动作

这条回复应该短而且可执行。

### 用户最小消息

这个仓库的目标是让用户可以直接用下面这种消息开场：

- `Repo: <repo-link>\nScene: greenfield`
- `Repo: <repo-link>\nScene: expansion`
- `Repo: <repo-link>\nScene: continue`
- `Repo: <repo-link>\nScene: review`
- `Repo: <repo-link>\nScene: recovery`

可选第三行：

- 产品想法
- 功能需求
- 阻塞描述
- review 目标

### 重要限制

这条规则只有在模型或工具真的能从链接或本地根目录读取仓库内容时才有效。

如果工具无法读取仓库，用户仍然需要通过下面方式提供访问：

- 给出本地路径
- 上传文件
- 或使用能够浏览该仓库的工具
