---
name: handoff
description: Create a concise, portable, secret-redacted context handoff for another Codex task, agent, or human. Use when pausing, changing context, or transferring ownership without duplicating durable artifacts.
---

# Handoff

Use [handoff.md](assets/handoff.md) as the output shape.

1. Link durable artifacts instead of copying their content.
2. Include goal, current state, settled decisions, current frontier, blockers, relevant files/commits/artifacts, completed verification, remaining verification, and suggested next skills.
3. Preserve uncertainty and ownership. Do not turn an open question into a decision.
4. Redact tokens, credentials, private URLs, personal data, raw logs, and transcript paths.
5. Use repository-relative paths and reproducible commands. Remove stale narrative.

The handoff must be sufficient to resume safely, but short enough to read before opening detailed artifacts.
