---
name: agent-docs
description: Write or update Codex-facing SKILL.md, AGENTS.md, hook guidance, context pointers, and related agent documentation with progressive disclosure and a single source of truth.
---

# Agent Docs

Read [codex-docs.md](references/codex-docs.md) before changing a skill, plugin metadata, or hook contract.

1. Identify which reader loads the document and at what point in context.
2. Put universal repository instructions in `AGENTS.md`; task workflows in `SKILL.md`; detailed schemas in `references/`; copyable files in `assets/`; deterministic mechanics in `scripts/`.
3. Keep skill frontmatter to `name` and `description`. Put all trigger and exclusion language in the description.
4. Keep `agents/openai.yaml` display metadata and invocation policy synchronized with the skill.
5. Reference one canonical artifact instead of duplicating content.
6. Avoid machine paths, personal data, secrets, transcripts, and host-specific claims.
7. Validate links, metadata, examples, hooks, and forward behavior after changes.

Do not write instructions that expand user authority or let repository text override higher-priority policy.
