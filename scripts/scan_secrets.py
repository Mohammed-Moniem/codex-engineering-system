#!/usr/bin/env python3
"""Scan the current repository and reachable Git history for likely secrets."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
MAX_FILE = 2_000_000
PLACEHOLDERS = ("YOUR_", "EXAMPLE_", "DUMMY_", "REDACTED", "CHANGEME")


def detector_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        ("private-key", re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
        ("github-token", re.compile("gh" + r"[pousr]_[A-Za-z0-9]{30,}")),
        ("aws-access-key", re.compile("AK" + r"IA[0-9A-Z]{16}")),
        ("slack-token", re.compile("xo" + r"x[baprs]-[A-Za-z0-9-]{20,}")),
        ("service-token", re.compile("sk" + r"-[A-Za-z0-9_-]{24,}")),
    ]


ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)"
    r"\s*[:=]\s*['\"]([^'\"\s]{16,})['\"]"
)


def entropy(value: str) -> float:
    if not value:
        return 0.0
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in Counter(value).values())


def findings(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for detector, pattern in detector_patterns():
        for match in pattern.finditer(text):
            value = match.group(0)
            if not value.upper().startswith(PLACEHOLDERS):
                found.append((detector, value))
    for match in ASSIGNMENT.finditer(text):
        value = match.group(1)
        if not value.upper().startswith(PLACEHOLDERS) and entropy(value) >= 3.5:
            found.append(("high-entropy-secret-assignment", value))
    return found


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def run_git(
    args: list[str], input_text: str | None = None, root: Path = ROOT
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def worktree_files(root: Path = ROOT) -> Iterable[tuple[str, bytes]]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if listed.returncode == 0:
        paths = [item for item in listed.stdout.split(b"\0") if item]
        for raw in paths:
            path = root / raw.decode("utf-8", "surrogateescape")
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= MAX_FILE:
                yield path.relative_to(root).as_posix(), path.read_bytes()
        return
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and path.stat().st_size <= MAX_FILE:
            yield path.relative_to(root).as_posix(), path.read_bytes()


def scan_records(records: Iterable[tuple[str, bytes]], scope: str) -> list[str]:
    reports: list[str] = []
    for label, raw in records:
        if b"\x00" in raw[:8192]:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for detector, value in findings(text):
            reports.append(f"{scope}:{label}:{detector}:{fingerprint(value)}")
    return reports


def history_records(root: Path = ROOT) -> Iterable[tuple[str, bytes]]:
    inside = run_git(["rev-parse", "--is-inside-work-tree"], root=root)
    if inside.returncode != 0:
        return
    shallow = run_git(["rev-parse", "--is-shallow-repository"], root=root)
    if shallow.returncode == 0 and shallow.stdout.strip() == "true":
        raise RuntimeError("history scan refuses a shallow repository")
    objects = run_git(["rev-list", "--objects", "--all"], root=root)
    if objects.returncode != 0:
        raise RuntimeError("unable to enumerate Git history")
    paths: dict[str, str] = {}
    for line in objects.stdout.splitlines():
        object_id, _, path = line.partition(" ")
        paths.setdefault(object_id, path or "<unmapped>")
    if not paths:
        return
    checked = run_git(
        ["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        "\n".join(paths) + "\n",
        root,
    )
    if checked.returncode != 0:
        raise RuntimeError("unable to inspect Git objects")
    for line in checked.stdout.splitlines():
        object_id, kind, size_text = line.split(" ", 2)
        if kind != "blob" or int(size_text) > MAX_FILE:
            continue
        blob = subprocess.run(
            ["git", "cat-file", "blob", object_id],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=10,
        )
        if blob.returncode == 0:
            yield f"{paths.get(object_id, '<unmapped>')}@{object_id[:12]}", blob.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="scan worktree and reachable history")
    group.add_argument("--worktree", action="store_true", help="scan current tracked and untracked files")
    group.add_argument("--history", action="store_true", help="scan all reachable Git blobs")
    parser.add_argument("--json", action="store_true", help="emit machine-readable redacted results")
    args = parser.parse_args()

    scan_worktree = args.all or args.worktree or not args.history
    scan_history = args.all or args.history
    reports: list[str] = []
    if scan_worktree:
        reports.extend(scan_records(worktree_files(), "worktree"))
    try:
        if scan_history:
            reports.extend(scan_records(history_records(), "history"))
    except RuntimeError as exc:
        print(f"Secret scan error: {exc}", file=sys.stderr)
        return 2
    reports = sorted(set(reports))
    if args.json:
        print(json.dumps({"clean": not reports, "findings": reports}, separators=(",", ":")))
    elif reports:
        for report in reports:
            print(f"POTENTIAL_SECRET {report}")
        print(f"Secret scan failed with {len(reports)} redacted finding(s).")
    else:
        scopes = "worktree and history" if scan_worktree and scan_history else "worktree" if scan_worktree else "history"
        print(f"Secret scan clean: {scopes}.")
    return 1 if reports else 0


if __name__ == "__main__":
    raise SystemExit(main())
