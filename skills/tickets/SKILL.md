---
name: tickets
description: Convert an implementation-ready specification into dependency-aware, independently demoable and verifiable delivery slices. Use after spec completion, not for raw requests or unresolved decision work.
---

# Tickets

Read [slicing.md](references/slicing.md) before splitting broad or cross-cutting work.

1. Trace each ticket to requirements, decisions, ADRs, research, and invariants.
2. Prefer a thin vertical path through real layers that produces observable behavior.
3. Keep each ticket small enough for a fresh Codex context and independently demoable or verifiable.
4. Declare blockers and dependencies. Do not hide order inside prose.
5. Include:
   - outcome and scope;
   - acceptance criteria;
   - referenced artifacts;
   - implementation boundary;
   - test strategy and deterministic verification;
   - risk and rollback note;
   - autonomy: `AFK`, `HITL`, or `HYBRID`.
6. For wide refactors or migrations, use `EXPAND`, `MIGRATE`, and `CONTRACT` phases instead of forcing an unsafe vertical slice.

Do not create tickets for decisions. If a blocking decision appears, return it to the plan or Wayfinder map.
