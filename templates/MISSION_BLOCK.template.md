# Mission Block

## Metadata

- `id`:
- `objective`:
- `mode`:

## Scope

- `in_scope`:
- `out_of_scope`:

## Boundaries

- `allowed_files`:
- `forbidden_files`:
- `change_budget`:

## Inputs

- `dependencies`:
- `required_artifacts`:

## Implementation Notes

- `constraints`:
- `required_patterns`:

## Acceptance Checks

- `commands`:
- `tests`:
- `review_conditions`:

## Evidence Required

- `changed_files`:
- `test_evidence`:
- `open_risks`:

## Rollback Notes

- `checkpoint`:
- `safe_revert_path`:

---

## 中文翻译

### Mission Block 模板

#### 元信息

- `id`：任务编号
- `objective`：任务目标
- `mode`：执行模式

#### 范围

- `in_scope`：允许做的内容
- `out_of_scope`：明确不做的内容

#### 边界

- `allowed_files`：允许修改的文件
- `forbidden_files`：禁止修改的文件
- `change_budget`：允许的最大改动面

#### 输入

- `dependencies`：依赖的前置任务或文档
- `required_artifacts`：必须先读的工件

#### 实现说明

- `constraints`：必须遵守的约束
- `required_patterns`：必须遵守的模式

#### 验收检查

- `commands`：需要运行的命令
- `tests`：需要通过的测试
- `review_conditions`：审查时必须满足的条件

#### 必需证据

- `changed_files`：改动过的文件
- `test_evidence`：测试或校验证据
- `open_risks`：尚未解决的风险

#### 回滚说明

- `checkpoint`：回退检查点
- `safe_revert_path`：安全回退路径
