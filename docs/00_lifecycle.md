# Lifecycle

This document is the only normative lifecycle source in the protocol repository.

## Session Modes

Use one main mode per session.

| Mode | Use When | Required Inputs | Expected Output |
| :--- | :--- | :--- | :--- |
| `greenfield` | Starting a new product or feature set | Business goal, user problem, known constraints | Initial specs, quality setup, and first FB plan |
| `expansion` | Adding one new capability to an existing system | Existing source-of-truth files plus the new goal | Delta spec and detailed FB/MB plan |
| `continue` | Resuming interrupted work | Current session state, active FB, active MB, latest progress or failure notes | Next bounded action |
| `review` | Auditing completed implementation | Diff, evidence, and relevant source-of-truth files | Structured quality report |
| `recovery` | Repairing a broken or confused state | Error evidence, recent changes, and current state | Recovery path with the smallest safe move |

## Preflight Rule

Before `INIT`, the agent must run `Project Preflight` against the working path.

The preflight must classify the project as:

- `ready`
- `bootstrap_required`
- `blocked`

If the result is `bootstrap_required`, initialize safe foundational files before entering the requested scene.

If the result is `blocked`, ask only for the minimum missing context.

## Four Execution Layers

The lifecycle is a four-layer execution model:

| Layer | Purpose | Question It Answers |
| :--- | :--- | :--- |
| `Preflight` | Check whether work can safely begin | Can the requested scene start now? |
| `Scene Path` | Select the required work sequence for one scene | What kind of work must happen next? |
| `Role Handoff` | Transfer responsibility during normal progress | Who should act at this step? |
| `Issue Routing` | Return discovered problems to the correct owner | Who must resolve this problem? |

Always apply them in this order:

1. run `Preflight`
2. enter the requested `Scene Path`
3. activate the correct role through `Role Handoff`
4. if a problem is found, stop forward motion and use `Issue Routing`

## Universal Control Shell

All scenes share the same control shell.

| Stage | Purpose | Exit Criteria |
| :--- | :--- | :--- |
| `PREFLIGHT` | Check startup readiness and classify project state | State is `ready`, `bootstrap_required`, or `blocked` |
| `INIT` | Identify mode, project, active artifacts, and first role | Scene, files, and role are explicit |
| `SCENE_WORK` | Execute the scene-specific required path | Required scene outputs exist or a role handoff is triggered |
| `REVIEW_GATE` | Validate evidence, quality gates, and impact | Pass, fail, rework, or reroute decision exists |
| `CLOSE` | Persist current state for later sessions | Session state and next step are written |

## Scene-Specific Required Paths

| Scene | Required Path | Working Focus | First Role |
| :--- | :--- | :--- | :--- |
| `greenfield` | `DISCOVERY -> SPEC -> QUALITY_SETUP -> FB_PLANNING -> HANDOFF_DECISION` | Define product truth, initial quality system, and first FBs | `Spec Architect` |
| `expansion` | `FEATURE_DISCOVERY -> DELTA_SPEC -> FB_DETAILING -> MB_PLANNING -> HANDOFF_DECISION` | Define the new feature, impact surface, regression risk, and detailed FB | `Spec Architect` |
| `continue` | `STATE_RECONSTRUCTION -> NEXT_ACTION_SELECTION -> HANDOFF_DECISION` | Reconstruct state and continue the next single safe action | `Builder`, `Spec Architect`, or `Recovery Coordinator` depending on state |
| `review` | `AUDIT_PREP -> EVIDENCE_REVIEW -> QUALITY_REPORTING` | Audit implementation against FB, MB, artifacts, and evidence | `Reviewer` |
| `recovery` | `FAILURE_CLASSIFICATION -> RECOVERY_DECISION -> STATE_REPAIR -> HANDOFF_DECISION` | Stop drift, repair state, and choose the smallest safe move | `Recovery Coordinator` |

## Experience Delivery Gate

When the ontology frame and impact map are clear enough for planning, the `Spec Architect` must decide whether the experience layer is Builder-owned or externally delivered.

This decision must be stored in the parent `FB` as `experience_delivery_mode`.

Allowed values:

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

This is a gate inside `SPEC` or `FB_DETAILING`, not a separate scene stage.

If the mode is `external_ui_package` or `hybrid`, the parent `FB` must also record:

- required external input artifacts
- the Builder's allowed integration scope

Any dependent `MB` must remain inactive until those required inputs exist and are readable.

## Research Rule

`Research` is a support capability, not a new scene, role, or stage.

Use it mainly in:

- `Spec Architect` work during `DISCOVERY`, `SPEC`, or `FB_DETAILING`
- `Builder` work inside the active `MB`

Two trigger types are allowed:

- `user_triggered`: the user explicitly asks for search or lookup work
- `system_triggered`: the active role sees a material need for external facts, tools, references, or technical solutions

Execution rule:

- `user_triggered` research may run immediately
- `system_triggered` research requires user approval before any search begins
- do not perform silent network research

Accepted uses include:

- simple market scan or similar-product review during spec work
- searching for mature tools, libraries, services, or open-source projects
- checking official docs, issues, changelogs, or workarounds for a bounded technical problem
- gathering UI references, component directions, rendering approaches, or style precedents

Every research run must be captured in artifacts instead of living only in chat.

At minimum, record:

- `query`
- `trigger_type`
- `why_now`
- `sources`
- `facts`
- `candidates`
- `recommendation`
- `impact_on_fb_or_mb`

Write those results into one or more of:

- `DECISIONS.md`
- the active `FB`
- the active `MB`
- a `RESEARCH_NOTE`

## External Tool Prompt And Intake Rule

When the experience layer is externally delivered, follow this order:

1. gather references or research when needed
2. discuss and resolve the key UI decisions that determine the outcome
3. let the user confirm the adopted references, final visual direction, design core, and major UI decisions
4. generate and persist the external-tool prompt in `experience_prompts/*.md`
5. include a copy-paste-ready final prompt inside that artifact
6. hand off through that prompt artifact and let the user confirm the returned external result
7. treat the approved result as `input_artifacts` for later `MB`s

UI-related research may propose references and recommendations, but it may not finalize visual direction.

Prompt requirements are context-relative rather than globally identical.

Do not generate an external-tool prompt for UI work until the user confirms:

- which references are adopted
- the final visual direction
- the design core
- the intended information density
- the layout direction
- the component style direction
- the color and typography direction
- the interaction and motion direction when relevant
- the responsive or platform priority
- the accessibility constraints
- the references or patterns that should be avoided

If the prompt is for a shared page family, the user and assistant must also align on:

- the `page_family_id`
- the shared shell scope
- what must be preserved across states or later `MB`s
- what variation is allowed
- what drift is explicitly forbidden
- which prior approved prompts or artifacts define the family contract

For Stitch handoff, prefer plain-language, screen-focused prompts. For a new family, establish the canonical shell first; for later work, refine the family screen by screen with tightly scoped edits instead of mixing many structural changes into one prompt.

Do not leave the final external-tool prompt only in chat. Persist it as an artifact so downstream `MB`s and reviews can read the same handoff contract, and include the full copy-paste-ready prompt body inside that artifact.

The default mode is manual handoff:

- the assistant prepares research and prompt inputs
- the user runs the external tool and approves the result
- the approved output returns as `input_artifacts`

If a future connected tool mode exists and the user grants permission, direct tool operation is allowed, but the approved output still remains an input artifact under `FB` and `MB` authority.

## Discovery Exit Rule

When a scene path includes `DISCOVERY`, it ends only when the protocol can write four lists:

1. confirmed facts
2. assumptions being taken
3. unresolved risks
4. intentionally out-of-scope items

If the scene is expected to produce a detailed `FB`, discovery must also cover the `8-element ontology frame`:

1. `Actor`
2. `Goal`
3. `Entity`
4. `Relation`
5. `State`
6. `Event`
7. `Rule`
8. `Evidence`

Each element must be marked as:

- `confirmed`
- `assumed`
- `risk`
- `out_of_scope`

Do not move into detailed `FB` writing or `MB` planning while ontology elements are still missing.

When the protocol starts `MB` planning, each planned `MB` must declare:

- which parent FB ontology elements are in scope
- which parent FB layers are in scope
- which ontology elements are deferred
- which layers are deferred

If the parent `FB` uses `external_ui_package` or `hybrid`, discovery must also identify:

- which states and branches the external package must cover
- which later `MB`s will consume those artifacts

## Role Handoff Rule

Scene paths define the sequence. Role handoffs define who owns the next step.

Every scene must:

- name the first active role
- define the handoff condition for the next role
- tell the user when a role change happens
- require user confirmation before entering a higher-cost or higher-risk work type

The Builder must not start from raw chat history.

The Builder starts only after reading:

- project constitution
- quality rulebook
- relevant feature or scope spec
- current function block
- current mission block
- required input artifacts when the current `FB` or `MB` depends on them
- current session state

If one of those is missing, the Builder must stop and request the missing artifact rather than infer it.

## Issue Routing Rule

Do not use vague fallback such as "go back one step".

When a problem is found, route it by ownership:

| Issue Type | Meaning | Route To |
| :--- | :--- | :--- |
| `spec_gap` | Goal, scope, acceptance, or contract is unclear or contradictory | `Spec Architect` |
| `implementation_bug` | Specs are clear, but implementation is wrong | `Builder` |
| `quality_evidence_gap` | Required checks, evidence, or quality report items are missing | `Builder` |
| `state_drift` | `SESSION_STATE`, active `FB/MB`, or repository references do not match reality | `Recovery Coordinator` |
| `environment_issue` | Toolchain, dependency, or runtime state blocks safe progress | `Recovery Coordinator` |
| `review_context_gap` | The current actor lacks required context to make a safe judgment | current scene lead role |

This rule applies in:

- `Preflight`
- scene work
- build
- review
- recovery

## AIPD Gate Outcome Rule

When an external execution runtime such as Symphony runs an `MB`, AIPD remains
the semantic authority.

The runtime may schedule work, hold locks, start Codex, retry, pause, release to
review, or close an `MB` only through a validated AIPD gate outcome.

The gate outcome must validate against `schemas/aipd-gate-outcome.schema.json`
before the runtime acts on it.

Two gates exist:

- `attempt_start`: decides whether Codex may start for one MB attempt
- `attempt_finish`: decides what happens after the attempt evidence is known

Fail-closed rule:

- missing gate outcome means Symphony must not start Codex
- malformed gate outcome means Symphony must not start Codex
- unknown `symphony_instruction.action` means Symphony must not start Codex
- `may_start_codex` is valid only when `action` is `dispatch_codex`
- process exit alone must not decide retry, review, recovery, or closure

If the gate outcome is invalid, ambiguous, or missing required evidence, route it
as `state_drift`, `quality_evidence_gap`, or `review_context_gap` according to
the concrete failure.

## Bootstrap Rule

If the user starts with only a repository and a scene, the agent must not ask for the SDD path again.

Instead, the agent must:

1. read the repository bootstrap files
2. run `Project Preflight`
3. map the requested scene path
4. activate the first appropriate role
5. tell the user what happens next

See `README.md` and `docs/06_session_bootstrap.md`.
