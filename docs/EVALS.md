# Evals and validation

## Local gate

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/scan_secrets.py --all
```

The gate is dependency-free apart from Git and Python 3.11 or newer.

## What is automated

- Skill frontmatter, folder/name equality, unique names, concise descriptions, and absence of a custom `plan` skill.
- Skill-local `agents/openai.yaml` interface fields, `$skill` default prompts, and invocation policy.
- Relative Markdown links and direct reachability of each reference from its `SKILL.md`.
- Plugin manifest paths and metadata.
- Router and planning-depth fixture coverage, including negative and explicit-override cases.
- Skill smoke fixture coverage.
- SessionStart path and output safety.
- PreToolUse destructive-Git parsing, wrappers, malformed payloads, and benign commands.
- GitHub workflow permissions, immutable action pins, full checkout history, and forbidden triggers.
- Secret patterns in the worktree, staged index blobs, Git reference names, every pathname in every reachable commit tree, deduplicated Git blob bodies, commit messages, and annotated tags; unsupported oversized objects fail the gate explicitly.

## Router evals

`evals/router-cases.json` is an offline behavior contract, not the runtime router. The test oracle encodes only stable priority rules. Natural-language model behavior should also be forward-tested in a fresh Codex task before a release.

## Adding a fixture

Give every case a stable ID, prompt, expected route, and reason. Include near-miss and negated cases so broader descriptions do not silently steal ordinary Codex work.
