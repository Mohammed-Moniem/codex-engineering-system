# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic versioning.

## [Unreleased]

## [0.1.1] - 2026-08-15

### Fixed

- Package the canonical skill tree as a real top-level `skills/` directory so installed plugins expose every skill, including Wayfinder, to Codex discovery and autocomplete.
- Validate that the manifest targets the complete packaged skill set rather than relying on a symlink that marketplace installation can omit.

## [0.1.0] - 2026-08-15

### Added

- Initial Codex-first engineering workflow bundle.
- Quickplan, native Plan-mode integration with a portable Standard Plan fallback, and Wayfinder V2 planning depths.
- Discovery, specification, delivery, quality, maintenance, and session skills.
- Safe session-recovery and destructive-Git hook examples.
- Static validation, routing fixtures, hook tests, and history-aware secret scanning.
