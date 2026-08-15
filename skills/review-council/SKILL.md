---
name: review-council
description: Review a code change through independent specification and code/standards axes, adding architecture, testing, security, performance, or operability axes only when the diff risk warrants them.
---

# Review Council

Read [axes.md](references/axes.md) to select optional axes.

1. Resolve the review scope, intended behavior, linked spec or ticket, repository standards, and verification evidence.
2. Always perform two independent passes:
   - `SPEC`: does the change meet the intended behavior and acceptance criteria?
   - `CODE-STANDARDS`: is the implementation correct, maintainable, and consistent with the repository?
3. Add `ARCHITECTURE`, `TESTING`, `SECURITY`, `PERFORMANCE`, or `OPERABILITY` only when affected surfaces justify them.
4. Validate each issue against the actual diff and relevant surrounding source. Do not report style preference as correctness risk.
5. Aggregate without erasing provenance. Use `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, or `OPTIONAL`, and name the axis that found it.

Return findings first, ordered by severity, with file/line, impact, evidence, and a concrete fix. Then list open questions and a short verification assessment. If there are no actionable findings, say so and name remaining test or coverage risk.
