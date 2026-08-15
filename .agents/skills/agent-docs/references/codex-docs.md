# Codex documentation contract

## Skills

- Store repository skills at `.agents/skills/<name>/SKILL.md`.
- Use lowercase kebab-case names under 64 characters.
- Keep frontmatter to `name` and `description`.
- Put interface metadata and invocation policy in `agents/openai.yaml`.
- Explicit invocation is `@skill` in ChatGPT desktop and `$skill` or `/skills` in Codex CLI and IDE.
- Keep descriptions short because the initial skill list has a bounded context budget.

## Progressive disclosure

Link every reference directly from `SKILL.md` and explain when to read it. Keep references one level deep. Do not duplicate the same contract in the body and reference.

## Hooks

Treat stdin as untrusted JSON and stdout as a protocol. Never reflect secrets. Use constant error messages for enforcement hooks, canonical path checks for filesystem input, and deterministic tests for malicious strings.

## Source of truth

`AGENTS.md` governs repository-wide behavior. A skill governs one workflow. A durable project artifact governs its domain state. Generated handoffs and summaries point to these sources rather than replacing them.
