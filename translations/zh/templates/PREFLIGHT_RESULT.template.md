### Preflight 结果模板

#### 元信息

- `scene`：用户请求的场景
- `project_root`：项目根目录
- `preflight_result`：预检结果
- `can_enter_scene`：是否可以进入该场景

#### 已检查项目

- `checked_files`：已检查文件
- `checked_directories`：已检查目录
- `state_references_checked`：已检查的状态引用

#### 缺失项目

- `missing_foundations`：缺失的基础制度文件
- `missing_scene_requirements`：缺失的场景必需项
- `stale_or_inconsistent_items`：过期或不一致项

#### 自动动作

- `auto_actions`：系统将自动执行的动作
- `bootstrap_scope`：本次自动补齐范围

#### 阻塞项

- `blocking_items`：阻塞进入场景的项目
- `minimal_user_input_needed`：仍需用户提供的最小信息

#### 结论

- `recommended_next_step`：建议的下一步
- `scene_entry_decision`：场景进入判断

#### 使用规则

- 每次新对话在进入请求场景前，都必须先生成一份 preflight 结果。
- `preflight_result` 只允许三种取值：
  `ready`、
  `bootstrap_required`、
  `blocked`。
- 只有当系统能够安全进入请求场景时，`can_enter_scene` 才能为 `true`。
- 如果结果是 `bootstrap_required`，系统应先自动补齐安全的基础制度文件，再进入场景。
- 如果结果是 `blocked`，系统只应询问最小必要缺失信息。
