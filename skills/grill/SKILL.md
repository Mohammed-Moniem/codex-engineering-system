---
name: grill
description: Resolve a bounded, fuzzy engineering design through a dependency-aware human interview. Use when facts can be gathered by Codex but one-session product, policy, UX, or architecture decisions still require a person.
---

# Grill

Build a small decision tree, then expose only the decision-ready frontier.

1. State the destination and identify what is fact versus choice.
2. Investigate code, documentation, tools, and trustworthy sources for discoverable facts. Do not ask the user to retrieve facts Codex can obtain.
3. Order decisions by dependency. Ask one conceptual branch at a time; combine only independent, simultaneously answerable choices.
4. For each question, give the evidence, viable options, consequences, and a recommended default when appropriate. Do not choose for the user.
5. Persist each answer immediately:
   - domain term → domain glossary;
   - durable rule → invariant ledger;
   - hard-to-reverse surprising trade-off → ADR;
   - active planning choice → Wayfinder decision or plan artifact.
6. Update dependent questions after every answer. Do not re-ask a settled decision unless its premise changed.

Finish when the bounded decision tree is resolved. Route ordinary work to native Plan mode or `standard-plan`; route expanding or multi-session fog to Wayfinder.
