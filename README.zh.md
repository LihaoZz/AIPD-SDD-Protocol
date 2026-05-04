<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: README.md
Translation source: translations/zh/README.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

### 这个仓库是什么

这个仓库是一套 AI 辅助产品开发协议。

它也是 AIPD 的单仓库分发入口。

它不是业务代码仓库本身。

这里存放的是：

- 运行规则
- 生命周期定义
- 角色提示词
- 模板
- 校验工具
- 内置的 Symphony runtime
- 一键安装与启动入口

真实项目状态放在外部 `PROJECT_ROOT`。

### 核心思想

`less is more`。

这套协议优先追求：

- 最小有用范围
- 最清晰文档
- 最少运动部件
- 最小安全改动
- 证据优先于自信
- 当体验层不归 Builder 直接负责时，以外部视觉权威优先于临场 UI 发明

### 两个根目录

- `PROTOCOL_ROOT`
  当前协议仓库，放可复用规则
- `PROJECT_ROOT`
  真实项目目录，放真理源文件和实现状态

两者必须分离。

### 启动契约

`README.md` 是唯一主入口。

新会话开始时，先读这个文件。

用户最少只需要给：

1. 仓库链接或本地协议根目录
2. 场景

可选第三项：

- 产品想法
- 功能请求
- 阻塞问题
- review 目标
- 如果当前工作区不是实际项目，再补一个项目根路径

### 端到端视图

一条正常链路应该是：

`Kickoff -> Discovery -> Specification -> Planning -> External UI Handoff(当相关时) -> Implementation -> Review -> Recovery(当需要时) -> Closure`

其中外部 UI handoff 不是所有功能都要有，只有体验层不由 Builder 直接负责时才出现。

### 一次好的会话应该发生什么

1. 先识别场景。
2. 先跑 `Project Preflight`。
3. 先消除危险模糊，再进入实现。
4. 先把答案写进稳定工件。
5. 如果体验层外包交付，先把 handoff 写清楚。
6. 再把实现切成小而有边界的 MB。
7. Builder 一次只做一个 MB。
8. Review 依据证据，不依据感觉。
9. 结束前写下当前项目状态。

### 支持的场景

- `greenfield`
- `expansion`
- `continue`
- `review`
- `recovery`

### 自动阅读路径

进入任何场景前，都必须：

1. 执行 `Project Preflight`
2. 返回简短 `Preflight Summary`
3. 把项目状态分类为 `ready`、`bootstrap_required` 或 `blocked`
4. 按 [docs/00_lifecycle.md](docs/00_lifecycle.md) 映射场景路径
5. 激活第一个角色
6. 只有在安全时才自动继续

全局启动文件：

- `README.md`
- [docs/00_lifecycle.md](docs/00_lifecycle.md)
- [docs/06_session_bootstrap.md](docs/06_session_bootstrap.md)

各场景的补充优先阅读如下：

- `greenfield`：`01_principles`、`02_artifacts`、`05_operating_playbook` 和核心模板
- `expansion`：`02_artifacts`、`03_mission_blocks`、`05_operating_playbook` 和当前项目真理源文件
- `continue`：按需读 `04_review_recovery`、`05_operating_playbook`、当前 `SESSION_STATE`、当前 `FB/MB` 与必需输入工件
- `review`：读 `04_review_recovery`、质量报告 schema、相关真理源工件与证据
- `recovery`：读 `04_review_recovery`、当前 `SESSION_STATE` 和受影响工件

精确场景路径始终以 [docs/00_lifecycle.md](docs/00_lifecycle.md) 为准。

### 最低启动清单

至少准备：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

如果有 API 或持久化，再补：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md` 或 `<PROJECT_ROOT>/openapi.yaml`

### 权威文档层级

最高权威顺序：

1. [docs/00_lifecycle.md](docs/00_lifecycle.md)
2. [docs/01_principles.md](docs/01_principles.md)
3. [docs/02_artifacts.md](docs/02_artifacts.md)
4. [docs/03_mission_blocks.md](docs/03_mission_blocks.md)
5. [docs/04_review_recovery.md](docs/04_review_recovery.md)

辅助说明：

- [docs/05_operating_playbook.md](docs/05_operating_playbook.md)
- [docs/06_session_bootstrap.md](docs/06_session_bootstrap.md)
- [docs/07_repository_layout.md](docs/07_repository_layout.md)

历史参考：

- [docs/99_legacy_master_protocol_v4.md](docs/99_legacy_master_protocol_v4.md)
