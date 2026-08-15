# Planning model

## Three depths

| Tier | Entry | Boundary | Exit |
| --- | --- | --- | --- |
| Quickplan | Small, bounded, clear | Inspect only enough context to avoid obvious mistakes | Compact executable plan and verification |
| Native Plan | Bounded, non-trivial | Explore requirements, repository, dependencies, risks, and test strategy | Ordered implementation plan |
| Wayfinder | Large, foggy, multi-session | Resolve decision dependencies and evidence before delivery design | Clear route ready for specification |

Explicit invocation wins. Otherwise `engineer` chooses the shallowest tier that can safely remove the relevant uncertainty.

## Native Plan integration

Codex ships a system `plan` skill. This repository does not define another skill named `plan`, because duplicate names appear independently in selectors and create avoidable ambiguity. `engineer` routes the standard tier to the native capability and documents the same user-facing invocation: `@plan` in ChatGPT desktop and `$plan` in Codex CLI or IDE.

## Routing principles

- Route a simple implementation to quickplan or directly to one bounded build item.
- Route an ordinary feature or refactor to native Plan.
- Route a large or multi-session decision space to Wayfinder.
- Route one-session fuzzy decisions to grill, then native Plan.
- Route bugs with a reproducible signal to debug.
- Route raw incoming work to triage.
- Route review requests to review-council.
- Route structural debt to architecture, then grill or Wayfinder only when a human decision remains.
- Research discoverable facts. Ask humans for decisions, authority, preferences, or unavailable external knowledge.

## Authority boundary

A plan, map, ticket, or generated instruction never grants authority to deploy, publish, delete, spend, contact people, alter external services, or take another material action. Authority comes from the user and host policy, not from an agent-authored artifact.
