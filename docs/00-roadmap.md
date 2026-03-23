# Product Development Roadmap

## Purpose

This document explains what happens after a project starts.

It is written for a non-technical user. The user does not need to know implementation details in advance. The protocol is responsible for turning business intent into a controlled delivery path.

---

## End-To-End Flow

| Phase | What The User Does | What The Protocol Does | Main Output |
| :--- | :--- | :--- | :--- |
| `Kickoff` | Describe the product idea, pain point, or desired feature in plain language | Identify session mode and gather missing business context | Initial understanding |
| `Discovery` | Answer focused product questions | Reduce ambiguity and surface risks, assumptions, and missing facts | Discovery notes |
| `Specification` | Confirm whether the proposed direction matches the business goal | Write source-of-truth artifacts and define scope boundaries | Constitution, scope, decisions, data and API contracts if needed |
| `Planning` | Approve or adjust priorities | Split work into bounded mission blocks | Task queue |
| `Implementation` | Observe progress and answer business tradeoff questions if needed | Implement one mission block at a time | Code plus evidence |
| `Review` | Decide whether findings are acceptable or need correction | Audit scope, correctness, and contract alignment | Structured review result |
| `Recovery` | Clarify priorities if work is blocked or broken | Restart from a controlled state instead of improvising | Recovery plan |
| `Closure` | Confirm whether to continue, pause, or release | Update repository state for the next session | Current project state |

---

## What The User Should Expect

The protocol will regularly ask for:

- the real business goal
- who the user is
- what must work first
- what can wait
- what counts as success
- what is too expensive or too risky

The protocol should not force the user to choose:

- frontend framework
- database design
- API shape
- file structure
- testing tool

unless those choices directly change cost, speed, risk, or product behavior in a meaningful way.

---

## What Happens In A Good Session

1. The session starts by identifying the mode.
2. The protocol asks enough questions to remove dangerous ambiguity.
3. The protocol writes the answer into stable files.
4. The implementation task is cut into small bounded units.
5. The coding agent only executes one bounded unit at a time.
6. Review is based on evidence, not on confidence.
7. Before ending, the current project state is written for the next session.

---

## Failure Modes This Roadmap Is Designed To Prevent

- coding before the product goal is clear
- the model inventing hidden requirements
- the model touching unrelated files
- "done" claims without evidence
- new sessions losing context and drifting
- technical debt caused by unbounded implementation

---

## Minimum Startup Checklist

Before starting a real project, prepare at least:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

If the system has APIs or data persistence, also prepare:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml`

---

## 中文翻译

### 目的

这个文档解释一个项目启动之后会发生什么。

它是写给非技术用户的。用户不需要预先了解实现细节，协议负责把业务意图转成受控的交付路径。

### 端到端流程

| 阶段 | 用户要做什么 | 协议要做什么 | 主要产出 |
| :--- | :--- | :--- | :--- |
| `Kickoff` | 用大白话描述产品想法、痛点或期望功能 | 识别会话模式，补齐缺失的业务上下文 | 初始理解 |
| `Discovery` | 回答聚焦的产品问题 | 减少模糊性，暴露风险、假设和缺失事实 | 调研记录 |
| `Specification` | 确认建议方向是否符合业务目标 | 写真理源文件并定义范围边界 | Constitution、Scope、Decisions，以及需要时的数据和 API 契约 |
| `Planning` | 批准或调整优先级 | 把工作拆成有边界的 mission blocks | 任务队列 |
| `Implementation` | 观察进展，并在需要时回答业务取舍问题 | 一次实现一个 mission block | 代码和证据 |
| `Review` | 判断审查发现是否可接受或需要修正 | 审核范围、正确性和契约一致性 | 结构化审查结果 |
| `Recovery` | 在工作卡住或出错时澄清优先级 | 从受控状态重新开始，而不是即兴乱补 | 恢复计划 |
| `Closure` | 确认是继续、暂停还是发布 | 更新仓库状态，供下次会话接手 | 当前项目状态 |

### 用户应该预期什么

协议会经常询问这些问题：

- 真正的业务目标是什么
- 用户是谁
- 哪些事情必须最先跑通
- 哪些事情可以等待
- 什么算成功
- 什么太贵或风险太高

协议不应该强迫用户去选择：

- 前端框架
- 数据库设计
- API 形态
- 文件结构
- 测试工具

除非这些选择会明显影响成本、速度、风险或产品行为。

### 一次好的会话会发生什么

1. 会话开始时先识别当前模式。
2. 协议会提足够多的问题，以消除危险的模糊性。
3. 协议把答案写入稳定文件。
4. 实现任务会被切成有边界的小单元。
5. 编码代理一次只执行一个小单元。
6. 审查以证据为依据，而不是以自信为依据。
7. 会话结束前，当前项目状态会被写下来供下次接手。

### 这份路线图要防止的失败模式

- 在产品目标还不清楚时就开始编码
- 模型擅自发明隐藏需求
- 模型碰触无关文件
- 没有证据却声称“已完成”
- 新会话丢失上下文后开始漂移
- 因为任务没有边界而积累技术债

### 最低启动清单

在开始一个真实项目之前，至少准备这些文件：

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

如果系统包含 API 或数据持久化，再额外准备：

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md` 或 `<PROJECT_ROOT>/openapi.yaml`
