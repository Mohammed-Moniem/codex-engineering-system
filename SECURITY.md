# Security Policy

## Supported versions

Security fixes are applied to the latest release and the default branch.

## Report a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a public issue for a suspected vulnerability and do not include live secrets, private repository content, or personal data in a report.

Include the affected file or workflow, attacker-controlled input, expected security invariant, observed impact, and a minimal safe reproduction when available. Maintainers will acknowledge the report, validate it, and coordinate remediation and disclosure through GitHub.

## Scope

Particularly useful reports cover hook command parsing, path traversal or symlink escape, secret leakage, unsafe installation behavior, untrusted pull-request execution, or skill instructions that could silently expand user authority.

The destructive-Git hook is defense in depth. Codex hooks do not observe every hosted or specialized tool path, so the hook must not be treated as a complete sandbox or authorization boundary.
