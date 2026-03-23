# SDD Protocol Repository

## What This Repository Is

This repository is a protocol system for AI-assisted product development.

It is not the project itself.

It stores:

- the operating rules
- the lifecycle
- the role prompts
- the templates
- the validation tools

Real project state does not live in this repository. It lives in the real project root chosen by the user.

---

## Core Idea

Less is more. Always keep it simple.

This idea applies everywhere:

- prefer the smallest useful scope
- prefer the fewest moving parts
- prefer the smallest safe change
- prefer the clearest document
- prefer the most direct solution that can be verified

Do not add complexity to look complete.

---

## Two Roots

This protocol assumes two different roots:

- `PROTOCOL_ROOT`
  This repository. It contains the rules, prompts, templates, schemas, and scripts.
- `PROJECT_ROOT`
  The real product workspace. It contains the generated source-of-truth files and the actual implementation work.

The model must keep these two roots separate.

---

## The Only Startup Rule

This `README.md` is the only main entry.

When a new conversation starts, the agent should read this file first.

The user should be allowed to start with only:

1. repository link or local protocol root
2. scene

Optional third input:

- product idea
- feature request
- blocker
- review target
- project root path if the current workspace is not already the real project

If `PROJECT_ROOT` is not explicitly given, the agent should treat the current real working project directory as `PROJECT_ROOT`.

Do not ask the user to restate internal protocol document paths.

---

## Scenes

Supported scenes:

- `greenfield`
- `expansion`
- `continue`
- `review`
- `recovery`

If the user gives a fuzzy label, map it to the nearest scene before continuing.

Examples:

- "start a new app" -> `greenfield`
- "add a feature" -> `expansion`
- "continue yesterday's work" -> `continue`
- "review this work" -> `review`
- "the project is broken" -> `recovery`

---

## Automatic Reading Path

After reading this `README.md`, the agent should route itself like this.

### `greenfield`

First active role:

- `Spec Architect`

Read next:

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/06-operating-playbook.md`
- `templates/CONSTITUTION.template.md`
- `templates/SCOPE.template.md`
- `templates/DECISIONS.template.md`
- `templates/SESSION_STATE.template.md`

Add these when relevant:

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

Then:

- enter `INIT`
- enter `DISCOVERY`
- ask only business questions first
- generate project files in `PROJECT_ROOT`
- do not enter `BUILD`

### `expansion`

First active role:

- `Spec Architect`

Read next:

- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `docs/06-operating-playbook.md`
- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

Add these when relevant:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

Then:

- identify what assumption the new feature may break
- update specs before implementation

### `continue`

First active role:

- `Builder` if state is healthy
- `Spec Architect` or `Recovery Coordinator` if state is blocked or drifting

Read next:

- `docs/02-lifecycle.md`
- `docs/05-review-recovery.md` when needed
- `docs/06-operating-playbook.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- current mission block named by `active_mission_block`
- every file listed under required reads

Then:

- name the current stage
- name the next single action
- do not restart the project from zero

### `review`

First active role:

- `Reviewer`

Read next:

- `docs/05-review-recovery.md`
- `schemas/audit-result.schema.json`
- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- relevant mission block
- relevant contract files

Then:

- review against written artifacts
- return a structured result
- do not silently fix code during the review pass

### `recovery`

First active role:

- `Recovery Coordinator`

Read next:

- `docs/05-review-recovery.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- current mission block if one exists
- `<PROJECT_ROOT>/VERSION_LOG.md` if it exists
- relevant broken-area artifacts

Then:

- classify the failure
- choose the smallest safe move
- update session state before new implementation begins

---

## Files Created In The Real Project

The protocol repository does not keep live project state.

The agent should create and maintain these files in `PROJECT_ROOT`:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `<PROJECT_ROOT>/DATA_MODEL.md` when needed
- `<PROJECT_ROOT>/API_CONTRACT.md` when needed
- `<PROJECT_ROOT>/VERSION_LOG.md` when needed
- `<PROJECT_ROOT>/missions/`
- `<PROJECT_ROOT>/reviews/`

These are generated into the real project during execution.

---

## First Reply Contract

After bootstrapping, the first substantive reply should contain:

1. selected scene
2. active role
3. `PROJECT_ROOT`
4. files read
5. missing files, if any
6. next questions or next action

The first reply should be short and operational.

---

## Validation

Protocol repository validation:

- `python3 scripts/sdd_guard.py check-protocol`

External project validation:

- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-review /path/to/workspace/reviews/<review-file>.json`
- `python3 scripts/sdd_guard.py check-all /path/to/project`

---

## Detailed References

Use these only after reading this file:

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `docs/05-review-recovery.md`
- `docs/06-operating-playbook.md`
- `docs/07-repository-layout.md`
- `docs/08-session-bootstrap.md`
- `docs/SDD_MASTER_PROTOCOL_V4.md`

---

## 中文翻译

### 这个仓库是什么

这个仓库是一套面向 AI 产品开发的协议系统。

它不是你的真实项目本身。

这里保存的是：

- 运行规则
- 生命周期
- 角色提示词
- 模板
- 校验工具

真实项目状态不保存在这个仓库里，而是保存在用户选择的真实项目根目录中。

### 核心思想

少即是多。永远保持简单。

这条思想适用于所有地方：

- 优先最小有用范围
- 优先最少运动部件
- 优先最小但安全的改动
- 优先最清晰的文档
- 优先最直接且可验证的方案

不要为了“看起来完整”而增加复杂度。

### 两个根目录

这套协议默认存在两个不同的根目录：

- `PROTOCOL_ROOT`
  也就是这个仓库。它保存规则、提示词、模板、schema 和脚本。
- `PROJECT_ROOT`
  真实产品工作区。它保存真实项目的真理源文件和实际实现内容。

模型必须清楚区分这两个根目录。

### 唯一启动规则

这个 `README.md` 是唯一主入口。

当新对话开始时，代理应该先读取这个文件。

用户应该只需要提供：

1. 仓库链接或本地协议根目录
2. 场景

可选第三项输入：

- 产品想法
- 功能需求
- 阻塞描述
- review 目标
- 如果当前工作区不是实际项目，再额外给项目根目录路径

如果没有明确给出 `PROJECT_ROOT`，代理应把当前真实工作项目目录视为 `PROJECT_ROOT`。

不要再要求用户重复输入内部协议文档路径。

### 场景

支持的场景有：

- `greenfield`
- `expansion`
- `continue`
- `review`
- `recovery`

如果用户给的是模糊描述，先映射到最接近的场景。

例如：

- “开始做一个新 app” -> `greenfield`
- “加一个新功能” -> `expansion`
- “继续昨天的工作” -> `continue`
- “审查这次工作” -> `review`
- “项目坏了/很乱” -> `recovery`

### 自动阅读路径

代理读完本 `README.md` 后，应按下面规则自动路由。

#### `greenfield`

第一个激活角色：

- `Spec Architect`

接着读取：

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/06-operating-playbook.md`
- `templates/CONSTITUTION.template.md`
- `templates/SCOPE.template.md`
- `templates/DECISIONS.template.md`
- `templates/SESSION_STATE.template.md`

如果相关，再补读：

- `templates/DATA_MODEL.template.md`
- `templates/API_CONTRACT.template.md`

然后：

- 进入 `INIT`
- 进入 `DISCOVERY`
- 先只问业务问题
- 在 `PROJECT_ROOT` 中生成项目文件
- 不要进入 `BUILD`

#### `expansion`

第一个激活角色：

- `Spec Architect`

接着读取：

- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `docs/06-operating-playbook.md`
- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

如果相关，再补读：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

然后：

- 找出新功能可能打破哪个已有假设
- 先更新规格，再进入实现

#### `continue`

第一个激活角色：

- 如果状态健康，先由 `Builder` 接手
- 如果状态阻塞或漂移，先由 `Spec Architect` 或 `Recovery Coordinator` 接手

接着读取：

- `docs/02-lifecycle.md`
- 必要时读取 `docs/05-review-recovery.md`
- `docs/06-operating-playbook.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `active_mission_block` 指向的当前任务块
- required reads 中列出的每个文件

然后：

- 明确当前阶段
- 明确下一个唯一动作
- 不要把项目重新从零启动

#### `review`

第一个激活角色：

- `Reviewer`

接着读取：

- `docs/05-review-recovery.md`
- `schemas/audit-result.schema.json`
- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- 相关 mission block
- 相关契约文件

然后：

- 对照书面工件进行审查
- 返回结构化结果
- 在 review 阶段不要静默修代码

#### `recovery`

第一个激活角色：

- `Recovery Coordinator`

接着读取：

- `docs/05-review-recovery.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- 如果存在，读取当前 mission block
- 如果存在，读取 `<PROJECT_ROOT>/VERSION_LOG.md`
- 与问题区域相关的工件

然后：

- 对失败进行分类
- 选择最小安全动作
- 在恢复实现前先更新 session state

### 真实项目中生成的文件

协议仓库不再保存实时项目状态。

代理应在 `PROJECT_ROOT` 中创建和维护这些文件：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- 如果需要，再生成 `<PROJECT_ROOT>/DATA_MODEL.md`
- 如果需要，再生成 `<PROJECT_ROOT>/API_CONTRACT.md`
- 如果需要，再生成 `<PROJECT_ROOT>/VERSION_LOG.md`
- `<PROJECT_ROOT>/missions/`
- `<PROJECT_ROOT>/reviews/`

这些文件会在真实开发过程中生成到实际项目根目录中。

### 第一条回复契约

完成启动后，第一条正式回复应该包含：

1. 当前选中的场景
2. 当前激活角色
3. `PROJECT_ROOT`
4. 已读取文件
5. 缺失文件（如果有）
6. 下一轮问题或下一步动作

第一条回复应简短且可执行。

### 校验

协议仓库校验：

- `python3 scripts/sdd_guard.py check-protocol`

外部项目校验：

- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-review /path/to/workspace/reviews/<review-file>.json`
- `python3 scripts/sdd_guard.py check-all /path/to/project`

### 详细参考

只有在读完本文件之后，再去看这些细节文档：

- `docs/00-roadmap.md`
- `docs/01-principles.md`
- `docs/02-lifecycle.md`
- `docs/03-artifacts.md`
- `docs/04-mission-blocks.md`
- `docs/05-review-recovery.md`
- `docs/06-operating-playbook.md`
- `docs/07-repository-layout.md`
- `docs/08-session-bootstrap.md`
- `docs/SDD_MASTER_PROTOCOL_V4.md`
