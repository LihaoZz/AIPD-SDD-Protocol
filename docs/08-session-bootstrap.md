# Session Bootstrap

## Purpose

This document defines how an agent should begin work when the user provides only a repository and a scene.

The goal is to remove setup friction for a non-technical user.

The user should not need to remember:

- internal file paths
- which role goes first
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

1. map the scene
2. read the required bootstrap files
3. choose the first active role
4. tell the user what it is doing
5. ask only the next necessary questions

---

## Global Bootstrap Files

For every scene, read these first:

- `README.md`
- `docs/02-lifecycle.md`
- `docs/06-operating-playbook.md`

These files define:

- the protocol purpose
- the lifecycle stages
- the scene-specific operating flow
- the repository bootstrap rule described by `README.md`

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
- `templates/SESSION_STATE.template.md`

Read these too when relevant:

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

First role:

- `Spec Architect`

Next action:

- ask product questions in plain language

Do not:

- start coding
- ask the user to choose technical stack too early

### `expansion`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`

Read these too when relevant:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

First role:

- `Spec Architect`

Next action:

- identify what this feature changes and what current assumption it may break

Do not:

- start implementing before specs are updated

### `continue`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current mission block
- every file listed in required reads

Also read when needed:

- `docs/05-review-recovery.md`

First role:

- `Builder` if the state is healthy
- `Spec Architect` or `Recovery Coordinator` if the state is blocked or drifting

Next action:

- name the current stage and the next single action

Do not:

- restart the whole project from zero

### `review`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- relevant mission block
- relevant contract files
- `docs/05-review-recovery.md`
- `schemas/audit-result.schema.json`

First role:

- `Reviewer`

Next action:

- audit against written artifacts and evidence

Do not:

- patch code during the review pass unless the user explicitly changes the task

### `recovery`

After the global bootstrap files, read:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current mission block if it exists
- `<PROJECT_ROOT>/VERSION_LOG.md` if it exists
- `docs/05-review-recovery.md`
- relevant broken-area artifacts

First role:

- `Recovery Coordinator`

Next action:

- classify the failure and choose the smallest safe move

Do not:

- continue implementation by instinct

---

## First Reply Template

After bootstrapping, the first real reply should contain:

1. selected scene
2. active role
3. files read
4. files missing, if any
5. next questions or next action

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
- 哪些文件属于哪个场景
- 下一步应该进入哪个阶段

### 启动规则

当新对话开始时，代理应该把仓库根目录或仓库链接视为权威来源。

用户不需要再次提供 SDD 路径。

用户只需要给：

- 仓库链接或仓库根目录
- 场景

然后代理必须：

1. 识别场景
2. 读取必需启动文件
3. 选择第一个激活角色
4. 告诉用户自己正在做什么
5. 只问下一轮真正必要的问题

### 全局启动文件

无论什么场景，都先读取这些文件：

- `README.md`
- `docs/02-lifecycle.md`
- `docs/06-operating-playbook.md`

这些文件定义了：

- 协议目的
- 生命周期阶段
- 场景对应的操作流程
- 仓库启动规则

### 场景专属阅读路径

#### `greenfield`

读取全局启动文件后，再读：

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/03-artifacts.md`
- `templates/CONSTITUTION.template.md`
- `templates/SCOPE.template.md`
- `templates/DECISIONS.template.md`
- `templates/SESSION_STATE.template.md`

如果相关，再补读：

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

第一个角色：

- `Spec Architect`

下一步动作：

- 用大白话问产品问题

不要：

- 直接开始编码
- 太早逼用户做技术栈选择

#### `expansion`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`

如果相关，再补读：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

第一个角色：

- `Spec Architect`

下一步动作：

- 找出新功能会改变什么，以及它可能打破哪个现有假设

不要：

- 在规格更新前就开始实现

#### `continue`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 当前 mission block
- required reads 里列出的每个文件

必要时再读：

- `docs/05-review-recovery.md`

第一个角色：

- 如果状态健康，先由 `Builder` 接手
- 如果状态阻塞或漂移，先由 `Spec Architect` 或 `Recovery Coordinator` 接手

下一步动作：

- 明确当前阶段和下一个唯一动作

不要：

- 把整个项目重新从零开始

#### `review`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- 相关 mission block
- 相关契约文件
- `docs/05-review-recovery.md`
- `schemas/audit-result.schema.json`

第一个角色：

- `Reviewer`

下一步动作：

- 对照书面工件和证据做审查

不要：

- 除非用户明确改变任务，否则不要在 review 阶段直接修代码

#### `recovery`

读取全局启动文件后，再读：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 如果存在，读取当前 mission block
- 如果存在，读取 `<PROJECT_ROOT>/VERSION_LOG.md`
- `docs/05-review-recovery.md`
- 与问题区域最相关的真理源文件

第一个角色：

- `Recovery Coordinator`

下一步动作：

- 分类失败并选择最小安全动作

不要：

- 凭直觉继续实现

### 第一条回复模板

完成启动后，第一条正式回复应该包含：

1. 选中的场景
2. 当前激活角色
3. 已读取文件
4. 缺失文件（如果有）
5. 下一轮问题或下一步动作

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
