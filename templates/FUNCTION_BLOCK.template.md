# Function Block

## Metadata

- `fb_id`:
- `title`:
- `status`:

## Product Goal

- `business_objective`:
- `user_value`:
- `success_definition`:

## Ontology Frame

- `actor_status`:
- `actor_description`:
- `goal_status`:
- `goal_description`:
- `entity_status`:
- `entity_description`:
- `relation_status`:
- `relation_description`:
- `state_status`:
- `state_description`:
- `event_status`:
- `event_description`:
- `rule_status`:
- `rule_description`:
- `evidence_status`:
- `evidence_description`:

## Impact Map

- `business_layer`:
- `domain_layer`:
- `flow_layer`:
- `experience_layer`:
- `application_layer`:
- `service_layer`:
- `data_layer`:
- `quality_layer`:

## Experience Delivery

- `experience_delivery_mode`:
- `experience_input_artifacts`:
- `experience_builder_scope`:

## Scope

- `in_scope`:
- `out_of_scope`:

## Acceptance

- `acceptance_criteria`:

## Mission Plan

- `planned_mbs`:
- `next_recommended_mb`:

## Optional Appendix

- `dependencies`:
- `related_artifacts`:
- `overall_risk`:
- `special_quality_concerns`:
- `release_blockers`:
- `completed_mbs`:
- `failed_mbs`:
- `open_questions`:
- `research_needed`:
- `research_questions`:
- `experience_prompt_needed`:

## Usage Rules

- One `FB` may contain multiple `MB`s.
- `FB` defines the product goal and final acceptance.
- Do not enter detailed planning until all 8 ontology elements are covered.
- Each ontology status must be one of: `confirmed`, `assumed`, `risk`, or `out_of_scope`.
- Each `*_layer` field should use: `affected=...; why=...; artifact_updates=...; validation_needed=...`.
- `experience_delivery_mode` must be one of: `builder_generated`, `external_ui_package`, `hybrid`, or `not_applicable`.
- `experience_input_artifacts` and `experience_builder_scope` are required only when the mode is `external_ui_package` or `hybrid`.
- `Optional Appendix` may be omitted entirely when it adds no useful clarity.
- Use `research_needed`, `research_questions`, and `experience_prompt_needed` only when research or external experience prompt preparation is relevant.

---
