# Source Of Truth Artifacts

## Artifact Set

Each project should maintain the following files.

| Artifact | Purpose | Owner | Required |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | Product intent, architecture boundaries, stack choices, and non-negotiables | Spec Architect | Yes |
| `<PROJECT_ROOT>/SCOPE.md` | Current user-facing scope and acceptance definition | Spec Architect | Yes |
| `<PROJECT_ROOT>/DECISIONS.md` | Important decisions and why alternatives were rejected | Spec Architect | Yes |
| `<PROJECT_ROOT>/SESSION_STATE.md` | Current stage, current FB, current MB, latest blocker, and next action | Builder updates under protocol | Yes |
| `<PROJECT_ROOT>/QUALITY_RULEBOOK.md` | Global quality profiles, quality checks, and waiver policy | Spec Architect | Yes |
| `<PROJECT_ROOT>/QUALITY_MEMORY.md` | Reusable lessons, repeated failures, and high-risk reminders | Builder and Reviewer | Yes |
| `<PROJECT_ROOT>/DATA_MODEL.md` | Core entities, relationships, and persistence rules | Spec Architect | Usually |
| `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml` | API behavior and payload rules | Spec Architect | If APIs exist |
| `<PROJECT_ROOT>/VERSION_LOG.md` | Important checkpoints and rollback references | Builder | Recommended |
| `<PROJECT_ROOT>/function_blocks/*.md` | Product-level feature delivery units with ontology frame, impact map, acceptance, and MB history | Spec Architect | Yes before scene planning finishes |
| `<PROJECT_ROOT>/missions/*.md` | Bounded code change units under one active FB with declared ontology and layer slice | Spec Architect or Builder | Yes before `BUILD` |
| `<PROJECT_ROOT>/reviews/*.json` | Evidence-based quality reports that match the quality report schema | Reviewer | Yes before `CLOSE` |

---

## Ownership Rule

The Builder may read all source-of-truth artifacts.

The Builder may not freely rewrite them during implementation. If implementation reveals a mismatch, the Builder must raise a spec conflict rather than silently change the contract.

Allowed cases for artifact changes:

- the active FB or MB explicitly authorizes the update
- the session is in `SPEC` stage
- the session is in `recovery` and the recovery plan requires documentation repair
- the session writes a quality lesson into `QUALITY_MEMORY.md`

---

## Session State Rule

`<PROJECT_ROOT>/SESSION_STATE.md` is the minimum restart file.

It should always answer:

- which mode the project is in
- which stage the work is in
- which function block is active
- which mission block is active
- what was completed
- what failed
- what the next single action is
- which artifacts must be read first

Without this file, every new conversation will waste time reconstructing context and may drift.

---

## FB, MB, And Quality Report Storage

Function blocks should live in `<PROJECT_ROOT>/function_blocks/`.

Mission blocks should live in `<PROJECT_ROOT>/missions/`.

Quality reports should live in `<PROJECT_ROOT>/reviews/`.

Keeping them inside the real project root makes it easier to preserve history while keeping the latest source-of-truth files close to the implementation.

Each mission block should inherit from its parent FB instead of copying the full ontology frame.

---

## Function Block Content Rule

An `FB` is not only a feature note.

It should contain:

- the product goal
- an 8-element ontology frame
- an 8-layer impact map
- scope and acceptance
- the MB plan and history

The ontology frame answers what the function is.

The impact map answers where the function must be implemented, updated, or validated.

The discovery flow should reach this content before detailed FB planning begins.

---

## 中文翻译

### 真理源文件集合

每个项目都应该维护下面这些文件。

| 文件 | 用途 | 所有者 | 是否必须 |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | 记录产品意图、架构边界、技术栈选择和不可违反项 | Spec Architect | 是 |
| `<PROJECT_ROOT>/SCOPE.md` | 记录当前用户可见范围和验收定义 | Spec Architect | 是 |
| `<PROJECT_ROOT>/DECISIONS.md` | 记录重要决策及放弃其他方案的原因 | Spec Architect | 是 |
| `<PROJECT_ROOT>/SESSION_STATE.md` | 记录当前阶段、当前 FB、当前 MB、最新阻塞和下一步动作 | Builder 按协议更新 | 是 |
| `<PROJECT_ROOT>/QUALITY_RULEBOOK.md` | 记录全局质量档位、检查项目和豁免规则 | Spec Architect | 是 |
| `<PROJECT_ROOT>/QUALITY_MEMORY.md` | 记录可复用经验、重复失败和高风险提醒 | Builder 和 Reviewer | 是 |
| `<PROJECT_ROOT>/DATA_MODEL.md` | 记录核心实体、关系和持久化规则 | Spec Architect | 通常需要 |
| `<PROJECT_ROOT>/API_CONTRACT.md` 或 `<PROJECT_ROOT>/openapi.yaml` | 记录 API 行为和载荷规则 | Spec Architect | 有 API 时需要 |
| `<PROJECT_ROOT>/VERSION_LOG.md` | 记录重要检查点和回滚参考 | Builder | 推荐 |
| `<PROJECT_ROOT>/function_blocks/*.md` | 记录产品级功能交付单元的本体框架、影响地图、验收和 MB 历史 | Spec Architect | 场景规划结束前必须存在 |
| `<PROJECT_ROOT>/missions/*.md` | 记录某个 FB 下有边界的代码改动单元，并声明本体与影响层切片 | Spec Architect 或 Builder | 进入 `BUILD` 前必须存在 |
| `<PROJECT_ROOT>/reviews/*.json` | 记录符合质量报告 schema 的证据型质量报告 | Reviewer | `CLOSE` 前必须存在 |

### 所有权规则

Builder 可以读取所有真理源文件。

但 Builder 不能在实现过程中随意重写这些文件。如果实现暴露出不匹配，Builder 必须提出规格冲突，而不是悄悄改写契约。

允许改动真理源文件的情况只有：

- 当前激活的 FB 或 MB 明确授权更新
- 当前会话处于 `SPEC` 阶段
- 当前会话处于 `recovery`，且恢复计划要求修正文档
- 当前会话需要把质量经验写入 `QUALITY_MEMORY.md`

### 会话状态规则

`<PROJECT_ROOT>/SESSION_STATE.md` 是最小可恢复文件。

它应该始终回答这些问题：

- 当前项目处于哪种模式
- 当前工作处于哪个阶段
- 当前激活的是哪个 function block
- 当前激活的是哪个 mission block
- 已经完成了什么
- 失败了什么
- 下一个唯一动作是什么
- 接手前必须先读哪些文件

没有这个文件，每次新会话都会浪费时间重建上下文，而且很容易漂移。

### FB、MB 和质量报告的存放位置

Function block 应该放在 `<PROJECT_ROOT>/function_blocks/`。

Mission block 应该放在 `<PROJECT_ROOT>/missions/`。

质量报告应该放在 `<PROJECT_ROOT>/reviews/`。

把它们放在真实项目根目录里，更容易让项目状态与实际实现保持同步。

每个 mission block 都应继承父 FB，而不是复制一份完整本体框架。

### Function Block 内容规则

`FB` 不只是功能说明条目。

它应包含：

- 产品目标
- 8 元素本体框架
- 8 层影响地图
- 范围和验收定义
- MB 计划与历史

本体框架回答“这个功能是什么”。

影响地图回答“这个功能必须落到哪些工程层去实现、更新或验证”。

discovery 应先达到这个粒度，再进入详细 FB 规划。
