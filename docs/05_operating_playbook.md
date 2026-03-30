# Operating Playbook

This document is an operational guide.

It is not the authority for lifecycle rules. For normative flow definitions, use `docs/00_lifecycle.md`.

## Project Preflight Checklist

At the start of a conversation:

1. identify the working path and requested scene
2. check foundational files and directories
3. check scene-specific requirements
4. return a short preflight summary
5. classify the state as `ready`, `bootstrap_required`, or `blocked`
6. if needed, initialize only safe foundational files
7. if blocked, route the problem by ownership and ask only for the minimum missing context

## Build An FB In This Order

Before detailed FB planning, cover these two views:

- `8-element ontology frame`: what the function is
- `8-layer impact map`: where the function lands in engineering

Use them in this order:

1. ontology first
2. impact map second
3. acceptance third
4. MB slicing last

If the ontology is weak, do not hide the gap inside implementation planning.

## Experience Delivery In Practice

When the `experience` layer is affected, the `Spec Architect` must decide `experience_delivery_mode` inside `SPEC` or `FB_DETAILING`.

Allowed values:

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

Practical rule:

- if the Builder owns the experience layer, continue normal MB planning
- if the experience layer is externally delivered, capture the input artifacts in the parent `FB`
- dependent `MB`s become integration slices, not visual redesign tasks

For external UI delivery, record at minimum:

- which states and branches the package must cover
- which artifact or code bundle is the approved input
- what part remains Builder-owned
- which later `MB`s are blocked until the input is ready

## Scene Heuristics

### `greenfield`

Focus on:

- business goal
- user value
- version-one boundary
- first quality system
- first FB plan

Avoid:

- early coding
- premature stack arguments

### `expansion`

Focus on:

- what existing assumption may break
- what regressions are likely
- what new FB must be written before coding

Avoid:

- treating a delta feature like a full restart

### `continue`

Focus on:

- active FB
- active MB
- last successful checkpoint
- the next single safe action

Avoid:

- restarting from zero
- switching tasks without recording state

### `review`

Focus on:

- artifact alignment
- scope compliance
- evidence completeness
- ownership classification for every finding

Avoid:

- patching code during review unless the user changes the task

### `recovery`

Focus on:

- last known good checkpoint
- failure classification
- smallest safe next move

Avoid:

- continuing implementation by instinct

## Local Validation

Run the local guard script before claiming the repository is ready for handoff.

Commands:

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`

## 中文翻译

### 说明

这个文档是操作说明，不是生命周期权威文件。

流程定义一律以 `docs/00_lifecycle.md` 为准。

### Project Preflight 检查清单

每次新对话开始时：

1. 确认工作路径和请求场景
2. 检查基础文件和目录
3. 检查场景专属要求
4. 返回简短 preflight summary
5. 把状态分类为 `ready`、`bootstrap_required` 或 `blocked`
6. 只在必要时补齐安全基础文件
7. 如果阻塞，按责任归因路由问题，并只问最小必要缺失信息

### 编写 FB 的顺序

进入详细 FB 规划前，先覆盖两个视角：

- `8 元素本体框架`：功能是什么
- `8 层影响地图`：功能会落到哪些工程层

推荐顺序：

1. 先本体
2. 再影响地图
3. 再验收
4. 最后切 MB

如果本体还很弱，不要把问题藏进实现计划里。

### 体验交付的实操规则

当 `experience` 层受影响时，`Spec Architect` 必须在 `SPEC` 或 `FB_DETAILING` 内决定 `experience_delivery_mode`。

允许值：

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

实操上：

- 如果体验层归 Builder，按普通 MB 规划继续
- 如果体验层由外部交付，就把输入工件写进父 `FB`
- 所有依赖它的 `MB` 都变成集成切片，而不是视觉重设计任务

外部 UI 交付最少要记录：

- 外部包必须覆盖哪些状态和分叉
- 哪个工件或代码包是批准输入
- 哪一部分仍归 Builder 负责
- 哪些后续 `MB` 在输入就绪前被阻塞

### 各场景的操作重心

- `greenfield`：聚焦业务目标、用户价值、V1 边界、首个质量体系和首批 FB
- `expansion`：聚焦新功能会打破什么假设、什么地方可能回归、编码前必须补齐哪些 FB 内容
- `continue`：聚焦当前 FB、当前 MB、最近成功检查点和下一个唯一安全动作
- `review`：聚焦工件对齐、范围合规、证据完整，以及每个发现的责任归因
- `recovery`：聚焦最近已知良好点、失败分类和最小安全下一步

不要：

- `greenfield` 时过早开始编码
- `continue` 时从零重启
- `review` 时顺手修代码
- `recovery` 时凭直觉继续实现

### 本地校验

声称协议仓库或项目可交接前，先运行本地 guard：

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`
