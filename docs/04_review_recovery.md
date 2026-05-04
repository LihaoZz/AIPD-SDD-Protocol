# Review And Recovery

## Review Standard

Reviews must be evidence-based.

The reviewer should verify:

- function block alignment
- FB ontology frame alignment
- FB impact map coverage alignment
- active MB inheritance-slice compliance
- mission block scope compliance
- required research artifacts when the active `MB` adopts external facts
- required external prompt artifacts when the active `MB` depends on handoff context
- external UI package alignment when the parent FB does not use Builder-owned experience delivery
- required quality checks
- data or API contract drift
- hidden risk introduced by the task

The reviewer must classify every finding by ownership instead of using vague fallback.

---

## Issue Routing By Ownership

Use the same routing rule in review, recovery, builder execution, and preflight.

| Issue Type | Meaning | Route To |
| :--- | :--- | :--- |
| `spec_gap` | Goal, scope, acceptance, or contract is unclear, missing, or contradictory | `Spec Architect` |
| `implementation_bug` | The written artifacts are clear, but the code does not match them | `Builder` |
| `quality_evidence_gap` | Required checks, evidence, or report fields are missing | `Builder` |
| `state_drift` | `SESSION_STATE`, active `FB/MB`, or file references do not match reality | `Recovery Coordinator` |
| `environment_issue` | Environment, dependency, or runtime state blocks safe progress | `Recovery Coordinator` |
| `review_context_gap` | The current actor lacks enough context to safely decide | current scene lead role |

The `Reviewer` does not fix problems.

The `Reviewer` must:

1. classify the issue
2. point to the correct owner
3. require the next action in the quality report

---

## Quality Report Output

Use a structured format so the result can later be automated.

Store review files under `<PROJECT_ROOT>/reviews/` and validate them against `schemas/quality-report.schema.json`.

```json
{
  "fb_id": "fb2",
  "mb_id": "fb2-mb3",
  "quality_profile": "standard",
  "result": "pass",
  "risk_level": "low",
  "baseline_summary": "Short machine-readable baseline summary",
  "changed_files": ["src/example.ts"],
  "scope_respected": true,
  "checks": {
    "scope_boundary": {
      "required": true,
      "status": "pass",
      "evidence": "changed files remained in scope",
      "note": ""
    },
    "fb_ontology_alignment": {
      "required": true,
      "status": "pass",
      "evidence": "implementation still matched the parent FB ontology frame",
      "note": ""
    },
    "layer_coverage_alignment": {
      "required": true,
      "status": "pass",
      "evidence": "affected layers in the FB were covered or explicitly deferred",
      "note": ""
    },
    "experience_input_alignment": {
      "required": false,
      "status": "not_applicable",
      "evidence": "The MB did not depend on an external UI package, or the approved package was consumed without visual drift",
      "note": ""
    }
  },
  "regression_found": false,
  "open_risks": [],
  "lessons": [],
  "required_actions": [],
  "manual_review_required": false
}
```

If the review fails, `required_actions` should make the ownership explicit.

Examples:

- `Spec Architect: clarify acceptance for fb2 before the next MB`
- `Builder: add missing regression coverage for fb2-mb3`
- `Recovery Coordinator: repair session state reference to active_mission_block`

---

## Recovery Rule

When the project enters a confused or broken state, do not continue coding by instinct.

Run recovery in this order:

1. identify the active function block and mission block
2. identify the last known good checkpoint
3. classify the failure:
   `spec_gap`, `implementation_bug`, `quality_evidence_gap`, `environment_issue`, `state_drift`, or `review_context_gap`
4. route the failure to the owning role
5. choose the smallest safe move
6. update `SESSION_STATE.md` before any new implementation begins

If the failure is caused by a missing external UI package, do not let the Builder compensate by inventing a replacement design. Record the missing input, route the handoff correctly, and keep the next action explicit.

If the failure is caused by a missing research note or missing experience prompt artifact that the active `MB` depends on, route it as missing execution context instead of letting the Builder infer the missing contract from chat history.

---

## Three-Strike Rule

If the same implementation attempt fails repeatedly, stop escalation by habit.

Suggested policy:

- after 2 similar failures, require a written hypothesis
- after 3 similar failures, stop implementation and return to `DISCOVERY`, `SPEC`, or `RECOVERY`

The point is not the number. The point is to stop blind retries.

---
