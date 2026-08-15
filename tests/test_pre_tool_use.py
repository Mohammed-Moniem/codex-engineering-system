from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "hooks" / "pre_tool_use.py"


def run_hook(command: object, raw: str | None = None) -> tuple[int, str, str]:
    payload = raw
    if payload is None:
        payload = json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": command},
            }
        )
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        timeout=5,
    )
    return result.returncode, result.stdout, result.stderr


class PreToolUseTests(unittest.TestCase):
    DENY = [
        "git reset --hard",
        "/usr/bin/git -C repo reset --hard",
        "env X=1 command git clean -fdx",
        "git clean --force -d",
        "git checkout -- path",
        "git restore path",
        "git restore --staged -W path",
        "git restore --staged --work path",
        "git branch -D feature",
        "git stash clear",
        "git stash drop",
        "git push --force",
        "git push -f origin main",
        "git reflog expire --expire=now --all",
        "git gc --prune=now",
        "git -c gc.pruneExpire=now gc",
        "git -c clean.requireForce=false clean -dx",
        "git -c remote.origin.mirror=true push origin",
        "git push origin main",
        "sh -c 'git reset --hard'",
        "echo ok; git clean -fd",
        "echo $(git reset --hard)",
        'g""it re\\set --ha\\rd',
        'op=reset; git "$op" --hard',
        "git rm important.txt",
        "git filter-branch -- --all",
        "git re\\\nset --hard",
        "bash -lc 'git reset --hard'",
        "bash.exe -lc 'git reset --hard'",
        "printf x \"$(git reset --hard)\"",
        "git -c alias.wipe='reset --hard' wipe",
        "git config alias.wipe 'reset --hard'; git wipe",
        "git -p reset --hard",
        "git --no-replace-objects reset --hard",
        "env -u UNUSED git reset --hard",
        "env -S 'git reset --hard'",
        "env -Sgit reset --hard",
        "env --split=git reset --hard",
        "env.exe -S 'git reset --hard'",
        "{ git reset --hard; }",
        "if true; then git reset --hard; fi",
        ">output.txt git reset --hard",
        "git res?? --hard",
        "GIT=git; if true; then \"$GIT\" reset --hard; fi",
        "./g?t reset --hard",
        "g{i..i}t reset --hard",
        "FLAG=--hard; git reset \"$FLAG\"",
        "git reset --h",
        "git checkout main",
        "git checkout HEAD important.txt",
        "git checkout -Bmain HEAD~1",
        "git branch -df feature",
        "git branch --del feature",
        "git push --force-with-lease=main:expected origin main",
        "git switch -C main",
        "git switch -Cmain HEAD~1",
        "git switch -f main",
        "git switch --force main",
        "git.exe reset --hard",
        "git tag -d release",
        "git worktree remove old-tree",
        "git clean -en -fdx",
        "git -c gc.pruneExpire=now maintenance run --task=gc",
        "git submodule foreach 'git reset --hard'",
    ]

    ALLOW = [
        "git status",
        "git diff -- .",
        "git reset --soft HEAD~",
        "git clean -ndx",
        "git clean -nfd",
        "git switch main",
        "git restore --staged path",
        "printf '%s' 'git reset --hard'",
        "sh -c 'printf \"%s\" \"git clean -fd\"'",
        "git -p status",
        "git config --get user.name",
        "printf '%s' '{\"x\":1}'",
    ]

    def test_denies_destructive_commands_without_reflection(self) -> None:
        for command in self.DENY:
            with self.subTest(command=command):
                code, stdout, stderr = run_hook(command)
                self.assertEqual(0, code)
                self.assertEqual("", stderr)
                output = json.loads(stdout)
                decision = output["hookSpecificOutput"]
                self.assertEqual("deny", decision["permissionDecision"])
                self.assertNotIn(command, stdout)

    def test_allows_benign_commands(self) -> None:
        for command in self.ALLOW:
            with self.subTest(command=command):
                code, stdout, stderr = run_hook(command)
                self.assertEqual((0, "", ""), (code, stdout, stderr))

    def test_malformed_payloads_fail_closed(self) -> None:
        payloads = [
            "not-json",
            "{}",
            '{"hook_event_name":"PreToolUse","hook_event_name":"PreToolUse"}',
            json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": ["git", "status"]}}),
            json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Other", "tool_input": {"command": "git status"}}),
        ]
        for payload in payloads:
            with self.subTest(payload=payload[:40]):
                code, stdout, _ = run_hook("", raw=payload)
                self.assertEqual(0, code)
                self.assertEqual("deny", json.loads(stdout)["hookSpecificOutput"]["permissionDecision"])


if __name__ == "__main__":
    unittest.main()
