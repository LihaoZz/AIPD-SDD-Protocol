# Source Of Truth Artifacts

## Artifact Set

Each project should maintain the following files.

| Artifact | Purpose | Owner | Required |
| :--- | :--- | :--- | :--- |
| `<PROJECT_ROOT>/CONSTITUTION.md` | Product intent, architecture boundaries, stack choices, and non-negotiables | Spec Architect | Yes |
| `<PROJECT_ROOT>/SCOPE.md` | Current user-facing scope and acceptance definition | Spec Architect | Yes |
| `<PROJECT_ROOT>/DECISIONS.md` | Important decisions and why alternatives were rejected | Spec Architect | Yes |
| `<PROJECT_ROOT>/SESSION_STATE.md` | Current stage, current FB, current MB, latest blocker, and next action | Harness runtime syncs it; recovery/spec may repair it when needed | Yes |
| `<PROJECT_ROOT>/QUALITY_RULEBOOK.md` | Global quality profiles, checks, and waiver policy | Spec Architect | Yes |
| `<PROJECT_ROOT>/QUALITY_MEMORY.md` | Human-readable quality memory bridge built from runtime memory plus curated human edits | Harness runtime syncs it; Builder and Reviewer may refine it | Yes |
| `<PROJECT_ROOT>/DATA_MODEL.md` | Core entities, relationships, and persistence rules | Spec Architect | Usually |
| `<PROJECT_ROOT>/API_CONTRACT.md` or `<PROJECT_ROOT>/openapi.yaml` | API behavior and payload rules | Spec Architect | If APIs exist |
| `<PROJECT_ROOT>/VERSION_LOG.md` | Important checkpoints and rollback references | Builder | Recommended |
| `<PROJECT_ROOT>/research/*.md` | Structured research runs, external references, and approved recommendations | Spec Architect or Builder | Optional when research is used |
| `<PROJECT_ROOT>/experience_prompts/*.md` | Approved external-tool handoff prompts with confirmed visual direction and return contract | Spec Architect or Builder | Optional when external UI prompt handoff is used |
| `<PROJECT_ROOT>/function_blocks/*.md` | Product-level delivery units with ontology frame, impact map, acceptance, and MB plan | Spec Architect | Yes before scene planning finishes |
| `<PROJECT_ROOT>/missions/*.md` | Bounded code change units under one active FB | Spec Architect or Builder | Yes before `BUILD` |
| `<PROJECT_ROOT>/missions/*.machine.json` | Machine-readable mission sidecars used by harness validation and execution | Spec Architect or Builder | Yes for runnable `MB`s |
| `<PROJECT_ROOT>/evals/*.json` | Reusable machine-checkable eval assets referenced by one or more `MB`s | Spec Architect or Builder | Recommended when checks should be reused |
| `<PROJECT_ROOT>/runtime/state/*.state.json` | Machine-readable current execution state for one `MB` | Harness runtime | Yes when harness is used |
| `<PROJECT_ROOT>/runtime/attempts/**` | Per-attempt prompts, raw outputs, diffs, scope checks, and verification reports | Harness runtime | Yes when harness is used |
| `<PROJECT_ROOT>/runtime/memory/project_memory.json` | Cross-session validated knowledge from completed work | Harness runtime | Recommended when harness is used |
| `<PROJECT_ROOT>/runtime/memory/failure_log.json` | Cross-attempt failure patterns and rejected fixes | Harness runtime | Recommended when harness is used |
| `<PROJECT_ROOT>/runtime/preflight/*.json` | Session and MB preflight results | Harness runtime | Yes when harness is used |
| `<PROJECT_ROOT>/reviews/*.json` | Evidence-based quality reports that match the quality report schema | Reviewer | Yes before `CLOSE` |

## Ownership Rule

The Builder may read all source-of-truth artifacts.

The Builder may not freely rewrite them during implementation. If implementation reveals a mismatch, the Builder must raise a spec conflict instead of silently changing the contract.

Allowed cases for artifact changes:

- the active FB or MB explicitly authorizes the update
- the session is in `SPEC`
- the session is in `recovery` and the recovery plan requires documentation repair
- the session writes a lesson into `QUALITY_MEMORY.md`

When an `FB` uses `external_ui_package` or `hybrid`, the external UI package itself may live outside the standard protocol files, but the authoritative references to that package must be recorded in the parent `FB`, dependent `MB`s, and `SESSION_STATE.md` when relevant.

That external UI package is an implementation input, not a replacement for protocol truth.

The authority order remains:

1. active `FB`
2. active `MB`
3. `QUALITY_RULEBOOK.md`
4. external UI package

The external UI package only governs experience presentation. It does not override ontology, task scope, acceptance, business rules, or quality gates.

Research artifacts follow the same authority model.

They may inform decisions, specs, and implementation notes, but they do not replace:

1. active `FB`
2. active `MB`
3. `QUALITY_RULEBOOK.md`

If research changes product truth, tool choice, or implementation direction, record the adopted result in project artifacts rather than leaving it only in chat.

## Session State Rule

`<PROJECT_ROOT>/SESSION_STATE.md` is the minimum restart file.

It should always answer:

- which mode the project is in
- which stage the work is in
- which function block is active
- which mission block is active
- what was completed
- what failed
- what the next single action is
- which artifacts must be read first

Without this file, every new conversation wastes time reconstructing context and may drift.

When the harness is active, `SESSION_STATE.md` is runtime-managed.

That means:

- the Builder reads it as context
- `state_writer.py` syncs it after runtime state changes
- runnable `MB`s should not list `SESSION_STATE.md` under `required_artifact_updates`

## Runtime Memory Rule

When the harness is active, machine memory lives in:

- `<PROJECT_ROOT>/runtime/memory/project_memory.json`
- `<PROJECT_ROOT>/runtime/memory/failure_log.json`

`QUALITY_MEMORY.md` is the bridge summary for humans.

Do not treat `QUALITY_MEMORY.md` as the machine memory source of truth.

## FB, MB, And Quality Report Storage

Function blocks should live in `<PROJECT_ROOT>/function_blocks/`.

Mission blocks should live in `<PROJECT_ROOT>/missions/`.

Machine sidecars should live next to their mission markdown files as `<PROJECT_ROOT>/missions/<mb_id>.machine.json`.

Quality reports should live in `<PROJECT_ROOT>/reviews/`.

Harness runtime artifacts should live under `<PROJECT_ROOT>/runtime/`.

Each mission block should inherit from its parent FB instead of copying the full ontology frame.

## Function Block Content Rule

An `FB` is the product anchor, not a running log of every code attempt.

Its main body should contain:

- metadata
- product goal
- 8-element ontology frame
- 8-layer impact map
- `experience_delivery_mode`
- scope
- acceptance
- mission plan

Conditional fields:

- if `experience_delivery_mode` is `external_ui_package` or `hybrid`, include `experience_input_artifacts` and `experience_builder_scope`

Optional Appendix:

- dependencies
- related artifacts
- overall risk
- special quality concerns
- release blockers
- completed or failed MB history
- open questions

Use the appendix only when it materially improves execution clarity.

Optional Appendix additions:

- `research_needed`
- `research_questions`
- `experience_prompt_needed`

## Mission Block Content Rule

An `MB` is the smallest bounded implementation unit.

Its main body should contain:

- metadata
- parent FB alignment
- goal
- allowed files
- quality plan
- required evidence
- result

Conditional fields:

- `input_artifacts` only when upstream inputs are required; otherwise use `none`
- `input_ready_check` only when `input_artifacts` is not `none`

Optional Appendix:

- extra boundary notes
- baseline details
- rollback details
- waived checks
- change budget and risk notes

Keep the main body small enough that the Builder can execute it without hunting through low-value fields.

The `input_artifacts` field records execution dependencies only. It does not replace the parent `FB` or the active `MB` as the task authority.

If research is needed for the active slice, record either:

- the adopted research result in the active `MB`
- or a reference to the relevant `RESEARCH_NOTE`

Optional Appendix additions:

- `research_inputs`
- `external_tool_prompt_ref`

Harness rule:

- each runnable `MB` should declare one machine sidecar reference in its markdown body
- machine sidecars may also reference reusable `evals/*.json`
- the full verification evidence for one attempt belongs in `<PROJECT_ROOT>/runtime/attempts/<mb_id>/<attempt_id>/verification_report.json`
- the retry prompt summary derived from that report is not a separate truth file
- the current machine state should store `last_verification_report_path` instead of inventing alternate names
- `required_artifact_updates` should list only direct Builder-managed source-of-truth files
- for runnable `MB`s, do not list `SESSION_STATE.md` there because harness runtime syncs it automatically

Reference rule:

- `research_inputs` should list comma-separated relative paths to `research/*.md`
- `external_tool_prompt_ref` should point to one relative path under `experience_prompts/*.md`

## Research Note Rule

Use a `RESEARCH_NOTE` when a search run produces reusable facts, candidate tools, UI references, or technical guidance that should survive the chat session.

A `RESEARCH_NOTE` should capture:

- the trigger type
- the role that owns the search
- the query and why it is needed now
- the sources and facts collected
- the candidates considered
- the recommendation
- the impact on the current `FB` or `MB`
- whether user approval was required and whether it was granted

UI-related research may support style exploration, but it does not finalize visual direction.

Before any external-tool UI prompt is generated, the user must confirm:

- which references are adopted
- the final visual direction
- the design core

## Experience Prompt Rule

Use an `EXPERIENCE_PROMPT` artifact when the assistant prepares a handoff prompt for Figma, Stitch, or another prompt-driven external experience tool.

An `EXPERIENCE_PROMPT` should capture:

- the parent `FB` and related `MB`s
- the `page_family_id` when the prompt belongs to a shared page family
- the `prompt_goal_type` and `consistency_mode` that explain what this prompt is trying to do
- any `family_source_refs` that define the existing family contract
- the confirmed visual direction and design core
- the confirmed UI decisions that materially affect output quality
- the shared shell contract when same-family consistency matters, including what must be preserved, what may vary, and what drift is forbidden
- the approved reference set
- the page or component goal
- the states, branches, and flows that must be covered
- the must-do and must-not-do constraints
- the prompt requirements and tool-specific notes that shape how the external tool should be instructed
- the expected returned artifacts for intake
- the final copy-paste-ready prompt text for the external tool

This prompt artifact is part of source-of-truth handoff context. It should not live only in chat, and it is not complete if it contains only direction notes without the final prompt body.

Do not treat every prompt as the same shape. Choose the prompt strategy that matches the task:

- `canonical_shell` when defining a page family shell for the first time
- `state_variant` when keeping the same shell and generating additional states
- `family_extension` when extending the same family with a bounded new region or capability
- `independent_screen` when the screen does not share a shell contract with other work

Treat prompt strategy as two axes:

- `prompt_goal_type` explains the structural goal of the prompt
- `tool_guidance_profile` explains how the target tool should be guided

Recommended `tool_guidance_profile` values:

- `stitch_first_pass` for the first high-detail Stitch generation of one screen or family shell
- `stitch_iterative_refine` for later Stitch edits that should stay screen-focused and tightly scoped
- `figma_structured_handoff` for richer, more complete Figma handoff prompts
- `general_structured_handoff` for other tools when no stronger profile exists

Use `same_family_strict` when the shell and component language should remain fixed except for explicitly named variation.

Use `same_family_adaptive` when the same page family should stay recognizable but a bounded region is allowed to change more visibly.

For Stitch, prefer plain-language prompts and screen-by-screen refinement. Same-family prompts should explicitly preserve the shared shell instead of trusting the tool to infer it.
