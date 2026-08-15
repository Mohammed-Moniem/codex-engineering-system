---
name: wizard
description: Guide a deterministic human-in-the-loop setup, verification, or cutover that Codex cannot safely complete itself. Use for credential entry, physical action, account approval, or privileged console steps—not ordinary agent-executable work.
---

# Wizard

Create a checkpointed procedure only for actions that genuinely require the human.

For each step provide:

1. **Precondition** and exact target.
2. **Human action** with placeholders, never live secrets.
3. **Expected signal** that proves the step succeeded.
4. **Safe failure action** or rollback.
5. **Evidence to return** with secrets redacted.

Run one checkpoint at a time. Verify returned evidence before advancing. Stop on an unexpected state; do not improvise around permissions, billing, destructive changes, or security controls. Do not ask the user to perform terminal or browser work Codex can safely do within granted authority.
