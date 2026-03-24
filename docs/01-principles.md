# Principles And Writing Style

## Core Principles

1. Less is more. Always keep it simple.
2. Do not code while the problem is still vague.
3. Do not let the coding agent invent architecture without approval.
4. Do not treat conversation memory as a reliable source of truth.
5. Do not accept "done" without evidence.
6. Do not expand scope inside implementation tasks.

Simplicity means:

- prefer the smallest useful scope
- prefer the fewest dependencies
- prefer the smallest safe change surface
- prefer the clearest design that can be explained and verified

---

## Plain Writing Rule

Use plain language first.

For models, clarity comes mainly from:

- stable structure
- explicit rules
- short sections
- consistent labels
- examples and templates

It does not come mainly from:

- emoji
- decorative emphasis
- many repeated punctuation marks
- aggressive formatting noise

Emoji and visual emphasis can help a human skim a document, but they rarely improve model compliance in a meaningful way. In long prompts they often become noise.

Recommended style:

- use short section titles
- use numbered stages and named artifacts
- use tables only when comparing options or responsibilities
- use bold sparingly for one term, not whole paragraphs
- keep one rule per bullet when possible

Avoid:

- stacked emoji
- repeated `###`, `!!!`, or similar visual shouting
- mixing policy, examples, and exceptions in the same paragraph

---

## Role Model

This protocol uses five roles.

| Role | Owner | Responsibility | Cannot Do |
| :--- | :--- | :--- | :--- |
| User | Human | Define business goal, priorities, acceptance, and tradeoffs | Invent technical design under pressure |
| Spec Architect | Planning model | Translate business intent into specs, decisions, function blocks, and mission boundaries | Write production code without changing role |
| Builder | Coding model | Implement one bounded mission block under the active function block | Expand scope or rewrite architecture on its own |
| Reviewer | Review model or review pass | Check evidence, risks, quality gates, and contract alignment | Trust the builder's claims without verification |
| Recovery Coordinator | Recovery model or recovery pass | Classify broken state, repair session truth, and choose the smallest safe recovery move | Continue implementation by instinct or hide state drift |

Scene paths define work sequence. Roles define responsibility boundaries.

No scene may collapse role separation.

When a problem is discovered, route it by ownership:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` -> `Recovery Coordinator`
- `environment_issue` -> `Recovery Coordinator`
- `review_context_gap` -> current scene lead role

---

## Ontology Skeleton vs Engineering Map

Do not mix these two ideas.

The `8-element ontology frame` describes what one function is:

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

The `8-layer impact map` describes where that function lands in engineering:

- business
- domain
- flow
- experience
- application
- service
- data
- quality

Think of it like this:

- ontology frame = meaning
- impact map = implementation surface

---

## Non-Technical User Rule

The user is not required to provide technical solutions.

The Spec Architect must:

- ask business questions in plain Chinese
- convert business answers into technical constraints
- present no more than a few decision options at once
- explain tradeoffs in product terms, not framework jargon
- make a reasonable default recommendation when the user lacks the technical basis to choose

The user must still decide:

- what problem matters most
- what "good enough" means
- which tradeoff is acceptable
- whether to proceed, pause, or cut scope

---

## 中文翻译

### 核心原则

1. 少即是多。永远保持简单。
2. 在问题仍然模糊时不要开始编码。
3. 不要让编码代理在未经批准的情况下自行发明架构。
4. 不要把聊天记忆当成可靠真理源。
5. 没有证据，就不要接受“完成了”。
6. 不要在实现任务内部偷偷扩范围。

简单意味着：

- 优先最小有用范围
- 优先最少依赖
- 优先最小且安全的改动面
- 优先最清晰、最容易解释和验证的设计

### 简明写作规则

优先使用大白话。

对模型来说，真正带来清晰度的主要是：

- 稳定结构
- 明确规则
- 短小章节
- 一致标签
- 示例和模板

而不是：

- 表情符号
- 装饰性强调
- 大量重复标点
- 过度格式噪音

表情和视觉强调可能帮助人类快速扫读文档，但通常不会显著提升模型的服从度。在长提示词里，它们更容易变成噪音。

推荐写法：

- 使用简短的章节标题
- 使用编号阶段和命名工件
- 只有在比较选项或职责时才使用表格
- 谨慎使用加粗，只强调单个术语，不要整段都强调
- 尽量一条规则对应一个 bullet

避免：

- 堆叠表情符号
- 重复的 `###`、`!!!` 或类似视觉喊叫
- 在同一段里混合政策、示例和例外

### 角色模型

这套协议使用五个角色。

| 角色 | 所有者 | 责任 | 不能做什么 |
| :--- | :--- | :--- | :--- |
| User | 人类 | 定义业务目标、优先级、验收标准和取舍 | 在压力下被迫发明技术设计 |
| Spec Architect | 规划模型 | 把业务意图翻译成规格、决策、function block 和 mission 边界 | 不切换角色却直接写生产代码 |
| Builder | 编码模型 | 在当前 function block 下实现一个有边界的 mission block | 自行扩范围或重写架构 |
| Reviewer | 审查模型或审查过程 | 检查证据、风险、质量门禁和契约一致性 | 不经验证就相信 Builder 的说法 |
| Recovery Coordinator | 恢复模型或恢复过程 | 分类故障状态、修复会话真理源、选择最小安全恢复动作 | 凭直觉继续实现或掩盖状态漂移 |

场景路径定义工作顺序，角色定义责任边界。

任何场景都不得破坏角色分离。

发现问题后，必须按责任归因路由：

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` -> `Recovery Coordinator`
- `environment_issue` -> `Recovery Coordinator`
- `review_context_gap` -> 当前场景主导角色

### 本体骨架 vs 工程地图

不要把这两个概念混在一起。

`8 元素本体框架` 用来描述一个功能“是什么”：

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

`8 层影响地图` 用来描述这个功能“落到哪些工程层”：

- business
- domain
- flow
- experience
- application
- service
- data
- quality

可以这样记：

- 本体框架 = 意义骨架
- 影响地图 = 实现落面

### 非技术用户规则

用户不需要提供技术解决方案。

Spec Architect 必须：

- 用中文大白话提出业务问题
- 把业务回答转成技术约束
- 一次提供不超过少量的决策选项
- 用产品语言解释取舍，而不是框架黑话
- 当用户缺乏技术背景时，给出合理默认建议

但用户仍然要决定：

- 当前最重要的问题是什么
- 什么叫“足够好”
- 哪种取舍是可以接受的
- 是继续、暂停还是缩减范围
