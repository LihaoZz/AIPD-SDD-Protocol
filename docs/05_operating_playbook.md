# Operating Playbook

This document is an operational guide.

It is not the authority for lifecycle rules. For normative flow definitions, use `docs/00_lifecycle.md`.

## Project Preflight Checklist

At the start of a conversation:

1. identify the working path and requested scene
2. check foundational files and directories
3. check scene-specific requirements
4. return a short preflight summary
5. classify the state as `ready`, `bootstrap_required`, or `blocked`
6. if needed, initialize only safe foundational files
7. if blocked, route the problem by ownership and ask only for the minimum missing context

## Build An FB In This Order

Before detailed FB planning, cover these two views:

- `8-element ontology frame`: what the function is
- `8-layer impact map`: where the function lands in engineering

Use them in this order:

1. ontology first
2. impact map second
3. acceptance third
4. MB slicing last

If the ontology is weak, do not hide the gap inside implementation planning.

## Experience Delivery In Practice

When the `experience` layer is affected, the `Spec Architect` must decide `experience_delivery_mode` inside `SPEC` or `FB_DETAILING`.

Allowed values:

- `builder_generated`
- `external_ui_package`
- `hybrid`
- `not_applicable`

Practical rule:

- if the Builder owns the experience layer, continue normal MB planning
- if the experience layer is externally delivered, capture the input artifacts in the parent `FB`
- dependent `MB`s become integration slices, not visual redesign tasks

For external UI delivery, record at minimum:

- which states and branches the package must cover
- which artifact or code bundle is the approved input
- what part remains Builder-owned
- which later `MB`s are blocked until the input is ready

## Research In Practice

Use research sparingly and only when it materially improves a current decision.

Two trigger types exist:

- `user_triggered`: the user explicitly asks for search or lookup work
- `system_triggered`: the active role sees a material gap that external facts can resolve

Practical rule:

- `user_triggered` research may start immediately
- `system_triggered` research must first explain why the search is needed, then wait for user approval

For `Spec Architect`, common uses are:

- simple market scan
- similar-product review
- searching for existing tools, services, or open-source projects
- gathering UI references before direction is chosen

For `Builder`, common uses are:

- official documentation lookup
- issue or changelog lookup
- bounded technical problem solving
- mature implementation references for the active `MB`

Always write adopted results into artifacts instead of relying on chat memory alone.

## UI Prompt Generation In Practice

When UI is externally delivered, use this order:

1. gather references or research
2. recommend options
3. discuss the concrete UI decisions that will materially affect generation quality
4. let the user confirm the adopted visual direction, design core, and major UI decisions
5. generate and persist the external-tool prompt in `experience_prompts/*.md`
6. include a copy-paste-ready final prompt inside that artifact
7. let the user confirm the returned output
8. pass the approved result to a later integration `MB`

The assistant may recommend styles or tools, but the user decides the final UI direction.

The discussion before prompt generation should normally cover:

- information density
- layout direction
- component style direction
- color direction
- typography direction
- interaction direction
- motion direction when relevant
- responsive priority
- accessibility rules
- references to adopt
- references to avoid

If some decisions remain intentionally open, record the default explicitly before prompt generation instead of leaving them implicit.

When a later `MB` depends on the handoff contract, point it to that artifact through `external_tool_prompt_ref` instead of relying on chat memory.

## Stitch Prompt Strategy In Practice

When the target tool is Stitch, use task-relative prompt strategy instead of one universal prompt shape.

Follow the guidance from the Stitch prompt guide:

- use plain language
- keep prompts screen-focused
- for complex products, start high-level and then refine screen by screen
- prefer one or two tightly scoped changes per edit pass instead of combining many structural changes

Choose one prompt goal type before writing the final prompt:

- `canonical_shell`: first prompt for a new page family or a deliberate family reset
- `state_variant`: same page family, same shell, different state coverage
- `family_extension`: same page family, same shell, bounded new region or capability
- `independent_screen`: unrelated screen with no shared shell contract

Then choose the tool guidance profile:

- `stitch_first_pass`: first high-detail Stitch generation for one screen or page family shell
- `stitch_iterative_refine`: later Stitch edits with one or two tightly scoped changes
- `figma_structured_handoff`: richer multi-state handoff for Figma
- `general_structured_handoff`: fallback for other tools

In practice, combine the two axes:

- new page family in Stitch: `canonical_shell` + `stitch_first_pass`
- more states in the same Stitch family: `state_variant` + `stitch_iterative_refine`
- bounded new panel or module in the same Stitch family: `family_extension` + `stitch_iterative_refine`
- standalone screen in Stitch: `independent_screen` + `stitch_first_pass`
- Figma handoff for a bounded page family slice: keep the right `prompt_goal_type`, then usually pair it with `figma_structured_handoff`

When the work stays inside the same page family, make the family contract explicit:

- name the `page_family_id`
- state which shell elements must stay fixed, such as sidebar, top nav, frame, grid, layout rhythm, and component language
- state which regions may vary
- state which drift is forbidden
- point to prior approved family artifacts through `family_source_refs`

Do not assume Stitch will preserve the shell on its own. If shell consistency matters, say so directly in the prompt.

## Scene Heuristics

### `greenfield`

Focus on:

- business goal
- user value
- version-one boundary
- first quality system
- first FB plan

Avoid:

- early coding
- premature stack arguments

### `expansion`

Focus on:

- what existing assumption may break
- what regressions are likely
- what new FB must be written before coding

Avoid:

- treating a delta feature like a full restart

### `continue`

Focus on:

- active FB
- active MB
- last successful checkpoint
- the next single safe action

Avoid:

- restarting from zero
- switching tasks without recording state

### `review`

Focus on:

- artifact alignment
- scope compliance
- evidence completeness
- ownership classification for every finding

Avoid:

- patching code during review unless the user changes the task

### `recovery`

Focus on:

- last known good checkpoint
- failure classification
- smallest safe next move

Avoid:

- continuing implementation by instinct

## Harness Loop In Practice

Use the harness when one active `MB` should run through a machine-controlled Builder loop.

Operational order:

1. run `preflight.py --level session` when entering or resuming a project
2. run `preflight.py --level mb` before invoking the active `MB`
3. read `<PROJECT_ROOT>/missions/<mb_id>.md` and `<PROJECT_ROOT>/missions/<mb_id>.machine.json`
4. require one valid protocol-level execution policy from `config/execution_policy.json`
5. let `mb_runner.py` assemble the Builder prompt and invoke Codex CLI with an explicit `--sandbox workspace-write` boundary
6. run mandatory hook guards before and after Codex execution
7. compare real workspace changes through `scope_guard.py`
8. if scope fails, stop and route to recovery
9. if scope passes, run `verifier.py` against inline acceptance plus any referenced eval assets
10. write runtime state and sync `SESSION_STATE.md`
11. if verification fails and retry is still allowed, inject `last_verification_digest`, `last_failure_reason`, `retry_count`, and relevant memory context into the next prompt
12. if verification passes, follow the `autonomy_level`: hand off to review for `L1/L2`, or close automatically for `L3`; if retry limit is reached, route to recovery

Do not treat `last_verification_digest` as a new truth artifact.

It is a runner-generated retry summary derived from the latest `verification_report.json`.

`scope_guard.py` in this wave is a repo-local file-boundary auditor.

It protects runtime-owned paths such as `runtime/state/`, `runtime/memory/`, `runtime/gate_outcomes/`, and `runtime/locks/`, and it may ignore artifacts created inside the current attempt directory under `runtime/attempts/<mb_id>/<attempt_id>/`.

It does not yet provide full-system sandbox guarantees, repo-external write detection, or per-command interception for every model-generated shell or network action.

## Local Validation

Run the local guard script before claiming the repository is ready for handoff.

Commands:

- `python3 scripts/sdd_guard.py check-protocol`
- `python3 scripts/sdd_guard.py check-preflight /path/to/project <scene>`
- `python3 scripts/sdd_guard.py check-project /path/to/project`
- `python3 scripts/sdd_guard.py check-function /path/to/workspace/function_blocks/<function-file>.md`
- `python3 scripts/sdd_guard.py check-mission /path/to/workspace/missions/<mission-file>.md`
- `python3 scripts/sdd_guard.py check-quality-report /path/to/workspace/reviews/<quality-report>.json`
- `python3 scripts/sdd_guard.py check-gate-outcome /path/to/gate-outcome.json`
