# Repository Layout

## Recommended Layout

```text
.
├── README.md
├── docs/
├── prompts/
├── schemas/
├── scripts/
└── templates/
```

---

## Directory Roles

| Directory | Purpose |
| :--- | :--- |
| `docs/` | Human-readable protocol guidance and workflow definitions |
| `prompts/` | Role-specific operating prompts for planning, implementation, and review |
| `schemas/` | Machine-readable validation contracts |
| `scripts/` | Local validation and guardrail scripts |
| `templates/` | Starter files for real projects |
| external `PROJECT_ROOT` | The active source-of-truth files and implementation state for one real project |

---

## Separation Rule

Do not mix reusable protocol assets with project-specific state.

- reusable rules belong in `docs/`, `prompts/`, `schemas/`, `scripts/`, and `templates/`
- live project truth belongs in the external `PROJECT_ROOT`

This separation makes it easier to reuse the protocol across different products.

---

## 中文翻译

### 推荐目录结构

协议仓库：

```text
.
├── README.md
├── docs/
├── prompts/
├── schemas/
├── scripts/
└── templates/
```

真实项目：

```text
<PROJECT_ROOT>/
├── CONSTITUTION.md
├── SCOPE.md
├── DECISIONS.md
├── QUALITY_RULEBOOK.md
├── QUALITY_MEMORY.md
├── SESSION_STATE.md
├── research/
├── experience_prompts/
├── function_blocks/
├── missions/
│   ├── fb1-mb1.md
│   └── fb1-mb1.machine.json
├── runtime/
│   ├── attempts/
│   ├── state/
│   ├── memory/
│   └── preflight/
└── reviews/
```

### 目录职责

| 目录 | 用途 |
| :--- | :--- |
| `docs/` | 给人阅读的协议说明和流程定义 |
| `prompts/` | 规划、实现和审查等不同角色的提示词 |
| `schemas/` | 机器可读的校验契约 |
| `scripts/` | 本地校验和守门脚本 |
| `templates/` | 真实项目可复用的模板文件 |
| 外部 `PROJECT_ROOT` | 某个真实项目当前的真理源文件和实现状态 |

### 分层规则

不要把可复用的协议资产和项目专属状态混在一起。

- 可复用规则放在 `docs/`、`prompts/`、`schemas/` 和 `templates/`
- 某个真实项目的当前状态和 harness 运行产物放在外部 `PROJECT_ROOT`

这样分层后，这套协议会更容易复用到不同产品中。
