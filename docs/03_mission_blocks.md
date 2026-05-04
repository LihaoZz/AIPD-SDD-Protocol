# Function Blocks And Mission Blocks

## Why The Split Exists

Product work and code change work are not the same unit.

- a `Function Block` (`FB`) represents one product-facing delivery unit
- a `Mission Block` (`MB`) represents one bounded code change attempt under one active FB

This split keeps product context stable while letting implementation move in small, auditable steps.

## Function Blocks

An `FB` should answer:

- what user value is being delivered
- who the actor is
- what goal the actor is trying to complete
- what entities, relations, states, events, and rules define this function
- what evidence proves the function is real
- which engineering layers are affected
- what the acceptance definition is
- what is out of scope
- how the experience layer is delivered when it is affected

The `FB` main body should stay focused on:

- metadata
- product goal
- ontology frame
- impact map
- experience delivery
- scope
- acceptance
- mission plan

If the mode is `external_ui_package` or `hybrid`, the `FB` must also name:

- the required external input artifacts
- the Builder's allowed integration scope

Low-frequency details belong in `Optional Appendix`, not in the main body.

## Mission Blocks

An `MB` should answer:

- what exact code change is being attempted
- which FB it belongs to
- which slice of the parent FB acceptance it advances
- which ontology elements from the parent FB are in scope now
- which affected engineering layers from the parent FB are in scope now
- which ontology elements or layers are explicitly deferred
- which files may be modified
- which quality checks must pass
- what evidence is required
- what happened after execution

The `MB` main body should stay focused on:

- metadata
- parent FB alignment
- goal
- inputs
- boundaries
- quality plan
- evidence required
- result

Conditional rule:

- use `input_artifacts: none` when there is no upstream input dependency
- require `input_ready_check` only when real upstream inputs exist

## MB Concurrency Contract

Machine-runnable MBs may declare optional `concurrency` metadata in their machine
spec.

Supported fields:

- `concurrency_group`
- `exclusive_touch`
- `shared_read_artifacts`
- `shared_write_artifacts`
- `blocked_by_mbs`
- `can_run_parallel`
- `parallel_safe_reason`

Execution rule:

- the same `mb_id` must not run concurrently
- an unresolved `blocked_by_mbs` dependency blocks `attempt_start`
- an existing `concurrency_group` lock blocks `attempt_start`
- an overlapping `exclusive_touch` lock blocks `attempt_start`
- an overlapping `shared_write_artifacts` lock blocks `attempt_start`
- lock conflicts must produce a start gate outcome with `defer_retry`
- dependency conflicts must produce a start gate outcome with `release_and_wait_input`
- no lock or dependency conflict may start Codex or create an attempt directory
- acquired locks must be released after `attempt_finish` or after a pre-execution block

If `exclusive_touch` is omitted, the runner derives it from `allowed_touch`.

Low-frequency details belong in `Optional Appendix`, not in the main body.

## External UI Input Rule

Some experience work may be delivered outside the Builder workflow.

In that case:

- the `FB` still owns the product definition
- the external UI package becomes an input to later `MB`s
- a dependent `MB` becomes an integration slice, not a visual redesign task

Authority rule:

- `FB` defines what the function is
- `MB` defines what this bounded implementation slice must do
- the external UI package defines only how the approved experience should be presented
- the external UI package does not override `FB` ontology, `MB` scope, `acceptance_slice`, business rules, or quality gates

Dependency rule:

- only an `MB` that explicitly declares the UI package in `input_artifacts` should wait for that input
- other `MB`s must not be blocked just because the parent `FB` has an external UI package

The Builder should consume the approved input, then connect:

- states
- routing
- validation
- API calls
- the smallest necessary structural adjustments

## Research Support Rule

`Research` may support `FB` planning or active `MB` execution, but it does not become a new execution standard.

Trigger rule:

- `user_triggered` research may run immediately
- `system_triggered` research requires user approval before search begins

Scope rule:

- `Spec Architect` may use research for market scan, tool discovery, similar-product review, or external references during spec work
- `Builder` may use research only for the active `MB`, such as bounded technical problem solving, official-doc lookup, or mature implementation references
- research must not expand the active `MB` scope

Recording rule:

- reusable results should be written into `DECISIONS.md`, the active `FB`, the active `MB`, or a `RESEARCH_NOTE`
- do not leave adopted external facts only in chat history

## UI Reference And Prompt Rule

UI-related research may provide:

- style references
- mature patterns
- component directions
- rendering approaches
- similar-product visual examples

That research may support recommendation work, but it does not own the final design direction.

Before generating any external-tool UI prompt:

- the user must confirm which references are adopted
- the user must confirm the final visual direction
- the user must confirm the design core
- the user must confirm the major UI decisions that determine generation quality

After confirmation, the external-tool prompt should stay derived from:

- the parent `FB`
- the active or planned `MB`
- the approved visual direction
- the required states and branches
- the resolved layout, density, component, color, typography, interaction, motion, responsive, and accessibility decisions

If the prompt targets the same page family as earlier or later work, it must also define:

- the `page_family_id`
- the shared shell scope
- the family source refs that anchor the contract
- what must stay identical across states or sibling `MB`s
- what variation is allowed
- the forbidden drift list

Persist that prompt in `experience_prompts/*.md`, include the final copy-paste-ready prompt body in that artifact, and let any dependent integration `MB` point to it through `external_tool_prompt_ref`.

The returned output becomes an `input_artifact` for a later integration `MB`.

Dependent `MB`s in the same page family should reuse that handoff contract instead of silently inventing a new shell.

## Naming Rule

Use compact IDs that make the hierarchy obvious.

Examples:

- `fb2`
- `fb2-mb1`
- `fb2-mb2`
- `fb7-mb3`

## Quality Rule

An `MB` must not invent its own quality standards.

Every `MB` must:

- select checks from `QUALITY_RULEBOOK.md`
- declare which ontology elements and layers from the parent FB are in scope
- list required upstream inputs when they exist
- produce a quality report
- return enough evidence for the harness runtime to sync `SESSION_STATE.md`

If a needed quality rule does not exist yet, stop and request a rulebook update instead of improvising.

## Completion Rule

An `MB` is not complete when the Builder says "done".

It is complete only when all required evidence exists:

- code changes
- required quality checks and results
- required external inputs were consumed when relevant
- the quality report
- scope remained within the allowed boundary
- session state was synced by the runtime
