# Mission Block

## Metadata

- `mb_id`: fb1-mb8
- `parent_fb_id`: fb1
- `status`: ready
- `change_type`: direct_update

## Parent FB Alignment

- `parent_fb_ontology_ref`: fb1
- `acceptance_slice`: protected runtime paths must trigger recovery routing
- `ontology_elements_in_scope`: evidence
- `affected_layers_in_scope`: application, quality
- `deferred_ontology_elements`: none
- `deferred_layers`: none

## Goal

- `goal`: Trigger protected runtime scope handling

## Inputs

- `input_artifacts`: none
- `input_ready_check`: none

## Boundaries

- `allowed_files`: src/app.py

## Quality Plan

- `quality_profile`: standard
- `selected_quality_checks`: no_out_of_scope_changes
- `required_commands`: none
- `pass_condition`: runtime protection blocks the attempt

## Evidence Required

- `required_test_evidence`: scope guard report
- `required_artifact_updates`: none
- `required_quality_report`: none

## Result

- `outcome`: pending
- `next_action`: run

## Machine Spec

- `machine_spec_ref`: missions/fb1-mb8.machine.json
