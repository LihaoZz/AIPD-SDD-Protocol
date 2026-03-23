# Mission Blocks

## Why Mission Blocks Exist

Most technical debt created by coding agents comes from unbounded tasks.

If the task is vague, the agent will:

- expand scope
- touch unrelated files
- refactor while implementing
- optimize prematurely
- declare success without proving it

Mission blocks prevent that.

---

## Required Fields

Every mission block must include all fields below.

| Field | Meaning |
| :--- | :--- |
| `id` | Stable task identifier |
| `objective` | Single concrete outcome |
| `in_scope` | Work that is allowed |
| `out_of_scope` | Work that is forbidden even if tempting |
| `allowed_files` | Files or directories the Builder may modify |
| `forbidden_files` | Files the Builder must not modify |
| `change_budget` | Maximum change surface allowed for this task |
| `dependencies` | Required artifacts or prior tasks |
| `required_artifacts` | Source-of-truth files that must be read before implementation |
| `constraints` | Rules the Builder must respect |
| `required_patterns` | Implementation patterns or conventions that must be followed |
| `acceptance_checks` | Commands, tests, and review conditions |
| `evidence_required` | What proof must be returned |
| `rollback_notes` | How to back out if the task goes wrong |

---

## Change Budget Rule

Every mission block should also declare a change budget in plain language.

Examples:

- modify at most 3 files
- no schema changes
- no new dependencies
- no cross-layer refactor
- no UI redesign

This is one of the most effective controls against AI-driven technical debt.

---

## Completion Rule

A mission block is not complete when the Builder says "done."

It is complete only when all required evidence exists:

- code changes
- test or validation output
- scope remained within the allowed boundary
- the session state was updated

---

## 中文翻译

### 为什么需要 Mission Block

编码代理制造的大多数技术债，都来自没有边界的任务。

如果任务很模糊，代理通常会：

- 擅自扩大范围
- 修改无关文件
- 在实现时顺手重构
- 过早优化
- 没有证据就宣布成功

Mission block 的作用，就是阻止这些事情发生。

### 必填字段

每个 mission block 都必须包含下面所有字段。

| 字段 | 含义 |
| :--- | :--- |
| `id` | 稳定的任务标识符 |
| `objective` | 单一、明确的任务结果 |
| `in_scope` | 允许做的工作 |
| `out_of_scope` | 即使很诱人也明确禁止做的工作 |
| `allowed_files` | Builder 允许修改的文件或目录 |
| `forbidden_files` | Builder 禁止修改的文件 |
| `change_budget` | 本任务允许的最大改动面 |
| `dependencies` | 依赖的工件或前置任务 |
| `required_artifacts` | 实现前必须先读的真理源文件 |
| `constraints` | Builder 必须遵守的规则 |
| `required_patterns` | 必须遵守的实现模式或约定 |
| `acceptance_checks` | 命令、测试和审查通过条件 |
| `evidence_required` | 必须返回的证据 |
| `rollback_notes` | 任务出问题时如何回退 |

### 改动预算规则

每个 mission block 还应该用大白话声明改动预算。

例如：

- 最多修改 3 个文件
- 不允许改 schema
- 不允许新增依赖
- 不允许跨层重构
- 不允许重新设计 UI

这是防止 AI 型技术债最有效的控制措施之一。

### 完成规则

不是 Builder 说“done”就算完成。

只有在下面这些证据都存在时，任务才算完成：

- 已有代码改动
- 已有测试或校验输出
- 实际范围没有越出允许边界
- `SESSION_STATE.md` 已更新
