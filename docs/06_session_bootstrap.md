# Session Bootstrap

This document explains how an agent should begin when the user provides only a repository and a scene.

It is a startup helper, not the authority for lifecycle rules.

## Global Bootstrap Files

For every scene, the machine default should read this first:

- `generated/protocol_compact.json`

Then return to these English authority files only when the compact summary is missing, stale, under protocol edit, or insufficient to resolve a contract dispute:

- `README.md`
- `docs/00_lifecycle.md`
- `docs/05_operating_playbook.md`
- `HARNESS.md` when the active `MB` is expected to run through the harness loop

These files define:

- what the protocol is
- what the lifecycle authority is
- how to run preflight
- how to operate the current scene safely
- how runtime naming, retry feedback, and machine state work when harness execution is enabled

## Preflight Summary Structure

After reading the compact startup summary, run `Project Preflight` before entering the requested scene.

The summary should contain:

1. requested scene
2. project root
3. preflight result
4. whether the scene can start now
5. active role
6. scene path
7. missing items
8. automatic actions
9. blocking items, if any

Use `templates/PREFLIGHT_RESULT.template.md` for the structure.

## Scene Reading Priorities

Follow the exact scene path from `docs/00_lifecycle.md`.

Use this document only to choose what to read first.

If the active role sees a need for research, follow `Research Rule` in `docs/00_lifecycle.md` instead of searching by default.

### `greenfield`

Read after the compact startup summary:

- `docs/01_principles.md`
- `docs/02_artifacts.md`
- core templates for constitution, scope, FB, MB, quality, and session state

First role:

- `Spec Architect`

First action:

- ask business questions until the 8 ontology elements and affected layers can be written
- if external facts or tool discovery would materially help, request user approval before any system-triggered research

Do not:

- start coding
- force early technical stack choices

### `expansion`

Read after the compact startup summary:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- `<PROJECT_ROOT>/DECISIONS.md`
- `<PROJECT_ROOT>/SESSION_STATE.md`
- `docs/02_artifacts.md`
- `docs/03_mission_blocks.md`
- `<PROJECT_ROOT>/QUALITY_RULEBOOK.md`
- `<PROJECT_ROOT>/QUALITY_MEMORY.md`

Read these too when relevant:

- `<PROJECT_ROOT>/DATA_MODEL.md`
- `<PROJECT_ROOT>/API_CONTRACT.md`

First role:

- `Spec Architect`

First action:

- identify what the feature changes, what current assumption it may break, and what FB detail must exist before coding
- if market scan, similar-product review, or tool discovery would materially help, request user approval before any system-triggered research

Do not:

- start implementing before specs are updated

### `continue`

Read after the compact startup summary:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current function block
- current mission block
- current mission machine spec when it exists
- required input artifacts when the current FB or MB depends on them

Also read when needed:

- `docs/04_review_recovery.md`

First role:

- `Builder` if the state is healthy
- `Spec Architect` or `Recovery Coordinator` if the state is blocked or drifting

First action:

- name the current stage and the next single action
- if harness execution is used, run `preflight.py --level mb` before invoking the Builder loop
- if a bounded technical gap needs external facts, request user approval before any system-triggered research

Do not:

- restart the whole project from zero

### `review`

Read after the compact startup summary:

- `<PROJECT_ROOT>/CONSTITUTION.md`
- `<PROJECT_ROOT>/SCOPE.md`
- relevant function block
- relevant mission block
- relevant input artifacts or design authority when the parent FB depends on them
- relevant contract files
- `docs/04_review_recovery.md`
- `schemas/quality-report.schema.json`

First role:

- `Reviewer`

First action:

- audit against written artifacts and evidence

Do not:

- patch code during the review pass unless the user changes the task

### `recovery`

Read after the compact startup summary:

- `<PROJECT_ROOT>/SESSION_STATE.md`
- current function block if it exists
- current mission block if it exists
- `<PROJECT_ROOT>/VERSION_LOG.md` if it exists
- `<PROJECT_ROOT>/QUALITY_MEMORY.md` if it exists
- `docs/04_review_recovery.md`
- relevant broken-area artifacts

First role:

- `Recovery Coordinator`

First action:

- classify the failure and choose the smallest safe move

Do not:

- continue implementation by instinct

## First Reply Template

After bootstrapping, the first real reply should contain:

1. selected scene
2. preflight result
3. whether the scene can start now
4. active role
5. scene path
6. files read
7. files missing, if any
8. next question or next action

That reply should be short and operational.

## Minimal User Messages

The repository is designed so the user can start with messages like:

- `Repo: <repo-link>\nScene: greenfield`
- `Repo: <repo-link>\nScene: expansion`
- `Repo: <repo-link>\nScene: continue`
- `Repo: <repo-link>\nScene: review`
- `Repo: <repo-link>\nScene: recovery`

Optional third line:

- product idea
- feature request
- blocker
- review target

## Important Limitation

This rule works only if the model or tool can actually read the repository contents from the link or local root.

If access is missing, the user must provide access by:

- giving the local path
- uploading the files
- or using a tool that can browse the repository

Chinese reference documents are generated under `docs/zh/` and are not authority files.
