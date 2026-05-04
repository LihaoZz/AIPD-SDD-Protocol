# Mission Block

## Metadata

- `mb_id`:
- `parent_fb_id`:
- `status`:
- `change_type`:

## Parent FB Alignment

- `parent_fb_ontology_ref`:
- `acceptance_slice`:
- `ontology_elements_in_scope`:
- `affected_layers_in_scope`:
- `deferred_ontology_elements`:
- `deferred_layers`:

## Goal

- `goal`:

## Inputs

- `input_artifacts`:
- `input_ready_check`:

## Boundaries

- `allowed_files`:

## Quality Plan

- `quality_profile`:
- `selected_quality_checks`:
- `required_commands`:
- `pass_condition`:

## Evidence Required

- `required_test_evidence`:
- `required_artifact_updates`:
- `required_quality_report`:

## Result

- `outcome`:
- `next_action`:

## Machine Spec

- `machine_spec_ref`:
- `machine_spec_eval_refs`: none
- `machine_spec_memory_policy`: default
- `machine_spec_autonomy_level`: L2_auto_with_review

## Optional Appendix

- `hypothesis`:
- `alignment_notes`:
- `research_inputs`:
- `external_tool_prompt_ref`:
- `forbidden_files`:
- `change_budget`:
- `risk_level`:
- `user_visible_before`:
- `checks_before`:
- `known_problem_before`:
- `artifact_state_before`:
- `waived_checks`:
- `regression_rule`:
- `checkpoint`:
- `safe_revert_path`:
- `changed_files`:

## Usage Rules

- This `MB` inherits from one parent `FB`.
- `ontology_elements_in_scope`, `affected_layers_in_scope`, `deferred_ontology_elements`, and `deferred_layers` must make the slice explicit.
- Use `input_artifacts: none` when there is no upstream dependency.
- `input_ready_check` is required only when `input_artifacts` is not `none`.
- `input_artifacts` records execution dependencies only. It does not override the parent `FB`, the active `MB`, business rules, acceptance, or quality gates.
- If the parent `FB` uses `external_ui_package` or `hybrid`, this `MB` is an integration slice, not a visual redesign task.
- `selected_quality_checks` must be chosen from `QUALITY_RULEBOOK.md`.
- This `MB` is complete only when its required quality report exists and all required checks are evaluated.
- `required_artifact_updates` is only for source-of-truth artifacts that the Builder must update directly.
- Do not list `SESSION_STATE.md` in `required_artifact_updates` for a runnable `MB`; the harness runtime syncs session state automatically.
- Each runnable `MB` must have one machine sidecar with the same base id at `missions/<mb_id>.machine.json`.
- `machine_spec_ref` should point to that sidecar using one relative path, or `none` only when the mission is explicitly non-runnable.
- The machine sidecar should declare reusable `eval_refs`, `memory_policy`, and `autonomy_level` when the harness loop depends on them.
- `Optional Appendix` may be omitted entirely when it adds no useful clarity.
- Use `research_inputs` and `external_tool_prompt_ref` only when the active `MB` depends on research or an external-tool prompt artifact.
- `research_inputs` should use comma-separated relative paths under `research/`, or `none`.
- `external_tool_prompt_ref` should use one relative path under `experience_prompts/`, or `none`.

---
