# Experience Prompt

## Metadata

- `prompt_id`:
- `parent_fb_id`:
- `related_mb_ids`:
- `page_family_id`:
- `prompt_goal_type`:
- `consistency_mode`:
- `family_source_refs`:
- `tool_guidance_profile`:
- `target_tool`:
- `status`:
- `source_artifacts`:

## Confirmed Direction

- `adopted_reference_refs`:
- `visual_direction`:
- `design_core`:
- `information_density`:
- `layout_direction`:
- `component_style_direction`:
- `color_direction`:
- `typography_direction`:
- `interaction_direction`:
- `motion_direction`:
- `responsive_priority`:
- `accessibility_rules`:
- `references_to_avoid`:

## Family Consistency Contract

- `shared_shell_scope`:
- `must_preserve`:
- `allowed_variation`:
- `forbidden_drift`:
- `component_contract_expectations`:

## Scope

- `page_or_component_goal`:
- `states_and_branches`:
- `required_flows`:

## Build Instructions

- `style_direction`:
- `must_do`:
- `must_not_do`:

## Expected Return

- `expected_return_artifacts`:
- `downstream_intake_notes`:

## Prompt Strategy

- `prompt_requirements`:
- `tool_specific_notes`:

## Copy-Paste Prompt

Paste the final tool-ready prompt here. This section should be detailed enough that the external tool can generate the intended UI in one pass.

```text
[Write the final copy-paste prompt here. Include the page or component goal, all required states and branches, confirmed visual direction, layout and component decisions, constraints, and expected return artifacts.]
```

## Usage Rules

- Create this artifact only after the user confirms adopted references, final visual direction, design core, and the major UI decisions that shape the output.
- `target_tool` must be one of: `figma`, `stitch`, or `other`.
- `status` must be one of: `draft`, `approved_for_handoff`, or `superseded`.
- `prompt_goal_type` must be one of: `canonical_shell`, `state_variant`, `family_extension`, or `independent_screen`.
- `consistency_mode` must be one of: `same_family_strict`, `same_family_adaptive`, or `not_applicable`.
- `tool_guidance_profile` must be one of: `stitch_first_pass`, `stitch_iterative_refine`, `figma_structured_handoff`, or `general_structured_handoff`.
- `source_artifacts` should list comma-separated relative paths to governing `FB`, `MB`, research notes, or other source-of-truth artifacts.
- `adopted_reference_refs` should list comma-separated relative paths to approved local references, or `none`.
- `family_source_refs` should list comma-separated relative paths to prior approved prompts or other family-governing artifacts, or `none`.
- Use the structured fields to record confirmed design decisions; use `Copy-Paste Prompt` to store the final detailed prompt text that the user can send directly to the external tool.
- Prompt requirements are context-relative. Do not force the same prompt shape on every task.
- If the prompt targets a shared page family, set `page_family_id` and make the shared shell contract explicit through `shared_shell_scope`, `must_preserve`, `allowed_variation`, and `forbidden_drift`.
- Use `canonical_shell` for the first prompt that defines a page family's shell, `state_variant` for the same shell under different states, `family_extension` for bounded additions inside the same family, and `independent_screen` for unrelated screens.
- `same_family_strict` means the shell, component language, and token rhythm should remain fixed except for the explicitly allowed variation.
- `same_family_adaptive` means the family shell remains recognizable, but bounded regions may change more visibly when the prompt explicitly allows it.
- If `prompt_goal_type` is `independent_screen`, set `page_family_id` to `not_applicable`, `consistency_mode` to `not_applicable`, and `family_source_refs` to `none`.
- `stitch_first_pass` is for the first high-detail screen prompt in Stitch; `stitch_iterative_refine` is for later screen-focused edits with one or two scoped changes; `figma_structured_handoff` is for richer multi-state handoff to Figma; `general_structured_handoff` is the fallback for other tools.
- When `target_tool` is `stitch`, prefer plain-language, screen-focused prompts. For complex work, establish the family shell first, then refine screen by screen with tightly scoped edits.
- This artifact guides external-tool handoff only. It does not override the active `FB`, active `MB`, business rules, acceptance, or quality gates.

---
