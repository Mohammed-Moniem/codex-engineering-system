---
name: setup-boundaries
description: Add optional TypeScript module-boundary enforcement adapted to an existing repository. Use when dependency direction is agreed and automated import rules would prevent real regressions; do not assume a fixed source layout.
---

# Setup Boundaries

Read [typescript.md](references/typescript.md) before selecting a tool or rule shape.

1. Inspect the actual module graph, package manager, TypeScript config, lint/build tools, and established architecture.
2. Define a small boundary policy from existing intended dependency direction. Do not invent layers to fit a template.
3. Prefer an existing approved checker. Consider dependency-cruiser or an equivalent only when it fits the repository and dependency policy.
4. Add the least invasive configuration and documentation.
5. Prove the rule with `PASS → deliberate violation FAIL → revert PASS`.
6. Run normal checks and report adoption or migration work for pre-existing violations.

Do not add a dependency without user authorization and review. Never weaken a rule merely to make the initial run green; scope or phase adoption explicitly.
