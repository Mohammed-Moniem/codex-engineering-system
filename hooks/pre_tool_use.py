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
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def tokenize(command: str) -> list[str]:
    if "\x00" in command:
        raise ValueError("NUL")
    normalized = command.replace("\r\n", "\n").replace("\r", "\n").replace("\n", ";")
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


def git_arguments(tokens: list[str], index: int) -> list[str] | None:
    index = skip_wrapper(tokens, index)
    if index >= len(tokens):
        return None
    command = tokens[index]
    if any(marker in command for marker in ("$", "`")):
        raise RuntimeError(DYNAMIC_REASON)
    if os.path.basename(command) != "git":
        return None
    args = tokens[index + 1 :]
    offset = 0
    while offset < len(args):
        token = args[offset]
        if token in {"--no-pager", "--paginate", "--literal-pathspecs", "--no-optional-locks"}:
            offset += 1
        elif token in {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}:
            offset += 2
        elif any(token.startswith(prefix) for prefix in ("--git-dir=", "--work-tree=", "--namespace=", "--exec-path=")):
            offset += 1
        else:
            break
    return args[offset:]


def has_short_flag(args: list[str], flag: str) -> bool:
    return any(token.startswith("-") and not token.startswith("--") and flag in token[1:] for token in args)


def destructive(args: list[str]) -> bool:
    if not args:
        return False
    subcommand = args[0]
    rest = args[1:]
    if any(marker in subcommand for marker in ("$", "`", "${")):
        raise RuntimeError(DYNAMIC_REASON)
    if subcommand == "reset":
        return any(flag in rest for flag in ("--hard", "--merge", "--keep"))
    if subcommand == "clean":
        dry = "--dry-run" in rest or has_short_flag(rest, "n")
        forced = "--force" in rest or has_short_flag(rest, "f")
        return forced and not dry
    if subcommand == "checkout":
        return "--" in rest or "." in rest or "--force" in rest or has_short_flag(rest, "f")
    if subcommand == "restore":
        return "--staged" not in rest or "--worktree" in rest
    if subcommand == "branch":
        return "-D" in rest or ("--delete" in rest and "--force" in rest)
    if subcommand == "stash":
        return bool(rest and rest[0] in {"drop", "clear"})
    if subcommand == "push":
        return (
            any(flag in rest for flag in ("--force", "--force-with-lease", "--delete", "-f"))
            or any(token.startswith("+") or token.startswith(":") for token in rest)
        )
    if subcommand == "reflog":
        return bool(rest and rest[0] in {"expire", "delete"})
    if subcommand == "gc":
        return any(token == "--prune=now" for token in rest)
    if subcommand == "rm":
        return "--cached" not in rest
    if subcommand == "worktree":
        return bool(rest and rest[0] in {"remove", "prune"} and ("--force" in rest or has_short_flag(rest, "f")))
    return subcommand in {"filter-branch", "filter-repo"}


def command_is_destructive(command: str, depth: int = 0) -> bool:
    if depth > MAX_DEPTH:
        raise RuntimeError(DYNAMIC_REASON)
    for part in segments(tokenize(command)):
        index = skip_wrapper(part, 0)
        if index >= len(part):
            continue
        base = os.path.basename(part[index])
        if any(marker in part[index] for marker in ("$", "`")):
            raise RuntimeError(DYNAMIC_REASON)
        if base in {"sh", "bash", "zsh", "dash"} and "-c" in part[index + 1 :]:
            option = part.index("-c", index + 1)
            if option + 1 >= len(part):
                raise RuntimeError(DYNAMIC_REASON)
            if command_is_destructive(part[option + 1], depth + 1):
                return True
            continue
        if base == "eval":
            if command_is_destructive(" ".join(part[index + 1 :]), depth + 1):
                return True
            continue
        args = git_arguments(part, 0)
        if args is not None and destructive(args):
            return True
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
