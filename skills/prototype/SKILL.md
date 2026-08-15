---
name: prototype
description: Run a throwaway engineering spike to retire one important uncertainty and return evidence to a plan or decision map. Use for UI, state, algorithm, API, data model, integration, AI, performance, or migration questions.
---

# Prototype

Read [branches.md](references/branches.md) and choose one branch: `UI`, `STATE`, `ALGORITHM`, `API`, `DATA-MODEL`, `INTEGRATION`, `AI-LLM`, `PERFORMANCE`, or `MIGRATION`.

Before changing files, declare:

- question or hypothesis;
- success and failure criteria;
- time and scope box;
- evidence to capture;
- production surfaces that must not change.

Build the smallest disposable artifact that can answer the question. Keep it isolated from production code unless the user explicitly authorizes a reversible spike in the working tree. Use dummy data and existing safe tools.

Return:

- **Verdict**: supported, rejected, mixed, or inconclusive;
- **Evidence** and reproduction commands;
- **Limitations**;
- **Decision impact**;
- **Assumptions affected**;
- **Cleanup performed or remaining**.

Do not polish or ship a prototype. A successful spike informs a decision; it is not automatically the implementation.
