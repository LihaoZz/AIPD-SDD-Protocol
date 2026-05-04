# Quality Rulebook

## Purpose

Define the only approved quality standards for all mission blocks.

## Usage Rules

- `MB` must not invent quality standards on its own.
- Every `MB` must select checks from this rulebook.
- If a needed check does not exist here, the `MB` must stop and request a rulebook update instead of improvising.
- Waiving a check is allowed only under the waiver rule below.
- When a parent `FB` uses `external_ui_package` or `hybrid` and the `MB` touches the `experience` or `application` layer, include `experience_input_alignment`.

## Profiles

- `standard`:
  `scope_boundary`, `fb_ontology_alignment`, `layer_coverage_alignment`, `build`, `lint`, `typecheck`, `related_tests`, `artifact_sync`, `evidence`

- `strict`:
  all `standard` checks plus
  `contract`, `smoke`, `rollback_ready`, `human_signoff`

## Check Catalog

- `scope_boundary`:
  pass when all changed files stay inside `allowed_files`,
  no `forbidden_files` are touched,
  and `change_budget` is not exceeded.

- `fb_ontology_alignment`:
  pass when the MB does not contradict the parent FB's actor, goal, entity, relation, state, event, rule, or evidence model,
  or the parent FB is updated first through the correct role.
  Evaluate this against the MB's declared ontology slice, not against irrelevant FB elements.

- `layer_coverage_alignment`:
  pass when every layer marked as affected in the parent FB has matching implementation, artifact, or validation coverage for this MB,
  or the deferred layer is explicitly called out with a reason.
  Evaluate this against the MB's declared layer slice and explicit deferrals.

- `build`:
  pass when the required build command exits successfully.

- `lint`:
  pass when lint exits successfully,
  or no new lint errors are introduced under the approved rule.

- `typecheck`:
  pass when typecheck exits successfully.

- `related_tests`:
  pass when all tests listed in the MB pass.

- `artifact_sync`:
  pass when any behavior, API, data model, or scope change is reflected in the related artifacts.

- `evidence`:
  pass when the QR includes changed files, executed checks, results, open risks, and next action.

- `experience_input_alignment`:
  pass when the MB consumes the approved external UI package or design authority declared in the parent FB,
  and does not introduce an unapproved visual redesign.
  This check validates external experience input consumption only.
  It does not replace `scope_boundary`, `fb_ontology_alignment`, `layer_coverage_alignment`, or any other required check.
  Use this when the parent FB's `experience_delivery_mode` is `external_ui_package` or `hybrid`
  and the MB touches the `experience` or `application` layer.

- `contract`:
  pass when API or data interaction changes are verified against the contract.

- `smoke`:
  pass when one critical real user path is verified end-to-end.

- `rollback_ready`:
  pass when the rollback path is written and feasible.

- `human_signoff`:
  pass when a human explicitly reviews a high-risk MB.

## Waiver Rule

- A check may be waived only when the project truly does not have that mechanism yet.
- Every waived check must include:
  reason,
  replacement evidence,
  and whether follow-up work is needed.
- Invalid waiver reasons:
  "small change",
  "looks fine",
  "time is short",
  "model already checked it".

## High-Risk Trigger

Use `strict` by default when the MB touches:

- auth, permission, payment
- database, schema, migration
- public API
- core state management
- deployment, env, infra
- critical user path

---
