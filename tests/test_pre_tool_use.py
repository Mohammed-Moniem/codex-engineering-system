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
        "git clean -ndx",
        "git clean -nfd",
        "git clean --ex -n -fdx",
        "git checkout -- path",
        "git restore path",
        "git restore --staged path",
        "git restore --pathspec-from-file --staged",
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
        "git -c diff.external=helper diff",
        "git -cdiff.external=helper diff",
        "git --exec-path=/tmp diff",
        "GIT_EXTERNAL_DIFF=helper git diff",
        "env GIT_EXTERNAL_DIFF=helper git diff",
        "git config diff.external helper",
        "git config diff.external helper; git diff",
        "export GIT_EXTERNAL_DIFF='sh -c \"git reset --hard\"'; git diff HEAD^",
        "shopt -s expand_aliases\nalias wipe='git reset --hard'\nwipe",
        "git status && git diff",
        "git -c clean.requireForce=false clean -dx",
        "git -c remote.origin.mirror=true push origin",
        "git push origin main",
        "sh -c 'git reset --hard'",
        "echo ok; git clean -fd",
        "echo $(git reset --hard)",
        'g""it re\\set --ha\\rd',
        'op=reset; git "$op" --hard',
        "git rm important.txt",
        "git rm --cached important.txt",
        "git rm -f --pathspec-from-file --cached",
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
        "git tag -f release HEAD~1",
        "git worktree remove old-tree",
        "git worktree prune",
        "git branch -f main HEAD~1",
        "git branch -M old main",
        "git reset --recurse-submodules",
        "git switch --orphan clean-room",
        "git submodule update --force --checkout",
        "git submodule deinit -f --all",
        "git difftool --extcmd helper",
        "git mergetool",
        "git repack -Ad",
        "git notes remove HEAD",
        "git notes --ref refs/notes/review remove HEAD",
        "git replace -f HEAD HEAD~1",
        "git replace --force HEAD HEAD~1",
        "git grep --open-files-in-pager='sh -c git-reset' .",
        "git rebase --exec='git reset --hard' main",
        "git archive --exec='git reset --hard' HEAD",
        "git fetch --upload-pack='git reset --hard' origin",
        "git clone -u 'git reset --hard' example.com/repo.git",
        "git pull --upload-pack='git reset --hard' origin main",
        "git request-pull main example.com/repo.git topic",
        "git bisect run sh -c 'git reset --hard'",
        "git merge --strategy=custom topic",
        "git cherry-pick --strategy=custom HEAD",
        "git revert --strategy=custom HEAD",
        "git stash -q clear",
        "git reflog --all expire --expire=now",
        "git apply --unsafe-paths change.patch",
        "git sparse-checkout reapply",
        "git remote remove origin",
        "git remote prune origin",
        "git remote -v remove origin",
        "git remote show origin",
        "git init --separate-git-dir=/tmp/outside .",
        "git init --sep=/tmp/outside .",
        "git mv -f source destination",
        "git mv --force source destination",
        "git mv --for source destination",
        "git clean -en -fdx",
        "git -c gc.pruneExpire=now maintenance run --task=gc",
        "git submodule foreach 'git reset --hard'",
        r"printf '\147\151\164\040\162\145\163\145\164\040\055\055\150\141\162\144\012' | bash",
        r"printf '\147\151\164\000\162\145\163\145\164\000\055\055\150\141\162\144\000' | xargs -0",
        "bash script.sh",
        "parallel command ::: input",
    ]

    ALLOW = [
        "git status",
        "git diff -- .",
        "git reset --soft HEAD~",
        "git switch main",
        "printf '%s' 'git reset --hard'",
        "sh -c 'printf \"%s\" \"git clean -fd\"'",
        "git -p status",
        "git config --get user.name",
        "git config --list",
        "git worktree list --porcelain",
        "git remote -v",
        "git remote get-url origin",
        "git remote show -n origin",
        "git remote show --no-query origin",
        "git init .",
        "git mv source destination",
        "git merge --abort",
        "git cherry-pick --abort",
        "git revert --abort",
        "git rebase --abort",
        "git am --abort",
        "printf '%s' '{\"x\":1}'",
        "export EXAMPLE_FLAG=1; printf '%s' ok",
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
