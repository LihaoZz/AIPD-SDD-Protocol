# Research Note

## Metadata

- `research_id`:
- `trigger_type`:
- `owner_role`:
- `date`:

## Query

- `query`:
- `why_now`:

## Findings

- `sources`:
- `facts`:

## Candidate Options

- `candidates`:
- `recommendation`:

## Impact And Adoption

- `impact_on_fb_or_mb`:
- `adopted_decision_ref`:
- `deferred_questions`:

## Approval

- `user_approval_required`:
- `user_approval_status`:

## Usage Rules

- Use this artifact when research produces reusable facts, options, or recommendations.
- `trigger_type` must be `user_triggered` or `system_triggered`.
- `user_triggered` research should use `user_approval_required: no` and `user_approval_status: not_required`.
- If `trigger_type` is `system_triggered`, set `user_approval_required` to `yes` before search and record `user_approval_status: approved`.
- If the note affects active work, write the adopted result into `DECISIONS`, active `FB`, or active `MB`.
- UI-related research may propose references, but final visual direction must be user-confirmed before external-tool prompt generation.

---
