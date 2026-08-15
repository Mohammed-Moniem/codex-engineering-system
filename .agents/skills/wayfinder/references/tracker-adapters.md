# Tracker adapters

Wayfinder state must work with no external service. Keep tracker operations behind this contract:

- `create(ticket)` → stable tracker ID
- `read(id)` → current tracker representation
- `update(id, patch)` → versioned update
- `list(query)` → matching ticket summaries
- `link(id, relation, target)` → dependency or evidence edge
- `close(id, resolution)` → terminal state

## Local Markdown

Use the effort layout in `map-schema.md`. It is always available and is the default. Git commits provide history; file links provide evidence and dependencies.

## GitHub Issues

Use only when the user selected GitHub Issues and authenticated repository access is available.

- Keep GitHub-specific labels, issue templates, and API calls inside the adapter.
- Use one issue per decision ticket and link its canonical `D-NNN` ID.
- Prefer repository-native structured tools. Use `gh` only for gaps.
- Do not create, edit, label, or close issues without user authorization for external writes.
- Never put secret evidence or private source excerpts in an issue.
- Treat the active Markdown map as the recovery index unless the setup artifact explicitly chooses GitHub as authoritative.

If synchronization conflicts, stop and show both versions. Do not silently choose the newer timestamp.
