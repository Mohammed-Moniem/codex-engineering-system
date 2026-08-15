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

`pre_tool_use.py` receives structured `Bash` input, tokenizes commands without executing them, and denies selected Git commands that discard local state, rewrite remote history, contact supplied remotes, or launch opaque nested commands. It blocks Bash-based pushes, garbage collection, maintenance, legacy checkout, clean, restore, rm, submodule lifecycle commands, executable Git configuration, command-launching Git families, and other high-risk forms. Use `git switch` for ordinary branch switching. Compound Git commands, cross-segment shell state, ambiguous Git options, environment assignments around Git, aliases, shell expansion, glob syntax, unrecognized Git subcommands, stdin-fed shells, and dynamic launchers such as `xargs` fail closed. Run benign Git commands as separate Bash calls. Because the hook is deliberately conservative, use a reviewed non-Bash specialized tool for commands that require denied features.

The deny response uses a constant reason code and does not echo attacker-controlled command text. Safe read-only commands remain available. Remote inspection is limited to local configuration reads; `git remote show` requires `-n` or `--no-query` so it cannot contact a remote or invoke a transport helper. `git clean` is denied even in dry-run mode because its abbreviated, operand-taking option grammar cannot be classified safely from raw command tokens.

Exact `--abort` forms for merge, cherry-pick, revert, rebase, and am are an intentional narrow exception. They support recovery from an invalid or unsafe in-progress operation, but can discard conflict-resolution work created after that operation began. The `resolve-conflicts` workflow must inspect the operation state and use an abort only when that recovery tradeoff is justified.

Hooks observe many local tools but not every possible execution path. Repository permissions, sandboxing, review, and user authorization remain the real security boundaries.
