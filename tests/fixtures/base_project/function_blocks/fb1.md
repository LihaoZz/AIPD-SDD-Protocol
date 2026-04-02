# Function Block

## Metadata

- `fb_id`: fb1
- `title`: Harness Fixture
- `status`: active

## Product Goal

- Validate the harness loop against a predictable file change

## Ontology Frame

- `actor_status`: confirmed
- `actor_description`: test harness
- `goal_status`: confirmed
- `goal_description`: execute bounded MBs
- `entity_status`: confirmed
- `entity_description`: src/app.py
- `relation_status`: confirmed
- `relation_description`: MB updates one file under one FB
- `state_status`: confirmed
- `state_description`: pending or passed
- `event_status`: confirmed
- `event_description`: runner attempt
- `rule_status`: confirmed
- `rule_description`: allowed touch and verification rules
- `evidence_status`: confirmed
- `evidence_description`: verification report

## Impact Map

- `business_layer`: no
- `domain_layer`: no
- `flow_layer`: yes
- `experience_layer`: no
- `application_layer`: yes
- `service_layer`: no
- `data_layer`: no
- `quality_layer`: yes

## Experience Delivery

- `experience_delivery_mode`: not_applicable

## Scope

- `in_scope`: harness fixture execution
- `out_of_scope`: external UI

## Acceptance

- `acceptance_criteria`: machine verification passes or routes correctly

## Mission Plan

- `planned_mbs`: fb1-mb1, fb1-mb2, fb1-mb3, fb1-mb4
- `next_recommended_mb`: fb1-mb1

## Usage Rules

- Fixture only
