# Hook design

Codex discovers the bundled `hooks/hooks.json` when the plugin is enabled. Non-managed hooks do not run until the user reviews and trusts their current definition.

## SessionStart recovery

`session_start.py` runs on `startup`, `resume`, `clear`, and `compact`. It:

1. Parses hook input without reflecting it.
2. Resolves the current Git root.
3. Reads only `.codex/wayfinder/ACTIVE`.
4. Accepts one relative Markdown path beneath `.codex/wayfinder/efforts/`.
5. Rejects control characters, traversal, absolute paths, missing targets, and symlink escapes.
6. Emits a short `additionalContext` pointer, never the map contents.

Malformed input fails open with no added context because this hook is an ergonomic enhancement, not an enforcement boundary.

## PreToolUse Git guardrail

`pre_tool_use.py` receives structured `Bash` input, tokenizes commands without executing them, finds Git invocations through common wrappers and compound syntax, and denies selected commands that discard local state or rewrite remote history. It blocks Bash-based pushes, garbage collection, maintenance, legacy checkout, and submodule `foreach` because effective configuration or nested commands can make those operations destructive. Use `git switch` for ordinary branch switching. Ambiguous Git options, aliases, shell expansion, glob syntax, and unrecognized Git subcommands fail closed. Because the hook is deliberately conservative, use a reviewed non-Bash specialized tool for commands that require those features.

The deny response uses a constant reason code and does not echo attacker-controlled command text. Safe read-only commands and dry runs remain available.

Hooks observe many local tools but not every possible execution path. Repository permissions, sandboxing, review, and user authorization remain the real security boundaries.
