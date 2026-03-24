# Operating Playbook

## Project Preflight

Use this flow at the start of every new conversation.

1. Identify the working path and requested scene.
2. Check foundational files and directories.
3. Check scene-specific requirements.
4. Return a short preflight summary to the user.
5. Classify the result as `ready`, `bootstrap_required`, or `blocked`.
6. If the result is `bootstrap_required`, initialize safe foundational files before entering the scene.
7. If the result is `blocked`, route the problem to the owning role and ask only for the minimum missing context.

---

## Four-Layer Operating Logic

Use this order in every scene:

1. `Preflight`
2. `Scene Path`
3. `Role Handoff`
4. `Issue Routing` when a problem is found

Interpret the layers like this:

- `Preflight`: can the requested scene safely start
- `Scene Path`: what sequence of work applies to this scene
- `Role Handoff`: who owns the next normal step
- `Issue Routing`: who must resolve a discovered problem

Do not let a scene path erase role separation.

---

## Scene Templates

For each scene, define these six blocks:

1. `Purpose`
2. `Required Path`
3. `Working Focus`
4. `Required Outputs`
5. `Role Handoffs`
6. `Issue Routing`

---

## FB Ontology Frame And Impact Map

Use this distinction before detailed FB planning:

- `8-element ontology frame`: what the function is
- `8-layer impact map`: where the function lands in engineering

The ontology frame should cover:

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

The impact map should cover:

- business
- domain
- flow
- experience
- application
- service
- data
- quality

Do not write a detailed FB until both are covered.

---

## Greenfield

Purpose:
create initial truth, quality rules, and the first FB plan for a new product or feature set.

Required path:
`DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION`

Working focus:

- product goal
- user value
- version-one boundary
- initial quality system
- first function blocks

Required outputs:

- initial source-of-truth artifacts
- initial quality files
- first FB ontology frames
- first FB impact maps
- first bounded FBs
- planned MBs with ontology and layer slices

Role handoffs:

- start with `Spec Architect`
- hand off to `Builder` only after discovery, spec, quality setup, and FB planning are complete, and the user agrees to implementation
- hand off from `Builder` to `Reviewer` after one MB is finished and evidence exists

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## Expansion

Purpose:
add one new feature to an existing project without losing clarity about impact or regression risk.

Required path:
`FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION`

Working focus:

- why the new feature matters
- what existing assumptions it may break
- what current paths may regress
- the function's 8 ontology elements
- what a detailed FB must contain before coding begins

Required outputs:

- updated source-of-truth artifacts
- one covered FB ontology frame
- one covered FB impact map
- one detailed new FB
- first planned MBs under that FB
- planned MBs with ontology and layer slices

Role handoffs:

- start with `Spec Architect`
- hand off to `Builder` only after the new feature has enough detail to form a bounded FB and MB plan, and the user agrees to implementation
- hand off from `Builder` to `Reviewer` after each completed MB

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## Continue

Purpose:
reconstruct state and continue the next single safe action instead of restarting the project.

Required path:
`STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION`

Working focus:

- what the active FB and MB are
- whether the previous step succeeded, failed, or stalled
- what the one next safe action is

Required outputs:

- updated `SESSION_STATE.md`
- the next bounded action

Role handoffs:

- start with `Builder` when state is healthy
- start with `Spec Architect` when the state is understandable but task intent is unclear
- start with `Recovery Coordinator` when state is drifting or broken
- hand off to `Reviewer` after an MB is finished and evidence exists

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## Review

Purpose:
audit implementation against FB, MB, source-of-truth artifacts, and quality evidence.

Required path:
`AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING`

Working focus:

- compare code to written artifacts
- verify evidence
- classify findings by ownership

Required outputs:

- one structured quality report
- findings with next required actions

Role handoffs:

- start with `Reviewer`
- do not hand off to `Builder` or `Spec Architect` automatically unless the user changes the task

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## Recovery

Purpose:
stop drift, classify the failure, repair state, and restore a safe next move.

Required path:
`FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION`

Working focus:

- last known good checkpoint
- failure class
- smallest safe recovery move

Required outputs:

- repaired session truth
- recommended next role and next action

Role handoffs:

- start with `Recovery Coordinator`
- hand off to `Spec Architect` if the root cause is a spec problem
- hand off to `Builder` if the root cause is an implementation or evidence problem
- hand off to `Reviewer` after recovery only when revalidation is the next safe step

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` or `environment_issue` -> `Recovery Coordinator`

---

## Ownership-Based Issue Routing

Use this rule everywhere, including preflight.

| Issue Type | Route To |
| :--- | :--- |
| `spec_gap` | `Spec Architect` |
| `implementation_bug` | `Builder` |
| `quality_evidence_gap` | `Builder` |
| `state_drift` | `Recovery Coordinator` |
| `environment_issue` | `Recovery Coordinator` |
| `review_context_gap` | current scene lead role |

---

## Local Validation

Run the local guard script before claiming the repository is ready for handoff.

Commands:

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`

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

### Project Preflight

每次新对话开始时，都先按下面流程执行：

1. 确认工作路径和请求场景。
2. 检查基础文件和目录。
3. 检查场景专属要求。
4. 先向用户返回一份简短的 preflight summary。
5. 将结果分类为 `ready`、`bootstrap_required` 或 `blocked`。
6. 如果结果是 `bootstrap_required`，先自动补齐安全的基础制度文件，再进入场景。
7. 如果结果是 `blocked`，按责任归因路由问题，并只询问最小必要缺失信息。

### 四层运行逻辑

每个场景都按下面顺序工作：

1. `Preflight`
2. `Scene Path`
3. `Role Handoff`
4. 发现问题时进入 `Issue Routing`

这四层的含义分别是：

- `Preflight`：请求场景现在能不能安全开始
- `Scene Path`：这个场景该走哪条工作序列
- `Role Handoff`：正常推进中的下一步由谁负责
- `Issue Routing`：发现问题后由谁来解决

不要让场景路径吞掉角色分离。

### 场景模板

每个场景都应固定写出这 6 个块：

1. `Purpose`
2. `Required Path`
3. `Working Focus`
4. `Required Outputs`
5. `Role Handoffs`
6. `Issue Routing`

### FB 本体框架与影响地图

在进入详细 FB 规划之前，先区分这两个东西：

- `8 元素本体框架`：功能本身是什么
- `8 层影响地图`：功能会落到哪些工程层

本体框架应覆盖：

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

影响地图应覆盖：

- business
- domain
- flow
- experience
- application
- service
- data
- quality

只有当两者都被覆盖后，才进入详细 FB 编写。

### Greenfield

Purpose:
为新产品或新功能集建立初始真理源、质量制度和首批 FB 计划。

Required path:
`DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION`

Working focus:

- 产品目标
- 用户价值
- 第一版边界
- 初始质量制度
- 首批 function blocks

Required outputs:

- 初始真理源工件
- 初始质量文件
- 第一批 FB 本体框架
- 第一批 FB 影响地图
- 第一批有边界的 FB
- 带本体和影响层切片的计划 MB

Role handoffs:

- 先由 `Spec Architect` 主导
- 只有在 discovery、spec、quality setup 和 FB planning 完成，且用户同意实现后，才交给 `Builder`
- `Builder` 完成一个 MB 且证据存在后，再交给 `Reviewer`

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### Expansion

Purpose:
给已有项目增加一个新功能，同时保持影响分析和回归风险清晰。

Required path:
`FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION`

Working focus:

- 新功能为什么重要
- 它可能打破哪些现有假设
- 哪些旧路径可能回归
- 该功能的 8 个本体元素
- 编码前详细 FB 需要写到什么程度

Required outputs:

- 更新后的真理源工件
- 一个已覆盖的 FB 本体框架
- 一个已覆盖的 FB 影响地图
- 一个新的详细 FB
- 该 FB 下的首批计划 MB
- 带本体和影响层切片的计划 MB

Role handoffs:

- 先由 `Spec Architect` 主导
- 只有当新功能信息足以形成有边界的 FB 和 MB 计划，且用户同意实现后，才交给 `Builder`
- 每个完成的 MB 都应从 `Builder` 交给 `Reviewer`

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### Continue

Purpose:
重建状态并继续下一个唯一安全动作，而不是从头再规划。

Required path:
`STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION`

Working focus:

- 当前激活的 FB 和 MB 是什么
- 上一步是成功、失败还是停滞
- 下一个唯一安全动作是什么

Required outputs:

- 更新后的 `SESSION_STATE.md`
- 下一个有边界的动作

Role handoffs:

- 状态健康时，先由 `Builder` 接手
- 状态可读但任务意图不清时，先由 `Spec Architect` 接手
- 状态漂移或损坏时，先由 `Recovery Coordinator` 接手
- MB 完成且证据存在后，再交给 `Reviewer`

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### Review

Purpose:
对照 FB、MB、真理源工件和质量证据审计当前实现。

Required path:
`AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING`

Working focus:

- 对照书面工件审查代码
- 核验证据
- 按责任归因分类发现

Required outputs:

- 一份结构化质量报告
- 带后续动作的发现列表

Role handoffs:

- 先由 `Reviewer` 主导
- 除非用户明确改变任务，否则不要自动切给 `Builder` 或 `Spec Architect`

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### Recovery

Purpose:
停止漂移、分类失败、修复状态，并恢复到可安全继续的下一步。

Required path:
`FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION`

Working focus:

- 最近一个已知良好的检查点
- 失败类别
- 最小安全恢复动作

Required outputs:

- 修复后的会话真理源
- 推荐的下一角色和下一动作

Role handoffs:

- 先由 `Recovery Coordinator` 主导
- 如果根因是规格问题，交给 `Spec Architect`
- 如果根因是实现或证据问题，交给 `Builder`
- 只有在恢复后下一步是重新验证时，才交给 `Reviewer`

Issue routing:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` 或 `environment_issue` -> `Recovery Coordinator`

### 按责任归因的问题路由

包括 preflight 在内的所有节点，都使用同一套路由规则。

| 问题类型 | 路由到 |
| :--- | :--- |
| `spec_gap` | `Spec Architect` |
| `implementation_bug` | `Builder` |
| `quality_evidence_gap` | `Builder` |
| `state_drift` | `Recovery Coordinator` |
| `environment_issue` | `Recovery Coordinator` |
| `review_context_gap` | 当前场景主导角色 |

### 本地校验

在声称仓库已经可以交接之前，先运行本地守门脚本。

命令如下：

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`

### 只用仓库加场景启动

当仓库已经能通过链接或本地根目录访问时，用户应该被允许只输入：

- 仓库链接或本地仓库根目录
- 场景

代理随后应先读取：

- `README.md`
- `docs/02-lifecycle.md`
- `docs/08-session-bootstrap.md`

然后再决定是否还需要额外问题。
