# TypeScript boundary setup

## Selection

Prefer the checker already used by the repository. If none exists, compare a dependency graph checker, lint import rules, and package-manager workspace constraints against the actual graph and CI budget.

## Minimal policy

- Name real modules or packages discovered in the repository.
- Express allowed dependency direction and a reason.
- Scope generated, test, tooling, and migration code deliberately.
- Provide an exception process with owner and expiry.
- Avoid path assumptions such as `src/packages`.

## Proof

Record three commands and results:

1. Existing code passes, or known violations are baselined with an explicit migration plan.
2. One deliberate forbidden import fails for the intended rule.
3. Removing the import restores a pass.

Pin any new dependency through the repository's normal lockfile and audit process. Do not fetch or execute installer scripts from untrusted sources.
