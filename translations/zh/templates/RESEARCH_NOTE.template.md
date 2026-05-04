### Research Note 模板

#### 元信息

- `research_id`：research 记录编号
- `trigger_type`：触发类型
- `owner_role`：负责这次 research 的角色
- `date`：日期

#### 查询信息

- `query`：检索问题
- `why_now`：为什么现在要查

#### 事实结果

- `sources`：信息来源
- `facts`：确认的事实

#### 候选项

- `candidates`：候选方案
- `recommendation`：推荐结论

#### 影响与采纳

- `impact_on_fb_or_mb`：对当前 FB 或 MB 的影响
- `adopted_decision_ref`：被采纳决策的引用
- `deferred_questions`：延期问题

#### 审批

- `user_approval_required`：是否需要用户审批
- `user_approval_status`：审批状态

#### 使用规则

- 当 research 产出可复用事实、候选方案或建议时，使用这个工件。
- `trigger_type` 只能是 `user_triggered` 或 `system_triggered`。
- `user_triggered` research 应使用 `user_approval_required: no` 和 `user_approval_status: not_required`。
- 如果是 `system_triggered`，必须先把 `user_approval_required` 设为 `yes`，并把 `user_approval_status` 记录为 `approved`。
- 如果这条记录影响当前工作，必须把采纳结论同步到 `DECISIONS`、当前 `FB` 或当前 `MB`。
- UI 相关 research 可以提供参考，但生成外部工具 prompt 前必须由用户确认最终视觉方向。
