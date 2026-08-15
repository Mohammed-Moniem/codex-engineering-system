# Wayfinder map schema

## Effort layout

```text
.codex/wayfinder/
├── ACTIVE
└── efforts/
    └── <slug>/
        ├── MAP.md
        ├── ASSUMPTIONS.md
        ├── INVARIANTS.md
        ├── decisions/
        │   └── D-001.md
        └── evidence/
            └── E-001.md
```

`ACTIVE` contains exactly one repository-relative path such as `.codex/wayfinder/efforts/offline-sync/MAP.md`.

## MAP.md

Required sections:

1. Destination
2. Success conditions
3. Constraints
4. Explicit out of scope
5. Frontier
6. Fog / Not Yet Specified
7. Decision graph
8. Recent invalidations
9. Exit gate

Keep MAP.md as a low-resolution operational view. Decision and evidence detail has one canonical child file.

## Decision ticket

| Field | Values or meaning |
| --- | --- |
| ID | Stable `D-NNN` |
| Question | One decision that can be resolved |
| Type | `RESEARCH`, `ANALYSIS`, `GRILL`, `PROTOTYPE`, `EXPERIMENT`, `EXTERNAL-INPUT`, `TASK` |
| Owner | `AFK`, `HITL`, `HYBRID` |
| Status | `OPEN`, `CLAIMED`, `BLOCKED`, `RESOLVED`, `REOPENED`, `SUPERSEDED` |
| Prerequisites | Decision IDs that must settle first |
| Dependents | Decision IDs to inspect on change |
| Blocks / affects | Destination slice or downstream artifact |
| Options | Viable choices when known |
| Evidence | Evidence IDs or source links |
| Resolution | Chosen answer and rationale |
| Invalidation rule | Evidence or premise that would reopen it |

The frontier is the set of actionable `OPEN` or `REOPENED` decisions with all prerequisites settled and no current claim. `CLAIMED` is active work, not frontier; `BLOCKED` remains visible in the graph and exit gate.

The effort cannot exit while any destination-blocking decision is `OPEN`, `CLAIMED`, `BLOCKED`, or `REOPENED`, even if that decision is not currently actionable.

## Assumption ledger

Use one row per assumption:

| ID | Assumption | Impact | Confidence | Evidence | Status | Blocks / affects |
| --- | --- | --- | --- | --- | --- | --- |

Allowed statuses: `OPEN`, `VALIDATED`, `REFUTED`, `ACCEPTED-RISK`, `SUPERSEDED`.

High-impact assumptions cannot remain `OPEN` at exit. `ACCEPTED-RISK` requires a named human decision or explicit user acceptance.

## Invariant ledger

Record stable business or system truths, not temporary context:

| ID | Invariant | Scope | Rationale | Enforcement | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |

Link to the project domain invariant ledger when one exists. Do not put invariants in `CONTEXT.md` or bury them in ADR prose.

## Dependency and invalidation

When a decision is changed, refuted, or superseded:

1. Record the old and new state and triggering evidence.
2. Visit every direct dependent.
3. Mark it `REOPENED`, `NEEDS-UPDATE` in its downstream artifact, or still valid with a reason.
4. Continue transitively for reopened dependents.
5. Recompute the frontier and exit gate.

Never silently edit the old rationale into the new one. Preserve the decision history concisely.
