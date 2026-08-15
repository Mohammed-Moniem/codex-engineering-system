---
name: tdd
description: Drive behavior through a stable public interface or seam with a focused red-green-refactor loop. Use when a fast deterministic test can express the requirement; do not force TDD for exploratory, visual, generated, or infrastructure-only work.
---

# TDD

1. Choose the narrowest durable observable seam, not a private implementation detail.
2. Write one failing test for one behavior. Run it and confirm failure for the intended reason.
3. Implement the minimum change that makes the test pass.
4. Run the focused test, then relevant surrounding tests.
5. Refactor only while green; keep behavior unchanged.
6. Repeat for the next meaningful behavior.

Avoid mock-heavy tests that merely repeat implementation. Use fakes at real boundaries, keep tests deterministic, and preserve a regression test for every fixed defect.

Switch techniques when the feedback loop is slow, the interface is still being discovered, or the test would couple to incidental structure. Record why and use the build skill's adaptive strategy.
