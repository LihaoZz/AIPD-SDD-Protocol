### 说明

这个文档定义：当用户只提供“仓库 + 场景”时，代理应如何开始。

它是启动辅助文件，不是生命周期权威文档。

### 全局启动文件

无论什么场景，都先读取：

- `README.md`
- `docs/00_lifecycle.md`
- `docs/05_operating_playbook.md`
- 当前 `MB` 需要进入 harness 闭环时，再额外读取 `HARNESS.md`

它们分别负责：

- 解释协议是什么
- 定义唯一流程真源
- 给出实操建议
- 在启用 harness 时解释 runtime 命名、retry feedback 和 machine state 规则

### Preflight Summary 结构

进入请求场景前，必须先运行 `Project Preflight`。

总结至少包含：

1. 用户请求的场景
2. 项目根目录
3. preflight 结果
4. 该场景现在是否可以开始
5. 当前激活角色
6. 场景路径
7. 缺失项
8. 自动动作
9. 阻塞项

结构使用 `templates/PREFLIGHT_RESULT.template.md`。

### 场景阅读优先级

精确场景路径始终跟 `docs/00_lifecycle.md` 走。

这个文档只负责告诉你先读什么。

如果当前角色判断需要 research，先按 `docs/00_lifecycle.md` 的 `Research Rule` 执行，不要默认直接搜索。

#### `greenfield`

补充读取：

- `docs/01_principles.md`
- `docs/02_artifacts.md`
- constitution、scope、FB、MB、quality、session state 等核心模板

第一个角色：

- `Spec Architect`

第一步动作：

- 用业务问题把 8 个本体元素和受影响层问清楚
- 如果外部事实或工具检索会实质帮助推进，先征得用户同意，再执行 system-triggered research

不要：

- 直接开始编码
- 太早逼用户选技术栈

#### `expansion`

补充读取：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/02_artifacts.md`
- `docs/03_mission_blocks.md`
- `<PROJECT_ROOT>/QUALITY_RULEBOOK.md`
- `<PROJECT_ROOT>/QUALITY_MEMORY.md`

相关时再读：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

第一个角色：

- `Spec Architect`

第一步动作：

- 识别新功能会改变什么、可能打破什么假设、编码前必须补齐哪些 FB 细节
- 如果市场扫描、相似产品查看或工具检索会实质帮助推进，先征得用户同意，再执行 system-triggered research

不要：

- 在规格更新前开始实现

#### `continue`

补充读取：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 当前 function block
- 当前 mission block
- 当前 machine sidecar（如果存在）
- 当前依赖的输入工件

必要时再读：

- `docs/04_review_recovery.md`

第一个角色：

- 状态健康时由 `Builder`
- 状态漂移或阻塞时由 `Spec Architect` 或 `Recovery Coordinator`

第一步动作：

- 说清当前阶段和下一个唯一动作
- 如果当前 `MB` 会进入 harness 执行，先跑 `preflight.py --level mb`
- 如果某个有边界技术缺口需要外部事实，先征得用户同意，再执行 system-triggered research

不要：

- 从零重启整个项目

#### `review`

补充读取：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- 相关 function block
- 相关 mission block
- 相关输入工件或设计权威来源
- 相关契约文件
- `docs/04_review_recovery.md`
- `schemas/quality-report.schema.json`

第一个角色：

- `Reviewer`

第一步动作：

- 对照书面工件和证据做审计

不要：

- 除非用户改任务，否则在 review 中顺手修代码

#### `recovery`

补充读取：

- `<PROJECT_ROOT>/SESSION_STATE.md`
- 当前 function block
- 当前 mission block
- `<PROJECT_ROOT>/VERSION_LOG.md`（如存在）
- `<PROJECT_ROOT>/QUALITY_MEMORY.md`（如存在）
- `docs/04_review_recovery.md`
- 相关故障区域工件

第一个角色：

- `Recovery Coordinator`

第一步动作：

- 先分类失败，再选择最小安全动作

不要：

- 凭直觉继续实现

### 首条回复模板

启动后，第一条正式回复应包含：

1. 识别出的场景
2. preflight 结果
3. 现在能否开始
4. 当前激活角色
5. 场景路径
6. 已读取文件
7. 缺失文件
8. 下一步问题或动作

回复应短而操作化。

### 最小用户输入

用户可以只发：

- `Repo: <repo-link>\nScene: greenfield`
- `Repo: <repo-link>\nScene: expansion`
- `Repo: <repo-link>\nScene: continue`
- `Repo: <repo-link>\nScene: review`
- `Repo: <repo-link>\nScene: recovery`

可选第三行：

- 产品想法
- 功能请求
- 阻塞问题
- review 目标

### 重要限制

前提是模型或工具真的能读取仓库内容。

如果访问不到，用户需要提供：

- 本地路径
- 上传文件
- 或可浏览仓库的工具
