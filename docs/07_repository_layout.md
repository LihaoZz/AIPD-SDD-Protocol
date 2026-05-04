# Repository Layout

## Recommended Layout

```text
.
├── README.md
├── bootstrap/
├── docs/
├── prompts/
├── runtime/
├── schemas/
├── scripts/
└── templates/
```

---

## Directory Roles

| Directory | Purpose |
| :--- | :--- |
| `docs/` | Human-readable protocol guidance and workflow definitions |
| `bootstrap/` | One-repository install, init, and runtime launch entrypoints |
| `prompts/` | Role-specific operating prompts for planning, implementation, and review |
| `runtime/` | Bundled runtime implementations shipped with the protocol |
| `schemas/` | Machine-readable validation contracts |
| `scripts/` | Local validation and guardrail scripts |
| `templates/` | Starter files for real projects |
| external `PROJECT_ROOT` | The active source-of-truth files and implementation state for one real project |

---

## Separation Rule

Do not mix reusable protocol assets with project-specific state.

- reusable rules belong in `docs/`, `prompts/`, `schemas/`, `scripts/`, `templates/`, and bundled runtime directories such as `runtime/symphony/`
- live project truth belongs in the external `PROJECT_ROOT`

This separation makes it easier to reuse the protocol across different products.

---
