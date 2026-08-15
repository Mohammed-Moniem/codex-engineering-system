---
name: domain
description: Maintain precise domain vocabulary, durable business or system invariants, and selective architecture decisions. Use when terms, lifecycle rules, or cross-cutting constraints need a stable source of truth.
---

# Domain

Keep three artifact types distinct. Read [artifact-boundaries.md](references/artifact-boundaries.md) before creating a new convention.

## Glossary

Maintain `CONTEXT.md` or the repository's established glossary. Record canonical term, definition, aliases to avoid, and concrete examples. Keep implementation details out.

## Invariants

Maintain a separate invariant ledger for rules that must remain true across implementations. Give each invariant a stable ID, scope, rationale, enforcement points, evidence, and status.

## ADRs

Create an ADR only when the choice is meaningful, difficult to reverse, surprising without context, and involves a real trade-off. Link the decision it closes, alternatives considered, consequences, and supersession state. Do not use ADRs as meeting notes.

Inspect existing conventions before adding files. Update references rather than duplicating the same rule in several artifacts.
