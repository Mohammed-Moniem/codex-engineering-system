---
name: quickplan
description: Produce a compact execution plan for a small, bounded engineering change whose requirements and architecture are already clear. Do not use for foggy, high-risk, cross-system, or multi-session work.
---

# Quickplan

Plan only as deeply as the change requires.

1. Restate the outcome and boundary in one sentence.
2. Inspect only the relevant files, conventions, and existing checks needed to avoid an obvious mistake.
3. List any material assumption. Resolve discoverable facts instead of asking the user.
4. Write 2–6 ordered implementation steps with concrete files or components when known.
5. Specify deterministic verification: focused tests, typecheck/lint/build commands, and one user-visible check when relevant.
6. Name the main risk or rollback point only if material.

Return:

- **Outcome**
- **Assumptions**
- **Plan**
- **Verification**
- **Ready to build**: yes/no and the blocker when no

Stop after the plan unless the user also requested implementation. If the task reveals an unresolved design choice, route to native Plan or `grill`; use `wayfinder` only when uncertainty is genuinely broad or persistent.
