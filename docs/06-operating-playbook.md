# Operating Playbook

## Starting A New Project

Use this flow for a new product or feature set.

1. Ask for the product goal in plain language.
2. Ask who the end user is.
3. Ask what problem is painful enough to solve first.
4. Ask what "good enough" means for version one.
5. Ask what constraints matter: time, money, risk, privacy, platform.
6. Write initial source-of-truth artifacts.
7. Stop before implementation until the scope is written down.

---

## Adding A Feature To An Existing Project

Use this flow when the system already exists.

1. Read the current source-of-truth artifacts first.
2. Define the business reason for the change.
3. Identify which current assumptions the new feature may break.
4. Update the relevant scope, data, or API artifacts before coding.
5. Create bounded mission blocks.

---

## Continuing Interrupted Work

Use this flow when a prior session already started work.

1. Read `SESSION_STATE.md`.
1. Read `<PROJECT_ROOT>/SESSION_STATE.md`.
2. Read the active mission block.
3. Read the most relevant source-of-truth artifact for that task.
4. Confirm whether the last attempt actually succeeded, failed, or stalled.
5. Resume from the next single action instead of re-planning the whole project.

---

## Reviewing Work

Use this flow when code already exists and needs checking.

1. Read the mission block and scope first.
2. Compare implementation against contract, not against intent alone.
3. Verify evidence.
4. Report findings in structured form.
5. Fail the review if required evidence is missing.

---

## Recovering From Chaos

Use this flow when the project is confused, broken, or inconsistent.

1. Stop new implementation.
2. Identify the last known good checkpoint.
3. Classify the failure type.
4. Choose the smallest safe recovery action.
5. Update `SESSION_STATE.md`.
5. Update `<PROJECT_ROOT>/SESSION_STATE.md`.
6. Only then resume planning or implementation.

---

## Local Validation

Run the local guard script before claiming the repository is ready for handoff.

Commands:

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-review /path/to/workspace/reviews/<review-file>.json`

---

## Starting From Only Repo Plus Scene

When the repository is already available by link or local root, the user should be allowed to start with only:

- repository link or local repository root
- scene

The agent should then read:

- `README.md`
- `docs/02-lifecycle.md`
- `docs/08-session-bootstrap.md`

before asking for any additional detail.

---

## 中文翻译

### 启动一个新项目

当你从零开始一个新产品或新功能集时，使用下面流程：

1. 用大白话询问产品目标。
2. 问清终端用户是谁。
3. 问清最值得先解决的痛点是什么。
4. 问清第一版做到什么程度算“够用”。
5. 问清约束是什么：时间、金钱、风险、隐私、平台。
6. 写出初始真理源文件。
7. 在范围没有写清之前，不要进入实现。

### 给已有项目增加功能

当系统已经存在时，按下面流程处理：

1. 先读当前真理源文件。
2. 写清这次改动的业务原因。
3. 找出新功能可能打破的现有假设。
4. 在写代码之前先更新相关的范围、数据或 API 文档。
5. 创建有边界的 mission blocks。

### 继续中断的工作

当之前的会话已经开始工作时：

1. 先读 `<PROJECT_ROOT>/SESSION_STATE.md`。
2. 再读当前激活的 mission block。
3. 再读与该任务最相关的真理源文件。
4. 确认上一次尝试到底是成功、失败还是停滞。
5. 从“下一个唯一动作”继续，而不是重新规划整个项目。

### 审查工作

当代码已经存在，需要检查时：

1. 先读 mission block 和 scope。
2. 用契约对照实现，而不是只对照模糊意图。
3. 核验证据。
4. 用结构化格式报告发现。
5. 如果缺少必要证据，就判定审查失败。

### 从混乱中恢复

当项目已经混乱、损坏或前后不一致时：

1. 停止新的实现。
2. 找到最近一个已知良好的检查点。
3. 对失败类型进行分类。
4. 选择最小的安全恢复动作。
5. 更新 `<PROJECT_ROOT>/SESSION_STATE.md`。
6. 完成这些后，才恢复规划或实现。

### 本地校验

在声称仓库已经可以交接之前，先运行本地守门脚本。

命令如下：

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-review /path/to/workspace/reviews/<review-file>.json`

### 只用仓库加场景启动

当仓库已经能通过链接或本地根目录访问时，用户应该被允许只输入：

- 仓库链接或本地仓库根目录
- 场景

代理随后应先读取：

- `README.md`
- `docs/02-lifecycle.md`
- `docs/08-session-bootstrap.md`

然后再决定是否还需要额外问题。
