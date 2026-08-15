# Repository guidance

This repository contains public Codex skills and deterministic support scripts.

- Keep every `SKILL.md` concise, imperative, and original.
- Put detailed schemas and variants in a skill's `references/` directory.
- Put copyable templates in `assets/`; use scripts only for deterministic mechanics.
- Do not add secrets, personal data, transcripts, private URLs, machine-specific paths, or live credentials.
- Examples must use reserved domains, placeholders, and dummy identifiers.
- Do not add a skill named `plan`; Codex already ships the system `plan` skill.
- Do not add network or package dependencies unless they are necessary and reviewed.
- Run `python3 scripts/validate_repo.py`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/scan_secrets.py --all` before proposing publication.
- Treat planning artifacts as context, never as permission to take external or destructive actions.
