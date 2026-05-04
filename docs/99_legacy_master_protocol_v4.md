# SDD Master Protocol v4

> Historical reference only.
>
> This file is preserved for traceability and comparison.
> The current authority lives in `README.md` and `docs/00_lifecycle.md`.

## Positioning

This is an AI software delivery protocol designed for non-technical users.

The goal is not to make the model "smarter." The goal is to make the model less likely to improvise, swap requirements, or accumulate technical debt in long-running projects.

This protocol assumes:

- the user understands business goals but not technical implementation details
- the model can write code, but will improvise when boundaries are unclear
- new sessions and new models should not depend on chat memory to continue work
- reliable context must be written into repository files

One function should be understood in two complementary ways:

- an `ontology frame` that defines what the function is
- an `impact map` that defines where the function lands in engineering

---

## Core Principles

1. Do not enter implementation before the problem is written clearly enough.
2. Design, implementation, and review must be separated instead of being handled by one role talking to itself.
3. Important decisions must be stored in repository files, not left in chat history.
4. Tasks must have boundaries. Do not hand the model a broad goal and let it start coding.
5. Completion must be based on evidence, not self-reporting.
6. Less is more. Always keep it simple.
7. After failure, return to the correct stage instead of repeating blind attempts.
8. When the experience layer is externally delivered, treat the external UI package as an input authority instead of asking the Builder to invent the visual design.

---

## Five Roles

| Role | Function | Description |
| :--- | :--- | :--- |
| User | Provides business goal, priorities, acceptance standard, and tradeoffs | Does not own implementation details |
| Spec Architect | Translates business language into specs, boundaries, and tasks | Responsible for reducing ambiguity |
| Builder | Implements code within task boundaries | Does not own scope expansion |
| Reviewer | Audits work against specs and evidence | Does not trust verbal completion claims |
| Recovery Coordinator | Repairs broken state and routes recovery work | Does not continue implementation by instinct |

---

## Lifecycle

Projects do not follow one identical path in every scene.

They run through four execution layers:

1. `Preflight`
2. `Scene Path`
3. `Role Handoff`
4. `Issue Routing`

The universal control shell is:

1. `PREFLIGHT`
2. `INIT`
3. `SCENE_WORK`
4. `REVIEW_GATE`
5. `CLOSE`

See [docs/02-lifecycle.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/02-lifecycle.md) for the detailed definition.

---

## Repository Principle

This protocol no longer stores everything in one oversized file. It is split into modules:

- roadmap: [docs/00-roadmap.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/00-roadmap.md)
- principles and writing style: [docs/01-principles.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/01-principles.md)
- lifecycle: [docs/02-lifecycle.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/02-lifecycle.md)
- source-of-truth artifacts: [docs/03-artifacts.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/03-artifacts.md)
- task boundaries: [docs/04-mission-blocks.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/04-mission-blocks.md)
- review and recovery: [docs/05-review-recovery.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/05-review-recovery.md)
- operating flow: [docs/06-operating-playbook.md](/Users/lihaozheng/Documents/AI/Product-Dev/docs/06-operating-playbook.md)

---

## Why v4 Is More Stable Than The Old Version

Compared with the single-file version, v4 makes several upgrades:

- it no longer depends on heavy visual emphasis to communicate priority, and instead depends on stable structure and explicit fields
- it no longer ends discovery when the user says "stop," and instead requires written facts, assumptions, risks, and intentionally excluded items
- it no longer stops at abstract principles, and instead adds templates, role prompts, and machine-readable schema
- it no longer lets new sessions recover from memory, and instead requires `SESSION_STATE.md` as the recovery entry point
- it no longer jumps directly into a scene, and instead requires `Project Preflight` before scene execution
- it no longer gives the coding agent a broad task, and instead requires each function block and mission block to define scope, boundaries, quality checks, and rollback notes
- it no longer assumes the Builder always authors the UI, and instead records when the experience layer is handed off to an external tool before integration work begins

---

## Minimum Execution Rules

If only the most important rules survive, keep at least these five:

1. Before coding, `CONSTITUTION.md`, `SCOPE.md`, `DECISIONS.md`, and `SESSION_STATE.md` must exist.
2. Every implementation flow must have an active `Function Block` and a current `Mission Block`.
3. Every new conversation must begin with `Project Preflight`.
4. The Builder must not go beyond `allowed_files`.
5. Review must use structured output.
6. `SESSION_STATE.md` must be updated before every session ends.
7. If the user provides only repository plus scene, the agent must bootstrap from repository rules instead of asking for internal document paths again.
8. If the `experience` layer is affected, the parent `FB` must record `experience_delivery_mode` before any dependent UI integration `MB` begins.

---

## Relationship To The Repository

This repository is the protocol product itself, not a specific business application.

- the protocol lives in `docs/`, `prompts/`, `schemas/`, and `templates/`
- the live state of one concrete project lives in an external `PROJECT_ROOT`

That separation makes the SDD reusable instead of forcing you to rewrite the prompt system from scratch every time.

---

## Bootstrap Entry

This repository is designed to support a minimal startup message:

- repository link or local root
- scene

The routing rule lives in `README.md`.

The scene-to-file map lives in `docs/08-session-bootstrap.md`.

---
