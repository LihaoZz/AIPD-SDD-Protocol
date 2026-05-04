# Preflight Result

## Metadata

- `scene`:
- `project_root`:
- `preflight_result`:
- `autonomy_decision`:
- `can_enter_scene`:

## Checked Items

- `checked_files`:
- `checked_directories`:
- `state_references_checked`:

## Missing Items

- `missing_foundations`:
- `missing_scene_requirements`:
- `stale_or_inconsistent_items`:

## Automatic Actions

- `auto_actions`:
- `bootstrap_scope`:

## Blocking Items

- `blocking_items`:
- `minimal_user_input_needed`:

## Conclusion

- `recommended_next_step`:
- `scene_entry_decision`:

## Usage Rules

- Every new conversation must produce a preflight result before entering the requested scene.
- Allowed `preflight_result` values are:
  `ready`,
  `bootstrap_required`,
  `blocked`.
- `can_enter_scene` must be `true` only when the system can safely continue into the requested scene.
- If the result is `bootstrap_required`, the system should initialize safe foundational files before entering the scene.
- If the result is `blocked`, the system should ask only for the minimum missing context.

---
