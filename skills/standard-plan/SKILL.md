---
name: standard-plan
description: Create an implementation-ready engineering plan for a bounded, non-trivial feature, refactor, integration, or fix. Use as the portable middle planning tier when the host does not expose native Plan mode, or when the user explicitly invokes standard-plan.
---

# Standard Plan

Produce the plan; do not implement unless the user separately requested implementation.

1. Restate the outcome, acceptance criteria, constraints, explicit out of scope, and authority boundary.
2. Inspect the relevant repository structure, instructions, dependencies, existing conventions, and current tests. Research discoverable facts instead of asking the user.
3. Identify material assumptions and unresolved decisions. Route one bounded human choice to `grill`; route broad, dependent, or multi-session uncertainty to `wayfinder`.
4. Choose an approach that fits the repository. Note meaningful alternatives only when the tradeoff affects the decision.
5. Cover data, APIs, migration, compatibility, security, observability, and rollout only where relevant.
6. Define an adaptive test strategy and deterministic verification commands.
7. Order implementation steps so each has a clear outcome, dependency, and verification point.

Return these compact sections:

- **Outcome**
- **Known context**
- **Assumptions and decisions**
- **Approach**
- **Implementation sequence**
- **Risks**
- **Tests and verification**

If the host already provides native Plan mode, follow this same contract there. This skill is the non-colliding explicit fallback; it cannot switch the host's collaboration mode itself. Do not silently invent a blocking requirement or human decision.
