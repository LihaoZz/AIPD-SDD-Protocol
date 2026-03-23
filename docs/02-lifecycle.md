# Lifecycle

## Session Modes

Use one mode per session.

| Mode | Use When | Required Inputs | Expected Output |
| :--- | :--- | :--- | :--- |
| `greenfield` | Starting a new product or feature set | Business goal, user problem, constraints if known | Initial specs and roadmap |
| `expansion` | Adding a new capability to an existing system | Existing source-of-truth docs plus the new goal | Delta spec and mission plan |
| `continue` | Resuming interrupted work | Current session state, latest mission block, failure or progress notes | Next bounded action |
| `review` | Auditing completed implementation | Diff, test evidence, and relevant source-of-truth docs | Structured audit result |
| `recovery` | Fixing a broken or confused state | Error evidence, recent changes, and session state | Recovery path with smallest safe move |

---

## Required Stages

Do not skip stages.

| Stage | Purpose | Exit Criteria |
| :--- | :--- | :--- |
| `INIT` | Identify mode, project, and active source-of-truth files | Mode and file set are explicit |
| `DISCOVERY` | Reduce ambiguity through targeted questions | Facts, assumptions, risks, and unknowns are written down |
| `SPEC` | Produce or update source-of-truth artifacts | User approves the written spec direction |
| `PLAN` | Create bounded mission blocks | Each task has scope, files, and acceptance checks |
| `BUILD` | Implement one mission block | Evidence for the task exists |
| `REVIEW` | Validate the task and system impact | Review result is pass or fail with findings |
| `CLOSE` | Persist current state for later sessions | Session state and next step are written |

---

## Discovery Exit Rule

`DISCOVERY` does not end when the model has asked "enough questions."

It ends when the protocol can write four lists:

1. confirmed facts
2. assumptions being taken
3. unresolved risks
4. items intentionally out of scope

If those four lists are weak, more questions are needed.

---

## Handoff Rule

The Builder must not start from raw chat history.

The Builder starts only after reading:

- project constitution
- relevant feature or scope spec
- current mission block
- current session state

If one of those is missing, the Builder must stop and ask for the missing artifact rather than infer it.

---

## Bootstrap Rule

If the user starts with only a repository and a scene, the agent must not ask for the SDD path again.

Instead, the agent must:

1. read the repository bootstrap files
2. map the scene
3. read the scene-specific files
4. activate the first appropriate role
5. tell the user what happens next

See `README.md` and `docs/08-session-bootstrap.md`.
See `README.md` and `docs/08-session-bootstrap.md`.

---

## 中文翻译

### 会话模式

每次会话只使用一种主模式。

| 模式 | 何时使用 | 必需输入 | 预期输出 |
| :--- | :--- | :--- | :--- |
| `greenfield` | 从零开始一个新产品或新功能集 | 业务目标、用户问题，以及已知约束 | 初始规格和路线图 |
| `expansion` | 给现有系统增加新能力 | 现有真理源文档加上新的目标 | 差异规格和任务计划 |
| `continue` | 继续中断的工作 | 当前会话状态、最新 mission block、失败或进展记录 | 下一个有边界的动作 |
| `review` | 审查已经完成的实现 | diff、测试证据和相关真理源文档 | 结构化审查结果 |
| `recovery` | 修复损坏或混乱状态 | 错误证据、最近变更和会话状态 | 最小安全恢复路径 |

### 必经阶段

不要跳过阶段。

| 阶段 | 目的 | 退出条件 |
| :--- | :--- | :--- |
| `INIT` | 确认模式、项目和当前激活的真理源文件 | 模式和文件集合已明确 |
| `DISCOVERY` | 通过定向提问降低模糊性 | 事实、假设、风险和未知项已写下 |
| `SPEC` | 产出或更新真理源文件 | 用户认可写下来的规格方向 |
| `PLAN` | 创建带边界的 mission blocks | 每个任务都有范围、文件边界和验收检查 |
| `BUILD` | 实现一个 mission block | 该任务的证据已经存在 |
| `REVIEW` | 验证任务及系统影响 | 审查结果已给出通过或失败及发现 |
| `CLOSE` | 为后续会话保存当前状态 | 会话状态和下一步已写下 |

### Discovery 的退出规则

`DISCOVERY` 不是在模型觉得“问题问够了”时结束。

它结束于协议能够写出四张清单：

1. 已确认事实
2. 当前采用的假设
3. 未解决风险
4. 明确不做的范围外事项

如果这四张清单写得很弱，就说明还需要继续提问。

### 交接规则

Builder 不能从原始聊天记录直接开工。

Builder 只有在读过以下内容后才能开始：

- 项目宪章
- 相关功能规格或范围文档
- 当前 mission block
- 当前会话状态

如果其中任意一个缺失，Builder 必须停下并要求补齐，而不是自行推断。

### 启动规则

如果用户开场时只给了“仓库”和“场景”，代理不应再要求重复提供 SDD 路径。

代理应当：

1. 读取仓库启动文件
2. 映射场景
3. 读取场景专属文件
4. 激活第一个合适角色
5. 告诉用户接下来要发生什么

详见 `README.md` 和 `docs/08-session-bootstrap.md`。
