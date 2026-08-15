from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


def load_scanner():
    path = ROOT / "scripts" / "scan_secrets.py"
    spec = importlib.util.spec_from_file_location("scan_secrets", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load secret scanner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = load_scanner()


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, timeout=5)


class SecretScannerTests(unittest.TestCase):
    def test_detects_dynamic_fake_token_and_redacts_report(self) -> None:
        token = "gh" + "p_" + "A1b2" * 9
        found = scanner.scan_records([("fixture.txt", token.encode())], "test")
        self.assertEqual(1, len(found))
        self.assertNotIn(token, found[0])

    def test_allows_explicit_placeholder(self) -> None:
        text = 'api_key="YOUR_TOKEN_VALUE_PLACEHOLDER"'
        self.assertEqual([], scanner.findings(text))

    def test_history_finds_deleted_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            git(repo, "init", "-q", "-b", "main")
            git(repo, "config", "user.name", "Example User")
            git(repo, "config", "user.email", "example@example.com")
            token = "gh" + "p_" + "Z9y8" * 9
            path = repo / "temporary.txt"
            path.write_text(token + "\n", encoding="utf-8")
            git(repo, "add", "temporary.txt")
            git(repo, "commit", "-q", "-m", "add fixture")
            path.unlink()
            git(repo, "add", "-u")
            git(repo, "commit", "-q", "-m", "remove fixture")

            current = scanner.scan_records(scanner.worktree_files(repo), "worktree")
            history = scanner.scan_records(scanner.history_records(repo), "history")
            self.assertEqual([], current)
            self.assertTrue(history)
            self.assertNotIn(token, "\n".join(history))


if __name__ == "__main__":
    unittest.main()
