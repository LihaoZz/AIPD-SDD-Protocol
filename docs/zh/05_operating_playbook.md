<!--
GENERATED FILE - DO NOT EDIT DIRECTLY
Source: docs/05_operating_playbook.md
Translation source: translations/zh/docs/05_operating_playbook.md
Generated at: 2026-05-04T02:16:50-07:00
Authority: Chinese reference only; the English source file is authoritative.
-->

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

### Research 的实操规则

只有当 research 能实质改善当前决策时，才使用它。

存在两种触发方式：

- `user_triggered`：用户明确要求搜索或检索
- `system_triggered`：当前角色判断外部事实可以解决关键缺口

实操规则：

- `user_triggered` research 可以立即开始
- `system_triggered` research 必须先说明为什么现在需要查，再等待用户同意

对 `Spec Architect`，常见用途包括：

- 简易市场研究
- 相似产品查看
- 搜索已有工具、服务或开源项目
- 在确定视觉方向前收集 UI 参考

对 `Builder`，常见用途包括：

- 查官方文档
- 查 issue 或 changelog
- 解决有边界技术问题
- 为当前 `MB` 找成熟实现参考

采纳后的结论必须写回工件，不能只依赖聊天记忆。

### UI Prompt 生成的实操规则

当 UI 由外部交付时，顺序固定为：

1. 先收集参考或做 research
2. 再给出建议选项
3. 再把会显著影响生成质量的 UI 细节讨论清楚
4. 由用户确认最终视觉方向、设计核心和主要 UI 决策
5. 然后把外部工具 prompt 生成并固化到 `experience_prompts/*.md`
6. 在该工件中写入可直接复制的完整提示词
7. 再由用户确认外部输出
8. 最后把批准结果交给后续集成 `MB`

assistant 可以建议风格或工具，但最终 UI 定调权在用户手里。

生成 prompt 前的讨论通常应覆盖：

- 信息密度
- 布局方向
- 组件风格方向
- 颜色方向
- 排版方向
- 交互方向
- 动效方向（相关时）
- 响应式优先级
- 可访问性规则
- 采纳哪些参考
- 明确避开什么参考

如果某些决策被有意留白，也要在生成 prompt 前把默认值写清楚，不能默默省略。

如果后续 `MB` 依赖这份交接契约，应通过 `external_tool_prompt_ref` 指向该工件，而不是依赖聊天记忆。

### Stitch Prompt 的实操策略

当目标工具是 Stitch 时，不要套用一种固定 prompt 结构，而要按任务选择策略。

遵循 Stitch prompt guide 的建议：

- 使用大白话
- prompt 聚焦单页
- 复杂产品先高层定义，再按 screen by screen 逐步细化
- 每一轮尽量只做一到两个边界清晰的变化，不要把太多结构改动揉在一起

在写最终 prompt 前，先明确本次属于哪种目标类型：

- `canonical_shell`：首次定义某个页面族，或有意识地重建该页面族壳子
- `state_variant`：同一页面族、同一壳子下的不同状态
- `family_extension`：同一页面族、同一壳子下的局部扩展或新增区域
- `independent_screen`：不受共享壳子约束的独立页面

然后再明确工具指引档位：

- `stitch_first_pass`：Stitch 的首轮高细节单页或页面族壳子生成
- `stitch_iterative_refine`：Stitch 的后续迭代，每次只做一到两个边界清晰的变化
- `figma_structured_handoff`：Figma 的较完整多状态交接
- `general_structured_handoff`：其他工具的保守兜底档位

实操上，把这两个轴组合起来看：

- Stitch 中的新页面族：`canonical_shell` + `stitch_first_pass`
- Stitch 中同页族补状态：`state_variant` + `stitch_iterative_refine`
- Stitch 中同页族做局部扩展：`family_extension` + `stitch_iterative_refine`
- Stitch 中的独立页面：`independent_screen` + `stitch_first_pass`
- Figma 的有边界页面族交接：先选对 `prompt_goal_type`，再通常搭配 `figma_structured_handoff`

如果本次工作仍在同一页面族内，必须把页面族契约写明：

- 写出 `page_family_id`
- 写出哪些壳子元素必须固定，例如 sidebar、top nav、页面框架、grid、布局节奏、组件语言
- 写出哪些区域允许变化
- 写出哪些 drift 被禁止
- 通过 `family_source_refs` 指向此前已批准的页面族工件

不要假设 Stitch 会自动保持壳子一致。如果壳子一致性重要，就必须在 prompt 里直接说清楚。

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

### Harness 闭环的实操规则

当某个 `MB` 要进入 machine-controlled Builder loop 时，按下面顺序运行：

1. 进入或恢复项目时先跑 `preflight.py --level session`
2. 真正执行当前 `MB` 前再跑 `preflight.py --level mb`
3. 读取 `<PROJECT_ROOT>/missions/<mb_id>.md` 和 `<PROJECT_ROOT>/missions/<mb_id>.machine.json`
4. 先要求协议级 `config/execution_policy.json` 存在且合法
5. 让 `mb_runner.py` 组装 Builder prompt，并以显式 `--sandbox workspace-write` 边界调用 Codex CLI
6. 运行强制 hook guards，覆盖 Codex 执行前后
7. 通过 `scope_guard.py` 比较真实工作区变化
8. 如果 scope 失败，立即停止并路由 recovery
9. 如果 scope 通过，再执行 `verifier.py`
10. 把机器状态写回 runtime，并同步 `SESSION_STATE.md`
11. 如果验证失败且仍允许重试，把 `last_verification_digest`、`last_failure_reason` 和 `retry_count` 注入下一轮 prompt
12. 如果验证通过，就关闭当前 `MB`；如果达到重试上限，就路由 recovery

不要把 `last_verification_digest` 当成新的真理源工件。

它只是 `mb_runner` 从最新 `verification_report.json` 提炼出来的 retry 摘要。

这一波里的 `scope_guard.py` 只是 repo 内文件边界审计器。

它会保护 `runtime/state/`、`runtime/memory/`、`runtime/gate_outcomes/` 和 `runtime/locks/` 这些 runtime 自有路径，也可以忽略当前 attempt 目录 `runtime/attempts/<mb_id>/<attempt_id>/` 下的运行产物。

它目前还不提供真正的全系统沙箱能力，也不保证捕获 repo 外写入、网络副作用，或模型内部每一条 shell/network 动作。

### 本地校验

声称协议仓库或项目可交接前，先运行本地 guard：

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`
- `python3 scripts/sdd_guard.py check-gate-outcome /path/to/gate-outcome.json`
