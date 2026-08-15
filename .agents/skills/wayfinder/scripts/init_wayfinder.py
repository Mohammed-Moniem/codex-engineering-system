#!/usr/bin/env python3
"""Create a new local Wayfinder effort without external dependencies."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def git_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise SystemExit("Not inside a Git repository.")
    return Path(result.stdout.strip()).resolve(strict=True)


def require_inside(path: Path, root: Path) -> None:
    if not path.resolve(strict=False).is_relative_to(root):
        raise SystemExit("Wayfinder path would escape the repository.")


def write_new(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--slug", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()

    if not SLUG.fullmatch(args.slug):
        raise SystemExit("Slug must be 1-64 lowercase letters, digits, or hyphens.")
    if not args.destination.strip() or len(args.destination) > 500 or CONTROL.search(args.destination):
        raise SystemExit("Destination must be one non-empty printable line of at most 500 characters.")

    root = git_root(args.root.resolve(strict=True))
    wayfinder = root / ".codex" / "wayfinder"
    effort = wayfinder / "efforts" / args.slug
    require_inside(wayfinder, root)
    require_inside(effort, root)

    if effort.exists() or effort.is_symlink():
        raise SystemExit("That Wayfinder effort already exists.")

    effort.mkdir(parents=True, exist_ok=False)
    (effort / "decisions").mkdir()
    (effort / "evidence").mkdir()

    assets = Path(__file__).resolve(strict=True).parent.parent / "assets"
    title = args.slug.replace("-", " ").title()
    templates = {
        "MAP.md": assets / "MAP.md",
        "ASSUMPTIONS.md": assets / "ASSUMPTIONS.md",
        "INVARIANTS.md": assets / "INVARIANTS.md",
    }
    for name, source in templates.items():
        content = source.read_text(encoding="utf-8")
        content = content.replace("{{TITLE}}", title).replace("{{DESTINATION}}", args.destination.strip())
        write_new(effort / name, content)

    relative_map = (effort / "MAP.md").relative_to(root).as_posix()
    wayfinder.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=".ACTIVE.",
        dir=wayfinder,
        delete=False,
    ) as handle:
        handle.write(relative_map + "\n")
        temporary = Path(handle.name)
    os.chmod(temporary, 0o600)
    os.replace(temporary, wayfinder / "ACTIVE")

    print(relative_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
