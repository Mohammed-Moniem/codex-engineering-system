# Routing reference

| Signal | Primary route | Typical composition |
| --- | --- | --- |
| Local, reversible, clear change | quickplan | quickplan → build |
| Multi-file ordinary feature with known behavior | native Plan mode or `standard-plan` | standard plan → build → review-council |
| Broad unknowns, dependencies, or several sessions | wayfinder | wayfinder → spec → tickets → build |
| Bounded human choice blocks design | grill | grill → native Plan mode or `standard-plan` |
| Evidence can settle the question | research | research → current planning tier |
| A small artifact can test feasibility | prototype | prototype → current decision |
| Knowledge exists only outside available sources | questionnaire | questionnaire → grill/wayfinder |
| Reproducible failure or regression | debug | debug → review-council |
| Unverified incoming request | triage | triage → selected planning/build route |
| Existing change needs review | review-council | review-council → build fixes |
| Structural pain without chosen solution | architecture | architecture → grill/wayfinder/plan |

## Priority

1. Explicit skill invocation.
2. Safety-specific workflow: conflict resolution, debug, review, or triage.
3. Planning depth.
4. Supporting knowledge or delivery skill.

Do not route by estimated line count alone. Use decision uncertainty, blast radius, reversibility, evidence quality, and expected session count.

High-risk work is not automatically Wayfinder. A well-specified security fix can use native Plan mode, `standard-plan`, or a bounded build; a harmless but undefined product domain may require Wayfinder.
