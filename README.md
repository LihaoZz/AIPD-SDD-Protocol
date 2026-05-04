# SDD Protocol Repository

## What This Repository Is

This repository is a protocol system for AI-assisted product development.

It is the single distribution repository for the AIPD framework.

It is not the product codebase itself.

It stores:

- operating rules
- lifecycle definitions
- role prompts
- templates
- validation tools
- hook entrypoints
- bundled Symphony runtime integration under `runtime/symphony/`
- bootstrap entrypoints for one-command local setup under `bootstrap/`

Harness runtime outputs and real product state still belong in the external
`PROJECT_ROOT`, not in this repository.

Direct Codex execution in this protocol should go through `scripts/codex_exec_with_hooks.py` so the mandatory hook layer stays active even outside `mb_runner.py`.

## Core Idea

Less is more.

This protocol prefers:

- the smallest useful scope
- the clearest document
- the fewest moving parts
- the smallest safe code change
- evidence over confidence
- approved external visual authority over improvised UI styling when the experience layer is not Builder-owned

Do not add complexity just to look complete.

## Three Layers

- `PROTOCOL_ROOT`
  This repository. It contains the reusable rules, prompts, templates, scripts,
  bundled runtime, and bootstrap helpers.
- `RUNTIME_ROOT`
  The bundled Symphony implementation under `runtime/symphony/`. It is shipped
  with the protocol repo so users can download one repository, but it remains a
  runtime layer rather than project truth.
- `PROJECT_ROOT`
  The real product workspace. It contains the source-of-truth files and implementation state for one project.

Keep these layers separate even though they are shipped from one repository.

## Quick Start

Clone this repository once, then use the bundled bootstrap entrypoints:

```bash
git clone <repo-url>
cd Product-Dev
bootstrap/install.sh
bootstrap/init_project.sh /path/to/my-project
bootstrap/run_symphony.sh /path/to/my-project
```

What each command does:

- `bootstrap/install.sh`
  verifies the local runtime prerequisites for AIPD and bundled Symphony
- `bootstrap/init_project.sh`
  initializes a new external `PROJECT_ROOT` from the bundled templates
- `bootstrap/run_symphony.sh`
  renders an AIPD-compatible Symphony workflow file and starts the bundled
  orchestrator

The first product-specification session should still begin in Codex with:

1. `Protocol Root`
2. `Project Root`
3. `Scene`
4. product idea

Symphony is for MB orchestration after the project truth and runnable MBs exist.

## Startup Contract

`README.md` is the only main entry.

When a new conversation starts, the agent should read this file first.

The user should be allowed to start with only:

1. repository link or local protocol root
2. scene

Optional third input:

- product idea
- feature request
- blocker
- review target
- project root path if the current workspace is not already the real project

If `PROJECT_ROOT` is not explicitly given, treat the current real working project directory as `PROJECT_ROOT`.

Do not ask the user to restate internal protocol paths.

## End-To-End View

| Phase | What The User Does | What The Protocol Does | Main Output |
| :--- | :--- | :--- | :--- |
| `Kickoff` | Describe the product idea, pain point, or desired feature in plain language | Identify scene and gather missing business context | Initial understanding |
| `Discovery` | Answer focused product questions | Reduce ambiguity and surface facts, assumptions, risks, and out-of-scope items | Discovery notes |
| `Specification` | Confirm the proposed direction | Write or update source-of-truth artifacts and define scope boundaries | Stable project truth |
| `Planning` | Approve or adjust priorities | Split work into function blocks and mission blocks | Bounded delivery plan |
| `External UI Handoff` | Provide or approve external UI output when needed | Record `experience_delivery_mode`, persist the handoff prompt when relevant, and wait for the approved package before dependent UI integration work | External UI package, approved experience prompt, or explicit Builder-owned decision |
| `Implementation` | Observe progress and answer business tradeoff questions when needed | Implement one mission block at a time under the active function block | Code plus evidence |
| `Review` | Decide whether findings are acceptable or need correction | Audit scope, correctness, and quality gates | Structured quality report |
| `Recovery` | Clarify priorities if work is blocked or broken | Restore a controlled next move instead of improvising | Recovery plan |
| `Closure` | Confirm whether to continue, pause, or release | Update project state for the next session | Current project state |

## What A Good Session Looks Like

1. The session starts by identifying the scene.
2. The agent runs `Project Preflight` before entering scene work.
3. The protocol asks enough questions to remove dangerous ambiguity.
4. The protocol writes the answers into stable artifacts.
5. If the experience layer is externally delivered, the handoff contract is recorded in artifacts before dependent UI integration work starts.
6. The implementation work is cut into small bounded units.
7. The Builder executes one bounded unit at a time.
8. Review is based on evidence, not on confidence.
9. Before ending, the current project state is written for the next session.
10. When runnable MBs exist, the bundled Symphony runtime can dispatch them in
    parallel under AIPD gate control.

## Failure Modes This Protocol Tries To Prevent

- coding before the product goal is clear
- the model inventing hidden requirements
- the model inventing UI styling that should have come from an external visual authority
- the model touching unrelated files
- "done" claims without evidence
- new sessions losing context and drifting
- technical debt caused by unbounded implementation

## Scenes

Supported scenes:

- `greenfield`
- `expansion`
- `continue`
- `review`
- `recovery`

If the user gives a fuzzy label, map it to the nearest scene before continuing.

## Automatic Reading Path

Before entering any scene workflow, the machine default should consume `generated/protocol_compact.json`.

Use the full English authority docs only when:

- the compact summary is missing or stale
- the protocol itself is being edited
- a contract dispute or recovery investigation needs source verification

After loading the compact summary, the agent must:

1. run `Project Preflight`
2. return a short `Preflight Summary`
3. classify the project state as `ready`, `bootstrap_required`, or `blocked`
4. map the scene-specific path from [docs/00_lifecycle.md](docs/00_lifecycle.md)
5. activate the first role
6. continue automatically only when safe

Use `templates/PREFLIGHT_RESULT.template.md` as the preflight structure.

Machine default startup artifact:

- `generated/protocol_compact.json`

English authority references:

- `README.md`
- [docs/00_lifecycle.md](docs/00_lifecycle.md)
- [docs/06_session_bootstrap.md](docs/06_session_bootstrap.md)
- [HARNESS.md](HARNESS.md) when one `MB` is expected to run through the harness loop

Scene-specific priorities:

### `greenfield`

First role:

- `Spec Architect`

Read next:

- [docs/01_principles.md](docs/01_principles.md)
- [docs/02_artifacts.md](docs/02_artifacts.md)
- [docs/05_operating_playbook.md](docs/05_operating_playbook.md)
- core templates for constitution, scope, FB, MB, quality, and session state

### `expansion`

First role:

- `Spec Architect`

Read next:

- [docs/02_artifacts.md](docs/02_artifacts.md)
- [docs/03_mission_blocks.md](docs/03_mission_blocks.md)
- [docs/05_operating_playbook.md](docs/05_operating_playbook.md)
- current project truth in `PROJECT_ROOT`

### `continue`

First role:

- `Builder` if state is healthy
- `Spec Architect` or `Recovery Coordinator` if state is blocked or drifting

Read next:

- [docs/04_review_recovery.md](docs/04_review_recovery.md) when needed
- [docs/05_operating_playbook.md](docs/05_operating_playbook.md)
- current `SESSION_STATE.md`, active `FB`, active `MB`, and required input artifacts

### `review`

First role:

- `Reviewer`

Read next:

- [docs/04_review_recovery.md](docs/04_review_recovery.md)
- `schemas/quality-report.schema.json`
- relevant project truth, active `FB`, active `MB`, and required evidence

### `recovery`

First role:

- `Recovery Coordinator`

Read next:

- [docs/04_review_recovery.md](docs/04_review_recovery.md)
- current `SESSION_STATE.md`
- latest affected artifacts and evidence

For the exact scene path, always defer to [docs/00_lifecycle.md](docs/00_lifecycle.md).

Chinese reference files are generated under `README.zh.md`, `docs/zh/`, and `templates/zh/`.

They are for human reading only. The English source files remain authoritative.

## Minimum Startup Checklist

Before a real project can run smoothly, prepare at least:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`

Optional when used:

- `<PROJECT_ROOT>/research/*.md`
- `<PROJECT_ROOT>/experience_prompts/*.md`

If the system has APIs or persistence, also prepare:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml`

## Canonical Document Map

Authority order:

1. [docs/00_lifecycle.md](docs/00_lifecycle.md)
2. [docs/01_principles.md](docs/01_principles.md)
3. [docs/02_artifacts.md](docs/02_artifacts.md)
4. [docs/03_mission_blocks.md](docs/03_mission_blocks.md)
5. [docs/04_review_recovery.md](docs/04_review_recovery.md)

Support documents:

- [docs/05_operating_playbook.md](docs/05_operating_playbook.md)
- [docs/06_session_bootstrap.md](docs/06_session_bootstrap.md)
- [docs/07_repository_layout.md](docs/07_repository_layout.md)

Historical reference only:

- [docs/99_legacy_master_protocol_v4.md](docs/99_legacy_master_protocol_v4.md)

## Bundled Runtime

The repository now ships a bundled Symphony runtime at
`runtime/symphony/`.

This gives users a one-repository download path, but it does not change the
semantic boundary:

- AIPD defines lifecycle truth, gate contracts, schemas, and verification
- Symphony handles orchestration, workspace creation, and Codex session dispatch
- the external `PROJECT_ROOT` remains the source of truth for any real product
