---
name: architecture
description: Analyze architecture debt using change coupling, dependency direction, cycles, module depth, testability, and agent navigability. Use for structural diagnosis and actionable candidates, not automatic rewrites.
---

# Architecture

Use repository evidence rather than imposing a preferred vocabulary. Read [heuristics.md](references/heuristics.md) for measurements and cautions.

1. Identify the change or maintenance pain being investigated.
2. Map components, ownership, dependency direction, public seams, tests, and high-churn files.
3. Inspect change coupling, cycles, dependency fan-in/out, shallow forwarding layers, hidden state, and the effort needed for a new agent to find the right edit surface.
4. Separate observed evidence from interpretation.
5. Produce a small ranked set of candidates with benefit, cost, migration path, risk, and a proof step.
6. Respect the project's established architecture unless evidence shows it is causing the named pain.

Use deep-module ideas as heuristics, not doctrine. Do not refactor during diagnosis. Route value or boundary choices to `grill` or `wayfinder`; route an accepted candidate to native Plan.
