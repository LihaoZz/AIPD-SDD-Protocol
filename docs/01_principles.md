# Principles And Writing Style

## Core Principles

1. Less is more. Always keep it simple.
2. Do not code while the problem is still vague.
3. Do not let the coding agent invent architecture without approval.
4. Do not treat conversation memory as a reliable source of truth.
5. Do not accept "done" without evidence.
6. Do not expand scope inside implementation tasks.
7. Do not let the Builder improvise visual design when the experience layer is assigned to an external UI tool or authority.

Simplicity means:

- prefer the smallest useful scope
- prefer the fewest dependencies
- prefer the smallest safe change surface
- prefer the clearest design that can be explained and verified

---

## Plain Writing Rule

Use plain language first.

For models, clarity comes mainly from:

- stable structure
- explicit rules
- short sections
- consistent labels
- examples and templates

It does not come mainly from:

- emoji
- decorative emphasis
- many repeated punctuation marks
- aggressive formatting noise

Emoji and visual emphasis can help a human skim a document, but they rarely improve model compliance in a meaningful way. In long prompts they often become noise.

Recommended style:

- use short section titles
- use numbered stages and named artifacts
- use tables only when comparing options or responsibilities
- use bold sparingly for one term, not whole paragraphs
- keep one rule per bullet when possible

Avoid:

- stacked emoji
- repeated `###`, `!!!`, or similar visual shouting
- mixing policy, examples, and exceptions in the same paragraph

---

## Role Model

This protocol uses five roles.

| Role | Owner | Responsibility | Cannot Do |
| :--- | :--- | :--- | :--- |
| User | Human | Define business goal, priorities, acceptance, and tradeoffs | Invent technical design under pressure |
| Spec Architect | Planning model | Translate business intent into specs, decisions, function blocks, and mission boundaries | Write production code without changing role |
| Builder | Coding model | Implement one bounded mission block under the active function block | Expand scope or rewrite architecture on its own |
| Reviewer | Review model or review pass | Check evidence, risks, quality gates, and contract alignment | Trust the builder's claims without verification |
| Recovery Coordinator | Recovery model or recovery pass | Classify broken state, repair session truth, and choose the smallest safe recovery move | Continue implementation by instinct or hide state drift |

Scene paths define work sequence. Roles define responsibility boundaries.

No scene may collapse role separation.

When a problem is discovered, route it by ownership:

- `spec_gap` -> `Spec Architect`
- `implementation_bug` -> `Builder`
- `quality_evidence_gap` -> `Builder`
- `state_drift` -> `Recovery Coordinator`
- `environment_issue` -> `Recovery Coordinator`
- `review_context_gap` -> current scene lead role

When the experience layer is externally delivered, role separation also means:

- the user or external tool owns the visual authority
- the `Spec Architect` records that delivery decision in the FB
- the `Builder` integrates the approved UI package instead of inventing a new one
- the `Reviewer` verifies integration and alignment instead of silently accepting visual drift

---

## Ontology Skeleton vs Engineering Map

Do not mix these two ideas.

The `8-element ontology frame` describes what one function is:

- `Actor`
- `Goal`
- `Entity`
- `Relation`
- `State`
- `Event`
- `Rule`
- `Evidence`

The `8-layer impact map` describes where that function lands in engineering:

- business
- domain
- flow
- experience
- application
- service
- data
- quality

Think of it like this:

- ontology frame = meaning
- impact map = implementation surface

---

## Experience Delivery Rule

If the `experience` layer is affected, the protocol must also decide how that layer is delivered.

Use `experience_delivery_mode` in the parent `FB`:

- `builder_generated`: the Builder may implement the experience layer directly
- `external_ui_package`: the visual UI is produced outside the Builder workflow and then handed back as an input artifact
- `hybrid`: the base visual UI comes from an external authority, but the Builder may complete a small approved portion of the experience work
- `not_applicable`: the current function does not change the experience layer

When the mode is `external_ui_package` or `hybrid`:

- the `FB` must name the affected surfaces and expected external inputs
- any `MB` that depends on those inputs must list them explicitly
- the `Builder` may integrate states, routing, API calls, and validation logic
- the `Builder` must not improvise a new visual language, layout direction, or component styling
- the `Reviewer` should verify that the approved external UI input was consumed correctly

---

## Non-Technical User Rule

The user is not required to provide technical solutions.

The Spec Architect must:

- ask business questions in plain Chinese
- convert business answers into technical constraints
- present no more than a few decision options at once
- explain tradeoffs in product terms, not framework jargon
- make a reasonable default recommendation when the user lacks the technical basis to choose

The user must still decide:

- what problem matters most
- what "good enough" means
- which tradeoff is acceptable
- whether to proceed, pause, or cut scope

---
