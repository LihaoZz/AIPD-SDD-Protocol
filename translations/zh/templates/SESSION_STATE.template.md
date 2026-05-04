### 会话状态模板

#### 当前上下文

- `project`：项目名称
- `mode`：当前模式
- `stage`：当前阶段
- `active_function_block`：当前激活的 function block
- `active_mission_block`：当前激活任务块

#### 最新状态

- `completed`：最近完成了什么
- `failed`：最近失败了什么
- `blocked_by`：当前阻塞项
- `runtime_state_ref`：当前机器状态 JSON 的相对路径
- `last_attempt_id`：最近一次尝试编号
- `last_verification_report_path`：最近一次验证报告路径

#### 必读文件

- artifact 1：接手前第一优先级要读的文件
- artifact 2：接手前第二优先级要读的文件
- artifact 3：接手前第三优先级要读的文件

#### 下一个唯一动作

- `action`：下一步唯一应该做的事

#### 给下一次会话的备注

- `assumptions_still_active`：仍然成立的假设
- `risks_to_watch`：需要继续关注的风险
