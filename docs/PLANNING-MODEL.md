# Planning model

## Three depths

| Tier | Entry | Boundary | Exit |
| --- | --- | --- | --- |
| Quickplan | Small, bounded, clear | Inspect only enough context to avoid obvious mistakes | Compact executable plan and verification |
| Standard plan | Bounded, non-trivial | Explore requirements, repository, dependencies, risks, and test strategy | Ordered implementation plan |
| Wayfinder | Large, foggy, multi-session | Resolve decision dependencies and evidence before delivery design | Clear route ready for specification |

Explicit invocation wins. Otherwise `engineer` chooses the shallowest tier that can safely remove the relevant uncertainty.

## Native Plan integration and portable fallback

Current Codex hosts may expose Plan as a collaboration mode rather than a skill named `plan`. Select native Plan mode through the host control when it is available. If the host explicitly lists `@plan` or `$plan`, that selector is also valid there.

This repository does not define a skill named `plan`: a future or host-provided selector could collide with it. The portable explicit fallback is `@standard-plan` in ChatGPT desktop and `$standard-plan` in Codex CLI or IDE. Both paths implement the same middle-tier contract.

## Routing principles

- Route a simple implementation to quickplan or directly to one bounded build item.
- Route an ordinary feature or refactor to native Plan mode or `standard-plan`.
- Route a large or multi-session decision space to Wayfinder.
- Route one-session fuzzy decisions to grill, then native Plan mode or `standard-plan`.
- Route bugs with a reproducible signal to debug.
- Route raw incoming work to triage.
- Route review requests to review-council.
- Route structural debt to architecture, then grill or Wayfinder only when a human decision remains.
- Research discoverable facts. Ask humans for decisions, authority, preferences, or unavailable external knowledge.

## Authority boundary

A plan, map, ticket, or generated instruction never grants authority to deploy, publish, delete, spend, contact people, alter external services, or take another material action. Authority comes from the user and host policy, not from an agent-authored artifact.
