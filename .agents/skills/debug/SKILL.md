---
name: debug
description: Diagnose and fix a hard bug, flaky failure, or performance regression through deterministic reproduction and falsifiable hypotheses. Use when a feedback loop can be built; do not guess-first.
---

# Debug

1. Reproduce the exact symptom with a deterministic command, test, trace, or benchmark. Record environment and expected versus actual behavior.
2. Minimize the reproduction without losing the failure.
3. Form 3–5 falsifiable hypotheses ranked by evidence and cost to test.
4. Instrument the boundary that separates the leading hypotheses. Avoid broad speculative edits.
5. Test one hypothesis at a time and update the evidence table.
6. Fix the verified cause with the smallest durable change.
7. Add a regression test at a stable observable seam.
8. Re-run the original reproduction, focused checks, and relevant surrounding checks. Remove temporary instrumentation.
9. Write a concise postmortem: cause, why existing controls missed it, fix, regression evidence, and prevention only when justified.

If no reliable feedback loop can be built, say what is missing and route external knowledge to `questionnaire` or a bounded experiment to `prototype`.
