# Source Of Truth Artifacts

## Artifact Set

Each project should maintain the following files.

| Artifact | Purpose | Owner | Required |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | Product intent, architecture boundaries, stack choices, and non-negotiables | Spec Architect | Yes |
| `<PROJECT_ROOT>/SCOPE.md` | Current user-facing scope and acceptance definition | Spec Architect | Yes |
| `<PROJECT_ROOT>/DECISIONS.md` | Important decisions and why alternatives were rejected | Spec Architect | Yes |
| `<PROJECT_ROOT>/DATA_MODEL.md` | Core entities, relationships, and persistence rules | Spec Architect | Usually |
| `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml` | API behavior and payload rules | Spec Architect | If APIs exist |
| `<PROJECT_ROOT>/SESSION_STATE.md` | Current stage, current task, latest blocker, next action | Builder updates under protocol | Yes |
| `<PROJECT_ROOT>/VERSION_LOG.md` | Important checkpoints and rollback references | Builder | Recommended |
| `<PROJECT_ROOT>/missions/*.md` | Bounded implementation tasks with allowed and forbidden change surfaces | Spec Architect or Planner | Yes before `BUILD` |
| `<PROJECT_ROOT>/reviews/*.json` | Evidence-based review outputs that match the audit schema | Reviewer | Recommended |

---

## Ownership Rule

The Builder may read all source-of-truth artifacts.

The Builder may not freely rewrite them during implementation. If implementation reveals a mismatch, the Builder must raise a spec conflict rather than silently change the contract.

Allowed cases for artifact changes:

- the mission block explicitly authorizes a contract update
- the session is in `SPEC` stage
- the session is in `recovery` and the recovery plan requires documentation repair

---

## Session State Rule

`<PROJECT_ROOT>/SESSION_STATE.md` is the minimum restart file.

It should always answer:

- which mode the project is in
- which stage the work is in
- which mission block is active
- what was completed
- what failed
- what the next single action is
- which artifacts must be read first

Without this file, every new conversation will waste time reconstructing context and may drift.

---

## Mission And Review Storage

Mission blocks should live in `<PROJECT_ROOT>/missions/`.

Reviews should live in `<PROJECT_ROOT>/reviews/`.

Keeping them inside the real project root makes it easier to preserve history while keeping the latest source-of-truth files close to the implementation.

---

## 中文翻译

### 真理源文件集合

每个项目都应该维护下面这些文件。

| 文件 | 用途 | 所有者 | 是否必须 |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | 记录产品意图、架构边界、技术栈选择和不可违反项 | Spec Architect | 是 |
| `<PROJECT_ROOT>/SCOPE.md` | 记录当前用户可见范围和验收定义 | Spec Architect | 是 |
| `<PROJECT_ROOT>/DECISIONS.md` | 记录重要决策及放弃其他方案的原因 | Spec Architect | 是 |
| `<PROJECT_ROOT>/DATA_MODEL.md` | 记录核心实体、关系和持久化规则 | Spec Architect | 通常需要 |
| `<PROJECT_ROOT>/API_CONTRACT.md` 或 `<PROJECT_ROOT>/openapi.yaml` | 记录 API 行为和载荷规则 | Spec Architect | 有 API 时需要 |
| `<PROJECT_ROOT>/SESSION_STATE.md` | 记录当前阶段、当前任务、最新阻塞和下一步动作 | Builder 按协议更新 | 是 |
| `<PROJECT_ROOT>/VERSION_LOG.md` | 记录重要检查点和回滚参考 | Builder | 推荐 |
| `<PROJECT_ROOT>/missions/*.md` | 记录带允许/禁止变更面的有边界实现任务 | Spec Architect 或 Planner | 进入 `BUILD` 前需要 |
| `<PROJECT_ROOT>/reviews/*.json` | 记录符合审查 schema 的证据型审查结果 | Reviewer | 推荐 |

### 所有权规则

Builder 可以读取所有真理源文件。

但 Builder 不能在实现过程中随意重写这些文件。如果实现暴露出不匹配，Builder 必须提出规格冲突，而不是悄悄改写契约。

允许改动真理源文件的情况只有：

- 当前 mission block 明确授权更新契约
- 当前会话处于 `SPEC` 阶段
- 当前会话处于 `recovery`，且恢复计划要求修正文档

### 会话状态规则

`<PROJECT_ROOT>/SESSION_STATE.md` 是最小可恢复文件。

它应该始终回答这些问题：

- 当前项目处于哪种模式
- 当前工作处于哪个阶段
- 当前激活的是哪个 mission block
- 已经完成了什么
- 失败了什么
- 下一个唯一动作是什么
- 接手前必须先读哪些文件

没有这个文件，每次新会话都会浪费时间重建上下文，而且很容易漂移。

### 任务和审查的存放位置

Mission block 应该放在 `<PROJECT_ROOT>/missions/`。

Review 结果应该放在 `<PROJECT_ROOT>/reviews/`。

把它们放在真实项目根目录里，更容易让项目状态与实际实现保持同步。
