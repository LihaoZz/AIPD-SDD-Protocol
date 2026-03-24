# Function Blocks And Mission Blocks

## Why The Split Exists

Product work and code change work are not the same unit.

- a `Function Block` (`FB`) represents one product-facing delivery unit
- a `Mission Block` (`MB`) represents one bounded code change attempt under one active FB

This split keeps product context stable while letting implementation move in small, auditable steps.

---

## Function Blocks

An `FB` should answer:

- what user value is being delivered
- who the actor is
- what goal the actor is trying to complete
- what entities, relations, states, events, and rules define this function
- what evidence proves the function is real
- which engineering layers are affected
- what the acceptance definition is
- what is out of scope
- what risks matter for this feature
- which MBs were planned, completed, or failed

An `FB` is the product anchor.

It should not become a running log of every code attempt.

Before an `FB` becomes detailed enough for MB planning, it should first contain an `FB Ontology Frame`.

The ontology frame covers 8 elements:

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

Each element must be covered with one of these states:

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

An `FB` should also contain an `Impact Map`.

The impact map is different from the ontology frame:

- the ontology frame defines what the function is
- the impact map defines where the function lands in engineering

The impact map should cover these 8 layers:

- business
- domain
- flow
- experience
- application
- service
- data
- quality

---

## Mission Blocks

An `MB` should answer:

- what exact code change is being attempted
- which FB it belongs to
- which slice of the parent FB acceptance it advances
- which ontology elements from the parent FB are in scope now
- which affected engineering layers from the parent FB are in scope now
- which ontology elements or layers are explicitly deferred
- which files may be modified
- what the baseline is before the change
- which quality checks must pass
- what evidence is required
- how to roll back safely

An `MB` is the smallest unit that should be implemented, reviewed, and either accepted or rejected.

An `MB` should not redefine the whole function.

It should inherit from the parent `FB` and declare one implementation slice.

---

## Naming Rule

Use compact IDs that make the hierarchy obvious.

Examples:

- `fb2`
- `fb2-mb1`
- `fb2-mb2`
- `fb7-mb3`

---

## Quality Rule

An `MB` must not invent its own quality standards.

Every `MB` must:

- select checks from `QUALITY_RULEBOOK.md`
- declare which ontology elements and layers from the parent FB are in scope
- record a full baseline
- produce a quality report
- update `SESSION_STATE.md`

If a needed quality rule does not exist yet, stop and request a rulebook update instead of improvising.

---

## Completion Rule

An `MB` is not complete when the Builder says "done."

It is complete only when all required evidence exists:

- code changes
- required quality checks and results
- the quality report
- scope remained within the allowed boundary
- the session state was updated

---

## 中文翻译

### 为什么要拆成 FB 和 MB

产品交付单元和代码改动单元不是同一种东西。

- `Function Block` (`FB`) 表示一个面向产品交付的单元
- `Mission Block` (`MB`) 表示该 FB 下的一次有边界代码改动尝试

这种拆分能让产品上下文保持稳定，同时让实现过程以更小、可审计的步子推进。

### Function Block

`FB` 应该回答这些问题：

- 这次要交付什么用户价值
- 谁是这个功能的 actor
- actor 想完成什么 goal
- 哪些 entity、relation、state、event、rule 定义了这个功能
- 什么 evidence 可以证明这个功能真的成立
- 哪些工程层会受到影响
- 验收定义是什么
- 什么明确不做
- 这个功能最重要的风险是什么
- 已计划、已完成、已失败的 MB 分别是什么

`FB` 是产品级锚点。

它不应该变成记录每次代码尝试的流水账。

在 `FB` 细化到可以拆 `MB` 之前，它应先包含一个 `FB Ontology Frame`。

这个本体框架覆盖 8 个元素：

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

每个元素都必须被覆盖，并标记为以下状态之一：

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

`FB` 还应包含一个 `Impact Map`。

`Impact Map` 和本体框架不是一回事：

- 本体框架定义“这个功能是什么”
- `Impact Map` 定义“这个功能会落到哪些工程层”

`Impact Map` 应覆盖这 8 层：

- business
- domain
- flow
- experience
- application
- service
- data
- quality

### Mission Block

`MB` 应该回答这些问题：

- 这次具体尝试什么代码改动
- 它属于哪个 FB
- 它推进了父 FB 的哪个验收切片
- 这次当前涉及父 FB 的哪些本体元素
- 这次当前覆盖父 FB 的哪些工程层
- 哪些本体元素或工程层被明确延期
- 允许修改哪些文件
- 改动前的基线是什么
- 必须通过哪些质量检查
- 必须返回什么证据
- 如何安全回滚

`MB` 是最小实现、审查和接受或拒绝的单元。

`MB` 不应该重新定义整个功能。

它应继承父 `FB`，并声明本次实现切片。

### 命名规则

使用能直接体现层级关系的精简命名。

例如：

- `fb2`
- `fb2-mb1`
- `fb2-mb2`
- `fb7-mb3`

### 质量规则

`MB` 不得自行发明质量标准。

每个 `MB` 都必须：

- 从 `QUALITY_RULEBOOK.md` 中选择检查项
- 声明本次涉及父 FB 的哪些本体元素和工程层
- 记录完整基线
- 产出质量报告
- 更新 `SESSION_STATE.md`

如果需要的质量规则还不存在，应停止并请求更新规则手册，而不是临场发挥。

### 完成规则

不是 Builder 说“done”就算一个 `MB` 完成。

只有在下面这些证据都存在时，它才算完成：

- 已有代码改动
- 已有必需的质量检查及结果
- 已有质量报告
- 实际范围没有越出允许边界
- `SESSION_STATE.md` 已更新
