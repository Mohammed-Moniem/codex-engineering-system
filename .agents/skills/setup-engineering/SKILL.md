---
name: setup-engineering
description: Adopt this engineering system in a repository by discovering tracker, documentation, test, domain, and hook conventions without overwriting established project behavior. Use once per repository or for an explicit setup refresh.
---

# Setup Engineering

Inspect before writing.

1. Discover repository instructions, languages, package managers, check commands, CI, tracker references, documentation layout, domain artifacts, release process, and current hooks.
2. Propose the smallest convention map using [engineering-config.md](assets/engineering-config.md). Prefer existing names and paths.
3. Choose the tracker adapter: local Markdown by default; GitHub Issues only with explicit user choice and authenticated access.
4. Configure pointers to existing glossary, invariant, ADR, spec, ticket, and handoff locations. Do not move or overwrite them.
5. Offer optional Wayfinder recovery hooks and boundary enforcement separately. Hooks require source review and trust; boundaries require an agreed dependency direction.
6. Verify every discovered command safely. Mark commands requiring services, credentials, or destructive state as unverified rather than running them.
7. Write only after showing the intended files and preserving existing conventions.

Return the adopted convention map, verification evidence, and any deferred optional setup.
