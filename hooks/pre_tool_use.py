#!/usr/bin/env python3
"""Conservatively deny selected destructive Git commands from Codex Bash hooks."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys


MAX_INPUT = 65_536
MAX_DEPTH = 4
DENY_REASON = "DG001: destructive Git command blocked by repository hook."
DYNAMIC_REASON = "DG002: dynamic Git command could not be classified safely."
OPERATORS = {";", "&&", "||", "|", "&", "(", ")"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$", re.DOTALL)
SHELLS = {"sh", "bash", "zsh", "dash"}
KNOWN_GIT_SUBCOMMANDS = {
    "add", "am", "apply", "archive", "bisect", "blame", "branch", "bundle",
    "checkout", "cherry", "cherry-pick", "clean", "clone", "commit", "config",
    "describe", "diff", "difftool", "fetch", "format-patch", "fsck", "gc", "grep",
    "init", "log", "maintenance", "merge", "mergetool", "mv", "notes", "pull",
    "push", "range-diff", "rebase", "reflog", "remote", "repack", "replace",
    "request-pull", "reset", "restore", "revert", "rm", "shortlog", "show",
    "show-branch", "sparse-checkout", "stash", "status", "submodule", "switch",
    "tag", "worktree",
}


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def deny(reason: str = DENY_REASON) -> int:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    json.dump(output, sys.stdout, separators=(",", ":"))
    return 0


def read_payload() -> dict[str, object] | None:
    raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    if not raw or len(raw) > MAX_INPUT:
        return None
    try:
        value = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def tokenize(command: str) -> list[str]:
    if "\x00" in command:
        raise ValueError("NUL")
    normalized = command.replace("\\\r\n", "").replace("\\\n", "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n").replace("\n", ";")
    lexer = shlex.shlex(normalized, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def segments(tokens: list[str]) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in OPERATORS or token and all(char in ";&|()" for char in token):
            if current:
                result.append(current)
                current = []
        else:
            current.append(token)
    if current:
        result.append(current)
    return result


def skip_wrapper(tokens: list[str], index: int) -> int:
    while index < len(tokens):
        token = tokens[index]
        base = os.path.basename(token)
        if token == "!" or ASSIGNMENT.fullmatch(token):
            index += 1
            continue
        if base in {"command", "builtin", "nohup", "time"}:
            index += 1
            while index < len(tokens) and tokens[index].startswith("-"):
                index += 1
            continue
        if base in {"env", "sudo"}:
            index += 1
            while index < len(tokens) and (tokens[index].startswith("-") or ASSIGNMENT.fullmatch(tokens[index])):
                index += 1
            continue
        break
    return index


def git_arguments(tokens: list[str], index: int) -> list[str]:
    args = tokens[index + 1:]
    if any(any(marker in token for marker in ("$", "`", "*", "?", "[", "]")) for token in args):
        raise RuntimeError(DYNAMIC_REASON)
    offset = 0
    while offset < len(args):
        token = args[offset]
        if not token.startswith("-"):
            break
        if token in {
            "--no-pager", "--paginate", "-p", "-P", "--literal-pathspecs",
            "--no-optional-locks", "--bare", "--no-replace-objects",
        }:
            offset += 1
        elif token in {"-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix"}:
            if offset + 1 >= len(args):
                raise RuntimeError(DYNAMIC_REASON)
            offset += 2
        elif token == "-c" or token.startswith("-c") and token != "-C":
            raise RuntimeError(DYNAMIC_REASON)
        elif token.startswith("-C") and token != "-C":
            offset += 1
        elif token.startswith("--exec-path"):
            raise RuntimeError(DYNAMIC_REASON)
        elif any(token.startswith(prefix) for prefix in ("--git-dir=", "--work-tree=", "--namespace=", "--super-prefix=")):
            offset += 1
        elif token.startswith("--config-env"):
            raise RuntimeError(DYNAMIC_REASON)
        else:
            raise RuntimeError(DYNAMIC_REASON)
    effective = args[offset:]
    if not effective or effective[0] not in KNOWN_GIT_SUBCOMMANDS:
        raise RuntimeError(DYNAMIC_REASON)
    if effective[0] == "config" and any(token.casefold().lstrip("-").startswith("alias.") for token in effective[1:]):
        raise RuntimeError(DYNAMIC_REASON)
    return effective


def has_short_flag(args: list[str], flag: str) -> bool:
    return any(token.startswith("-") and not token.startswith("--") and flag in token[1:] for token in args)


def has_long_prefix(args: list[str], prefix: str) -> bool:
    return any(token.startswith(prefix) for token in args if token.startswith("--"))


def executable_name(token: str) -> str:
    name = os.path.basename(token).casefold()
    return name[:-4] if name.endswith(".exe") else name


def destructive(args: list[str]) -> bool:
    if not args:
        return False
    subcommand = args[0]
    rest = args[1:]
    if any(marker in subcommand for marker in ("$", "`", "${")):
        raise RuntimeError(DYNAMIC_REASON)
    if subcommand == "reset":
        return any(has_long_prefix(rest, prefix) for prefix in ("--h", "--mer", "--k", "--rec"))
    if subcommand == "clean":
        return True
    if subcommand == "checkout":
        return True
    if subcommand == "restore":
        return True
    if subcommand == "branch":
        return (
            any(has_short_flag(rest, flag) for flag in ("d", "D", "f", "M", "C"))
            or has_long_prefix(rest, "--del")
            or has_long_prefix(rest, "--force")
        )
    if subcommand == "config":
        return not bool(rest and rest[0] in {"--get", "--get-all", "--get-regexp", "--list", "-l", "get", "list"})
    if subcommand == "stash":
        return bool(rest and rest[0] in {"drop", "clear"})
    if subcommand == "push":
        return True
    if subcommand == "reflog":
        return bool(rest and rest[0] in {"expire", "delete"})
    if subcommand == "gc":
        return True
    if subcommand == "maintenance":
        return True
    if subcommand == "rm":
        return True
    if subcommand == "worktree":
        return not bool(rest and rest[0] == "list")
    if subcommand == "switch":
        return (
            any(token.startswith("-C") for token in rest)
            or has_short_flag(rest, "f")
            or has_long_prefix(rest, "--force")
            or has_long_prefix(rest, "--force-c")
            or has_long_prefix(rest, "--discard")
            or has_long_prefix(rest, "--or")
        )
    if subcommand == "tag":
        return (
            has_short_flag(rest, "d")
            or has_short_flag(rest, "f")
            or has_long_prefix(rest, "--del")
            or has_long_prefix(rest, "--force")
        )
    if subcommand == "submodule":
        return True
    if subcommand == "notes":
        return bool(rest and rest[0] in {"remove", "prune"})
    if subcommand == "replace":
        return has_short_flag(rest, "d") or has_short_flag(rest, "f") or has_long_prefix(rest, "--del")
    return subcommand in {"difftool", "filter-branch", "filter-repo", "mergetool", "repack"}


def command_is_destructive(command: str, depth: int = 0) -> bool:
    if depth > MAX_DEPTH:
        raise RuntimeError(DYNAMIC_REASON)
    tokenized = tokenize(command)
    if any(any(marker in token for marker in ("$", "`", "*", "?", "[", "]")) for token in tokenized):
        raise RuntimeError(DYNAMIC_REASON)
    if any(re.search(r"\{[^{}]*(?:,|\.\.)[^{}]*\}", token) for token in tokenized):
        raise RuntimeError(DYNAMIC_REASON)
    for part in segments(tokenized):
        index = skip_wrapper(part, 0)
        if index >= len(part):
            continue
        if any(marker in part[index] for marker in ("$", "`")):
            raise RuntimeError(DYNAMIC_REASON)
        for position, token in enumerate(part):
            base = executable_name(token)
            if base == "eval":
                raise RuntimeError(DYNAMIC_REASON)
            if base == "env" and any(
                option.startswith("-S") or option.startswith("--s") for option in part[position + 1:]
            ):
                raise RuntimeError(DYNAMIC_REASON)
            if base in SHELLS:
                for option in range(position + 1, len(part)):
                    shell_flag = part[option]
                    if shell_flag.startswith("-") and not shell_flag.startswith("--") and "c" in shell_flag[1:]:
                        if option + 1 >= len(part):
                            raise RuntimeError(DYNAMIC_REASON)
                        if command_is_destructive(part[option + 1], depth + 1):
                            return True
                        break
            if base == "git" and destructive(git_arguments(part, position)):
                return True
            if base == "git" and any(ASSIGNMENT.fullmatch(item) for item in part[:position]):
                raise RuntimeError(DYNAMIC_REASON)
    return False


def main() -> int:
    payload = read_payload()
    if payload is None or payload.get("hook_event_name") != "PreToolUse" or payload.get("tool_name") != "Bash":
        return deny(DYNAMIC_REASON)
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return deny(DYNAMIC_REASON)
    command = tool_input.get("command")
    if not isinstance(command, str) or not command or len(command) > MAX_INPUT:
        return deny(DYNAMIC_REASON)
    try:
        if command_is_destructive(command):
            return deny()
    except (ValueError, RuntimeError):
        return deny(DYNAMIC_REASON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
