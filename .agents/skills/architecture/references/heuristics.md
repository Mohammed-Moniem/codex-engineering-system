# Architecture heuristics

- **Change coupling:** files or modules that repeatedly change together may hide a missing boundary.
- **Dependency direction:** unstable policy should not silently become a dependency of stable core rules.
- **Cycles:** distinguish harmless type cycles from runtime, ownership, or release cycles.
- **Module depth:** prefer a useful capability behind a small stable interface; do not measure quality by file size alone.
- **Forwarding layers:** a layer that adds no policy, isolation, translation, or test seam may be accidental complexity.
- **Testability:** a boundary should permit deterministic behavior checks without reconstructing the whole system.
- **Agent navigability:** names, ownership, and entry points should help a new agent find the intended change surface from repository evidence.

Support each claim with imports, callers, history, test structure, or a reproducible change path. Do not rename established concepts merely to match these heuristics.
