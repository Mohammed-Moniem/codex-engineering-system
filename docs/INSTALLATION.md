# Installation

## Product syntax

- ChatGPT desktop: type `@` and select a skill.
- Codex CLI or IDE: type `$` to mention a skill, or use `/skills`.

## Repository-scoped use

Clone the repository and run Codex from its root or a child directory. Codex scans `.agents/skills` from the working directory to the repository root.

## Individual skills

Ask the built-in `$skill-installer` to install a GitHub repository subpath, for example `.agents/skills/wayfinder`. Individual skill directories are self-contained; references, assets, and scripts do not reach outside their skill.

## Whole bundle

Add this repository as a Git marketplace, then install the plugin:

```bash
codex plugin marketplace add Mohammed-Moniem/codex-engineering-system
codex plugin add codex-engineering-system@codex-engineering-system
```

For a local clone under review, substitute the clone's path in the first command. There are three supported paths:

1. Clone the repository and use its repo-scoped skills immediately.
2. Add the Git or local marketplace and install the included skills-only plugin.
3. Submit the plugin through the current Codex universal-directory workflow.

The marketplace and plugin manifests are ready for local validation and future universal-directory submission. This repository does not claim that a public GitHub URL by itself is a universal plugin-directory listing. Follow the current [OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins) for local marketplace testing and submission.

Codex supports symlinked skill folders. Advanced users may link selected directories from `.agents/skills` into their user skill directory, but should review the exact source before doing so.

## Hooks

Installed plugin hooks require explicit trust. Use `/hooks` to inspect their source and current hash. The skills work without the hooks; session recovery then requires manually opening `.codex/wayfinder/ACTIVE`.
