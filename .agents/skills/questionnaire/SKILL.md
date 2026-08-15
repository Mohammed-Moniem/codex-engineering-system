---
name: questionnaire
description: Extract missing engineering knowledge from a subject-matter expert or stakeholder when the answer is not available in code, documentation, tools, or public sources. Do not use for discoverable facts.
---

# Questionnaire

1. State the decision or specification gap the external knowledge must close.
2. Remove every question answerable from available code, docs, data, or research.
3. Group remaining questions by owner and dependency; ask the smallest decision-ready set first.
4. Use concrete scenarios and edge cases instead of vague preference prompts.
5. Distinguish required answer, optional context, and evidence requested.
6. Provide an answer format that is easy to complete asynchronously.
7. On return, validate contradictions and persist answers into the relevant glossary, invariant, decision, assumption, or spec artifact.

Never invent the stakeholder's response or let an agent/subagent answer the stakeholder side.
