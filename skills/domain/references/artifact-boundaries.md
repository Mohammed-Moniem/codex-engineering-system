# Domain artifact boundaries

| Artifact | Owns | Must not own |
| --- | --- | --- |
| `CONTEXT.md` or glossary | Domain vocabulary, definitions, aliases, examples | Implementation plan, temporary assumptions, decision history |
| Invariant ledger | Rules that remain true across implementations | One-off acceptance criteria, design preferences |
| ADR | A consequential, hard-to-reverse, surprising trade-off | Routine choices, status updates, meeting transcript |
| Wayfinder decision | An active planning choice and its dependencies | Full domain glossary or implementation tasks |
| Spec | Resolved behavior and delivery constraints | New blocking decisions |

Prefer existing repository locations. If none exist, use `docs/domain/CONTEXT.md`, `docs/domain/INVARIANTS.md`, and `docs/adr/NNNN-title.md`, but confirm before creating a new convention.

When an ADR is superseded, keep it and link the replacing ADR. When an invariant changes, record whether it was refuted, replaced, or narrowed and inspect dependent requirements and tests.
