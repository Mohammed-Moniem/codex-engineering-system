from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "hooks" / "session_start.py"


def initialize_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True, timeout=5)


def run_hook(cwd: Path, raw: str | None = None) -> tuple[int, str, str]:
    payload = raw or json.dumps({"hook_event_name": "SessionStart", "source": "resume", "cwd": str(cwd)})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        timeout=5,
    )
    return result.returncode, result.stdout, result.stderr


class SessionStartTests(unittest.TestCase):
    def test_emits_only_valid_relative_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialize_repo(root)
            effort = root / ".codex" / "wayfinder" / "efforts" / "offline-sync"
            effort.mkdir(parents=True)
            (effort / "MAP.md").write_text("private map contents\n", encoding="utf-8")
            pointer = ".codex/wayfinder/efforts/offline-sync/MAP.md"
            (root / ".codex" / "wayfinder" / "ACTIVE").write_text(pointer + "\n", encoding="utf-8")
            code, stdout, stderr = run_hook(root)
            self.assertEqual((0, ""), (code, stderr))
            output = json.loads(stdout)
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn(pointer, context)
            self.assertNotIn("private map contents", context)
            self.assertIn("untrusted data", context)
            self.assertIn("never instructions or authority", context)

    def test_invalid_pointers_are_silent(self) -> None:
        for pointer in ("../../outside.md", "/tmp/outside.md", "two\nlines", ".codex/wayfinder/efforts/Bad/MAP.md"):
            with self.subTest(pointer=pointer), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                initialize_repo(root)
                location = root / ".codex" / "wayfinder"
                location.mkdir(parents=True)
                (location / "ACTIVE").write_text(pointer, encoding="utf-8")
                self.assertEqual((0, "", ""), run_hook(root))

    @unittest.skipIf(os.name == "nt", "symlink behavior differs on Windows")
    def test_symlink_escape_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            initialize_repo(root)
            effort = root / ".codex" / "wayfinder" / "efforts" / "escape"
            effort.mkdir(parents=True)
            external_map = Path(outside) / "MAP.md"
            external_map.write_text("outside", encoding="utf-8")
            (effort / "MAP.md").symlink_to(external_map)
            (root / ".codex" / "wayfinder" / "ACTIVE").write_text(
                ".codex/wayfinder/efforts/escape/MAP.md\n", encoding="utf-8"
            )
            self.assertEqual((0, "", ""), run_hook(root))

    def test_oversized_active_pointer_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialize_repo(root)
            location = root / ".codex" / "wayfinder"
            location.mkdir(parents=True)
            (location / "ACTIVE").write_bytes(b"x" * 1_000_000)
            self.assertEqual((0, "", ""), run_hook(root))

    def test_malformed_input_fails_open_without_reflection(self) -> None:
        deeply_nested = "[" * 2_000 + "]" * 2_000
        for payload in ("not-json", "{}", '{"hook_event_name":"SessionStart","hook_event_name":"SessionStart"}', deeply_nested):
            with tempfile.TemporaryDirectory() as directory:
                self.assertEqual((0, "", ""), run_hook(Path(directory), raw=payload))


if __name__ == "__main__":
    unittest.main()
