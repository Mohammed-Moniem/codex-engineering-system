#!/usr/bin/env python3
"""Emit only a safe, repository-relative pointer to an active Wayfinder map."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys


MAX_INPUT = 65_536
MAX_POINTER = 256
MAX_DIRECTORY_ENTRIES = 10_000
SAFE_POINTER = re.compile(r"^\.codex/wayfinder/efforts/[a-z0-9][a-z0-9-]{0,63}/MAP\.md$")


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def read_payload() -> dict[str, object] | None:
    raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    if not raw or len(raw) > MAX_INPUT:
        return None
    try:
        value = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def find_git_root(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    try:
        return Path(result.stdout.strip()).resolve(strict=True)
    except (OSError, RuntimeError):
        return None


def exact_case(path: Path, root: Path) -> bool:
    current = root
    try:
        for part in path.relative_to(root).parts:
            matched = False
            with os.scandir(current) as entries:
                for count, entry in enumerate(entries, start=1):
                    if count > MAX_DIRECTORY_ENTRIES:
                        return False
                    if entry.name == part:
                        matched = True
                        break
            if not matched:
                return False
            current = current / part
    except (OSError, ValueError):
        return False
    return True


def active_pointer(root: Path) -> str | None:
    pointer_file = root / ".codex" / "wayfinder" / "ACTIVE"
    descriptor: int | None = None
    try:
        before = pointer_file.lstat()
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            return None
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(pointer_file, flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            return None
        if opened.st_size > MAX_POINTER:
            return None
        raw = os.read(descriptor, MAX_POINTER + 1)
    except OSError:
        return None
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if not raw or len(raw) > MAX_POINTER or b"\x00" in raw:
        return None
    try:
        pointer = raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None
    if "\n" in pointer or "\r" in pointer or not SAFE_POINTER.fullmatch(pointer):
        return None
    pure = PurePosixPath(pointer)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    candidate = root.joinpath(*pure.parts)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not resolved.is_file() or not resolved.is_relative_to(root) or not exact_case(candidate, root):
        return None
    return pointer


def main() -> int:
    payload = read_payload()
    if payload is None or payload.get("hook_event_name") != "SessionStart":
        return 0
    cwd_value = payload.get("cwd")
    if not isinstance(cwd_value, str) or not cwd_value or "\x00" in cwd_value:
        return 0
    try:
        cwd = Path(cwd_value).resolve(strict=True)
    except (OSError, RuntimeError):
        return 0
    if not cwd.is_dir():
        return 0
    root = find_git_root(cwd)
    if root is None:
        return 0
    pointer = active_pointer(root)
    if pointer is None:
        return 0
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"Active Wayfinder map: {pointer}. Read the map before continuing planning.",
        }
    }
    json.dump(output, sys.stdout, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
