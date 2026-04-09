# Mission Block

## Metadata

- `mb_id`: fb1-mb1
- `parent_fb_id`: fb1
- `status`: ready
- `change_type`: direct_update

## Parent FB Alignment

- `parent_fb_ontology_ref`: fb1
- `acceptance_slice`: write PASS_ONE into src/app.py
- `ontology_elements_in_scope`: evidence
- `affected_layers_in_scope`: application, quality
- `deferred_ontology_elements`: none
- `deferred_layers`: none

## Goal

- `goal`: Make src/app.py contain PASS_ONE

## Inputs

- `input_artifacts`: none
- `input_ready_check`: none

## Boundaries

- `allowed_files`: src/app.py

## Quality Plan

- `quality_profile`: standard
- `selected_quality_checks`: unit_command, no_out_of_scope_changes
- `required_commands`: inline command
- `pass_condition`: PASS_ONE exists in src/app.py

## Evidence Required

- `required_test_evidence`: verification report
- `required_artifact_updates`: none
- `required_quality_report`: none

## Result

- `outcome`: pending
- `next_action`: run

## Machine Spec

- `machine_spec_ref`: missions/fb1-mb1.machine.json
