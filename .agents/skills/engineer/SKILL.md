---
name: engineer
description: Route software engineering work to the shallowest safe Codex workflow. Use for general feature, refactor, bug, architecture, review, or delivery requests when the user has not explicitly chosen another skill.
---

# Engineer

Classify the request before adding process. Honor an explicitly invoked skill.

## Route

1. Identify the requested outcome, current evidence, uncertainty, reversibility, risk, and likely session count.
2. Route to one primary workflow:
   - Small and clear: `quickplan`, or a directly bounded `build` when no planning artifact adds value.
   - Bounded and non-trivial: Codex's native `plan` skill. Do not emulate or shadow it.
   - Large, foggy, cross-system, or multi-session: `wayfinder`.
   - One-session fuzzy decision: `grill`, then native `plan`.
   - Hard bug or performance regression: `debug`.
   - Raw incoming bug, feature, or PR: `triage`.
   - Review: `review-council`.
   - Structural debt: `architecture`; route selected changes through grill or Wayfinder only if decisions remain.
3. Research discoverable facts. Ask the user only for human decisions, authority, preferences, or unavailable external knowledge.
4. State the selected route in one sentence, then follow it. Do not produce a ceremony menu.

Read [routing.md](references/routing.md) when signals conflict or multiple skills must compose.

## Boundaries

- Treat explicit `@quickplan` / `$quickplan`, `@plan` / `$plan`, and `@wayfinder` / `$wayfinder` as overrides.
- Never let a planning artifact expand the user's authority.
- Escalate depth only when new evidence shows the current tier cannot resolve a blocking uncertainty.
- Keep the next artifact single-source: map, spec, ticket, or implementation evidence—not duplicated prose.
