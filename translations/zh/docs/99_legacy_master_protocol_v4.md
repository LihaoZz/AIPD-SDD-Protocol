## 定位

这是一套面向非技术用户的 AI 软件交付协议。

目标不是让模型“更聪明”，而是让模型在长期项目里更少即兴发挥、更少偷换需求、更少积累技术债。

这套协议默认以下现实：

- 用户懂业务，但不懂技术实现细节
- 模型会写代码，但当边界不清时会擅自发挥
- 新会话和新模型不应依赖聊天记忆来继续工作
- 可靠上下文必须写进仓库文件

一个功能应通过两种互补方式被理解：

- `ontology frame` 用来定义“这个功能是什么”
- `impact map` 用来定义“这个功能落到哪些工程层”

## 核心原则

1. 问题没有写清楚之前，不要进入实现。
2. 设计、实现和审查必须分离，不能让同一个角色自说自话。
3. 所有重要决策都必须进入仓库文件，不能只留在聊天记录。
4. 任务必须有边界，不能只给模型一个宽泛目标就让它开始编码。
5. 完成必须靠证据，而不是靠自我陈述。
6. 少即是多。永远保持简单。
7. 失败后要回到正确阶段，而不是盲目重复尝试。
8. 当体验层由外部交付时，应把外部 UI 包视为输入权威，而不是要求 Builder 去发明视觉设计。

## 五个角色

| 角色 | 作用 | 说明 |
| :--- | :--- | :--- |
| User | 提供业务目标、优先级、验收标准和取舍 | 不负责实现细节 |
| Spec Architect | 把业务语言翻译成规格、边界和任务 | 负责消除模糊性 |
| Builder | 在任务边界内实现代码 | 不拥有范围扩张权 |
| Reviewer | 对照规格和证据做审查 | 不相信口头“做完了” |
| Recovery Coordinator | 修复损坏状态并路由恢复工作 | 不得凭直觉继续实现 |

## 生命周期

项目并不是在所有场景下都走同一条固定路径。

它们运行在四层执行模型中：

1. `Preflight`
2. `Scene Path`
3. `Role Handoff`
4. `Issue Routing`

通用控制外壳是：

1. `PREFLIGHT`
2. `INIT`
3. `SCENE_WORK`
4. `REVIEW_GATE`
5. `CLOSE`

详细定义见 [docs/02-lifecycle.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/02-lifecycle.md)。

## 仓库化原则

这套协议不再把所有内容塞进一个超大文件，而是拆成多个模块：

- 总路线图：[docs/00-roadmap.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/00-roadmap.md)
- 原则和写作风格：[docs/01-principles.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/01-principles.md)
- 生命周期：[docs/02-lifecycle.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/02-lifecycle.md)
- 真理源文件体系：[docs/03-artifacts.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/03-artifacts.md)
- 任务边界：[docs/04-mission-blocks.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/04-mission-blocks.md)
- 审查与恢复：[docs/05-review-recovery.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/05-review-recovery.md)
- 实操流程：[docs/06-operating-playbook.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/06-operating-playbook.md)

## 为什么 v4 比旧版更稳

相较于单文件版本，v4 有几个关键升级：

- 不再依赖重度视觉强调来传递重点，而是依赖稳定结构和明确字段
- 不再把 discovery 的结束条件写成“用户说停”，而是要求写出事实、假设、风险和明确排除项
- 不再停留在抽象原则，而是补上模板、角色 prompt 和机器可读 schema
- 不再让新会话靠记忆恢复，而是要求使用 `SESSION_STATE.md` 作为恢复入口
- 不再直接跳进某个场景，而是要求先执行 `Project Preflight`
- 不再给编码代理宽泛任务，而是要求每个 function block 和 mission block 都定义范围、边界、质量检查和回滚说明
- 不再默认 Builder 总是 UI 作者，而是要求在 UI 集成工作开始前先记录体验层是否交给外部工具交付

## 最小执行规则

如果只保留最关键的规则，至少保留下面五条：

1. 开始编码前，必须已有 `CONSTITUTION.md`、`SCOPE.md`、`DECISIONS.md` 和 `SESSION_STATE.md`
2. 每个实现流程必须同时有激活的 `Function Block` 和当前 `Mission Block`
3. 每次新对话都必须先执行 `Project Preflight`
4. Builder 不得越出 `allowed_files`
5. 审查必须使用结构化输出
6. 每次会话结束前必须更新 `SESSION_STATE.md`
7. 如果用户只给“仓库 + 场景”，代理必须按仓库规则自行启动，而不是再次索要内部文档路径
8. 如果 `experience` 层受影响，父 `FB` 必须在任何依赖它的 UI 集成 `MB` 开始前记录 `experience_delivery_mode`

## 与仓库的关系

这个仓库本身就是协议产品，而不是某个具体业务应用。

- 协议本体存放在 `docs/`、`prompts/`、`schemas/` 和 `templates/`
- 某个真实项目的实时状态存放在外部 `PROJECT_ROOT`

这种分层使得 SDD 可以被反复复用，而不是每次都从头重写一套 prompt 体系。

## 启动入口

这个仓库的目标是支持最小开场消息：

- 仓库链接或本地根目录
- 场景

仓库级路由规则放在 `README.md`。

场景到文件的映射放在 `docs/08-session-bootstrap.md`。
