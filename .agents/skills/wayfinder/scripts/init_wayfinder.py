#!/usr/bin/env python3
"""Create a new local Wayfinder effort without external dependencies."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess


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


def require_secure_directory_api() -> None:
    required = (os.open, os.mkdir, os.rename, os.unlink)
    if (
        any(function not in os.supports_dir_fd for function in required)
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
    ):
        raise SystemExit("Secure descriptor-relative initialization is unavailable on this platform.")


def open_directory(parent: int, name: str, create: bool = False) -> int:
    if create:
        try:
            os.mkdir(name, 0o755, dir_fd=parent)
        except FileExistsError:
            pass
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(name, flags, dir_fd=parent)
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise SystemExit("Wayfinder directory validation failed.")
    return descriptor


def write_new(parent: int, name: str, content: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(name, flags, 0o600, dir_fd=parent)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def replace_active(parent: int, relative_map: str) -> None:
    temporary = f".ACTIVE.{secrets.token_hex(8)}"
    descriptor: int | None = None
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        descriptor = os.open(temporary, flags, 0o600, dir_fd=parent)
        payload = (relative_map + "\n").encode("utf-8")
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        os.rename(temporary, "ACTIVE", src_dir_fd=parent, dst_dir_fd=parent)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temporary, dir_fd=parent)
        except FileNotFoundError:
            pass


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

    require_secure_directory_api()
    root = git_root(args.root.resolve(strict=True))

    assets = Path(__file__).resolve(strict=True).parent.parent / "assets"
    title = args.slug.replace("-", " ").title()
    templates = {
        "MAP.md": assets / "MAP.md",
        "ASSUMPTIONS.md": assets / "ASSUMPTIONS.md",
        "INVARIANTS.md": assets / "INVARIANTS.md",
    }
    descriptors: list[int] = []
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(root_fd)
        codex_fd = open_directory(root_fd, ".codex", create=True)
        descriptors.append(codex_fd)
        wayfinder_fd = open_directory(codex_fd, "wayfinder", create=True)
        descriptors.append(wayfinder_fd)
        efforts_fd = open_directory(wayfinder_fd, "efforts", create=True)
        descriptors.append(efforts_fd)
        try:
            os.mkdir(args.slug, 0o755, dir_fd=efforts_fd)
        except FileExistsError as exc:
            raise SystemExit("That Wayfinder effort already exists.") from exc
        effort_fd = open_directory(efforts_fd, args.slug)
        descriptors.append(effort_fd)
        os.mkdir("decisions", 0o755, dir_fd=effort_fd)
        os.mkdir("evidence", 0o755, dir_fd=effort_fd)
        for name, source in templates.items():
            content = source.read_text(encoding="utf-8")
            content = content.replace("{{TITLE}}", title).replace("{{DESTINATION}}", args.destination.strip())
            write_new(effort_fd, name, content)

        relative_map = f".codex/wayfinder/efforts/{args.slug}/MAP.md"
        replace_active(wayfinder_fd, relative_map)
    except OSError as exc:
        raise SystemExit(f"Secure Wayfinder initialization failed: {exc.strerror or 'filesystem error'}.") from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)

    print(relative_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
