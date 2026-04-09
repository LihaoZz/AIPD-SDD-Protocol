# Mission Block

## Metadata

- `mb_id`: fb1-mb7
- `parent_fb_id`: fb1
- `status`: ready
- `change_type`: human_approval_gate

## Parent FB Alignment

- `parent_fb_ontology_ref`: fb1
- `acceptance_slice`: require explicit approval before executing PASS_SEVEN
- `ontology_elements_in_scope`: evidence
- `affected_layers_in_scope`: application, quality
- `deferred_ontology_elements`: none
- `deferred_layers`: none

## Goal

- `goal`: Require human approval before execution

## Inputs

- `input_artifacts`: none
- `input_ready_check`: none

## Boundaries

- `allowed_files`: src/app.py

## Quality Plan

- `quality_profile`: standard
- `selected_quality_checks`: unit_command, no_out_of_scope_changes
- `required_commands`: inline command
- `pass_condition`: PASS_SEVEN exists in src/app.py

## Evidence Required

- `required_test_evidence`: verification report
- `required_artifact_updates`: none
- `required_quality_report`: none

## Result

- `outcome`: pending
- `next_action`: await_human_approval

## Machine Spec

- `machine_spec_ref`: missions/fb1-mb7.machine.json
