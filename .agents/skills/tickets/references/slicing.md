# Delivery slicing

## Prefer vertical evidence

A good slice crosses only the layers required to demonstrate one real behavior. It has an observable result, focused tests, and a bounded rollback.

Avoid horizontal tickets such as “build all models” followed by “build all APIs” unless a platform prerequisite is independently useful and verifiable.

## Fresh-context test

A ticket fits a fresh Codex context when it provides:

- one outcome and clear non-goals;
- all blocking decisions already linked;
- a limited set of relevant surfaces;
- explicit dependencies;
- acceptance and verification that do not require hidden conversation state.

## Wide changes

Use expand–migrate–contract:

1. `EXPAND`: add backward-compatible capability and verification.
2. `MIGRATE`: move callers or data in observable batches.
3. `CONTRACT`: remove the compatibility path after evidence proves completion.

Each phase must be independently safe, testable, and reversible where practical.
