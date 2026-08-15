---
name: build
description: Implement one bounded engineering ticket or work item with repository-aware tests, checks, deterministic verification, and self-review. Use when scope and required decisions are already clear.
---

# Build

Work on one bounded item.

1. Read the ticket, linked decisions, nearest agent instructions, relevant code, and repository check conventions.
2. Confirm the outcome, boundary, acceptance criteria, and current working-tree state. Preserve unrelated user changes.
3. Select an adaptive test strategy: TDD when a stable public seam makes it useful; characterization first for legacy behavior; focused post-change tests for mechanical work.
4. Implement the smallest coherent change. Follow existing architecture and avoid unrelated cleanup.
5. Run focused tests early, then the proportionate typecheck, lint, build, and broader tests.
6. Verify the exact user-visible or machine-observable outcome deterministically.
7. Review the diff against the ticket, repository standards, security boundaries, and regression risk.
8. Report changed files, verification evidence, remaining risk, and any follow-up.

Commit only when the user explicitly requested a commit. Repository conventions may shape commit contents but never supply commit authority. Never treat a ticket as authority for deployment, publication, destructive actions, or external writes.
