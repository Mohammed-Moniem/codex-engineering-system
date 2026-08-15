---
name: resolve-conflicts
description: Resolve Git merge, rebase, or cherry-pick conflicts by reconstructing intent from primary source, tests, and both sides of the change. Use only when a conflict operation is active or conflict markers are present.
---

# Resolve Conflicts

1. Inspect repository status and identify the active Git operation without changing it.
2. For each conflict, read base, ours, theirs, linked commits, surrounding source, tests, and generated-file provenance.
3. State the intent of each side and choose a resolution that preserves compatible intent. Do not mechanically keep one side.
4. Regenerate derived files from their source when safe; never hand-merge opaque generated output without a documented generator.
5. Remove conflict markers, stage only resolved files when appropriate, and run focused plus repository-required checks.
6. Reinspect the final diff against both intents.

Abort only when the operation is clearly invalid, unsafe, or based on the wrong branch/history. Explain the evidence and ask before aborting unless the user already authorized it. Never hide lost behavior with a passing syntax check.
