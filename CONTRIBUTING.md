# Contributing

Contributions should make Codex engineering work clearer, safer, or easier to verify without adding unnecessary ceremony.

## Before opening a change

1. Open an issue for a new skill or a material workflow change.
2. Keep skill descriptions concise and front-load their trigger boundary.
3. Add detailed formats to `references/`, copyable templates to `assets/`, and deterministic mechanics only to `scripts/`.
4. Use original wording. Cite upstream ideas and preserve applicable licenses.
5. Add or update positive, negative, and edge-case fixtures.
6. Avoid new dependencies unless the benefit is clear and the security cost is reviewed.

## Required checks

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/scan_secrets.py --all
```

All checks must pass. Pull requests should explain the user-visible behavior, risks, verification evidence, and whether invocation policy changed.

## Pull requests

- Keep one coherent change per pull request.
- Do not include transcripts, generated runtime state, private project data, or real credentials.
- Do not weaken hook parsing or publication gates without dedicated adversarial tests.
- Do not add a `plan` skill; improve native Plan-mode integration or the `standard-plan` fallback instead.
