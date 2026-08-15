---
name: spec
description: Collapse resolved product and engineering decisions into an implementation-ready specification. Use after planning decisions are settled; route back to grill or Wayfinder instead of inventing any blocking decision.
---

# Spec

Synthesize decisions; do not reopen them without evidence and do not fill gaps by guessing.

1. Gather the active plan or Wayfinder map, accepted decisions, ADRs, research, prototypes, domain glossary, and invariants.
2. Build a trace table from each material requirement to its source decision and evidence.
3. Detect contradictions, superseded inputs, and missing blocking decisions. If a missing choice changes behavior or architecture, stop and route it to `grill` or `wayfinder`.
4. Write the specification using [template.md](references/template.md). Mark non-blocking unknowns explicitly with owner and resolution point.
5. Test the document mentally against primary journeys, failure paths, migration, rollback, and observability.

The finished spec must cover problem/destination, actors, journeys, functional requirements, business rules, domain, architecture, data, APIs, integrations, AI requirements when applicable, non-functional requirements, security, testing, observability, migration/rollout, feature flags, assumptions, risks, and out of scope.

Exit only when implementation can proceed without inventing a material product or architecture decision.
