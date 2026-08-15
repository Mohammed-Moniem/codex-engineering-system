#!/usr/bin/env python3
"""Validate repository structure and security-sensitive static contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
ACTION_LINE = re.compile(
    r"^\s*(?:-\s+)?uses:\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@([0-9a-f]{40})(?:\s+#.*)?$"
)
ALLOWED_INTERFACE = {"display_name", "short_description", "default_prompt"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, path: Path | str, message: str) -> None:
        try:
            label = Path(path).relative_to(ROOT).as_posix()
        except (TypeError, ValueError):
            label = str(path)
        self.errors.append(f"{label}: {message}")


def tracked_paths(check: Validation) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        check.error(ROOT, "unable to enumerate tracked files")
        return set()
    return {item.decode("utf-8", "surrogateescape") for item in result.stdout.split(b"\0") if item}


def parse_frontmatter(path: Path, check: Validation) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        check.error(path, "frontmatter must start at byte zero")
        return {}, text
    closing = text.find("\n---\n", 4)
    if closing < 0:
        check.error(path, "frontmatter closing delimiter is missing")
        return {}, text
    metadata: dict[str, str] = {}
    for line in text[4:closing].splitlines():
        if ":" not in line:
            check.error(path, f"invalid frontmatter line {line!r}")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in metadata:
            check.error(path, f"duplicate frontmatter key {key}")
        metadata[key] = value.strip('"')
    if set(metadata) != {"name", "description"}:
        check.error(path, "frontmatter must contain exactly name and description")
    body = text[closing + 5 :].strip()
    if not body:
        check.error(path, "skill body is empty")
    return metadata, text


def parse_openai_yaml(path: Path, check: Validation) -> dict[str, object]:
    result: dict[str, object] = {}
    section: str | None = None
    seen: set[tuple[str, str]] = set()
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw or any(marker in raw for marker in ("&", "*", "!!", "<<:")):
            check.error(path, f"unsupported YAML feature on line {number}")
        if not raw.startswith(" "):
            if not raw.endswith(":"):
                check.error(path, f"invalid top-level line {number}")
                continue
            section = raw[:-1]
            if section not in {"interface", "policy"}:
                check.error(path, f"unsupported top-level key {section}")
            continue
        if not raw.startswith("  ") or raw.startswith("   ") or ":" not in raw or section is None:
            check.error(path, f"invalid indentation or mapping on line {number}")
            continue
        key, value = raw.strip().split(":", 1)
        identity = (section, key)
        if identity in seen:
            check.error(path, f"duplicate key {section}.{key}")
        seen.add(identity)
        value = value.strip()
        if section == "interface":
            if key not in ALLOWED_INTERFACE:
                check.error(path, f"unsupported interface key {key}")
            if not (value.startswith('"') and value.endswith('"')):
                check.error(path, f"interface.{key} must be quoted")
                parsed: object = value
            else:
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    check.error(path, f"interface.{key} is not a valid quoted string")
                    parsed = ""
        else:
            if key != "allow_implicit_invocation" or value not in {"true", "false"}:
                check.error(path, "policy supports only a boolean allow_implicit_invocation")
            parsed = value == "true"
        result[f"{section}.{key}"] = parsed
    return result


def validate_skills(check: Validation) -> None:
    names: dict[str, Path] = {}
    tracked = tracked_paths(check)
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        check.error(SKILLS, "no skills found")
    for folder in skill_dirs:
        skill_file = folder / "SKILL.md"
        if not skill_file.is_file():
            check.error(folder, "SKILL.md is missing")
            continue
        for required_path in (skill_file, folder / "agents" / "openai.yaml"):
            relative = required_path.relative_to(ROOT).as_posix()
            if relative not in tracked:
                check.error(required_path, "required skill file is not tracked or staged")
        metadata, text = parse_frontmatter(skill_file, check)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not NAME.fullmatch(name) or len(name) > 64:
            check.error(skill_file, "invalid skill name")
        if folder.name != name:
            check.error(skill_file, "folder name must equal frontmatter name")
        if name in names:
            check.error(skill_file, f"duplicate skill name also declared by {names[name]}")
        names[name] = skill_file
        if not description or len(description) > 1024 or "TODO" in description:
            check.error(skill_file, "description is empty, too long, or unfinished")
        if name == "plan":
            check.error(skill_file, "plan is reserved for host-native Plan mode; use standard-plan")
        metadata_path = folder / "agents" / "openai.yaml"
        if not metadata_path.is_file():
            check.error(folder, "agents/openai.yaml is required")
        else:
            ui = parse_openai_yaml(metadata_path, check)
            expected = {
                "interface.display_name",
                "interface.short_description",
                "interface.default_prompt",
                "policy.allow_implicit_invocation",
            }
            if set(ui) != expected:
                check.error(metadata_path, "metadata fields do not match the repository contract")
            short = ui.get("interface.short_description", "")
            if not isinstance(short, str) or not 25 <= len(short) <= 64:
                check.error(metadata_path, "short_description must be 25-64 characters")
            prompt = ui.get("interface.default_prompt", "")
            if not isinstance(prompt, str) or f"${name}" not in prompt:
                check.error(metadata_path, f"default_prompt must mention ${name}")
        reference_dir = folder / "references"
        if reference_dir.is_dir():
            for reference in reference_dir.rglob("*"):
                if reference.is_file() and f"references/{reference.relative_to(reference_dir).as_posix()}" not in text:
                    check.error(reference, "reference is not linked directly from SKILL.md")


def validate_links(check: Validation) -> None:
    tracked = tracked_paths(check)
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            resolved = (path.parent / target).resolve(strict=False)
            if not resolved.is_relative_to(ROOT.resolve()):
                check.error(path, f"local link escapes repository: {target}")
            elif not resolved.exists():
                check.error(path, f"broken local link: {target}")
            else:
                relative = resolved.relative_to(ROOT.resolve()).as_posix()
                if relative not in tracked:
                    check.error(path, f"local link target is not tracked: {target}")


def validate_manifest(check: Validation) -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        check.error(path, f"invalid plugin manifest: {exc}")
        return
    for key in ("name", "version", "description", "author", "skills", "interface"):
        if key not in manifest:
            check.error(path, f"missing required field {key}")
    if manifest.get("name") != "codex-engineering-system":
        check.error(path, "unexpected plugin name")
    if manifest.get("skills") != "./skills/":
        check.error(path, "plugin manifest must use the conventional skills path")
    bridge = ROOT / "skills"
    if not bridge.is_symlink() or bridge.resolve(strict=False) != SKILLS.resolve(strict=False):
        check.error(bridge, "skills must be an in-repository symlink to canonical .agents/skills")
    if "hooks" in manifest:
        check.error(path, "omit the manifest hooks key; use default hooks/hooks.json discovery")

    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        check.error(marketplace_path, f"invalid marketplace manifest: {exc}")
        return
    if marketplace.get("name") != "codex-engineering-system":
        check.error(marketplace_path, "unexpected marketplace name")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
        check.error(marketplace_path, "marketplace must contain exactly one plugin entry")
        return
    entry = plugins[0]
    expected_entry_keys = {"name", "source", "policy", "category"}
    if set(entry) != expected_entry_keys:
        check.error(marketplace_path, "plugin entry fields do not match the repository contract")
    if entry.get("name") != manifest.get("name"):
        check.error(marketplace_path, "marketplace and plugin names must match")
    if entry.get("source") != {"source": "local", "path": "."}:
        check.error(marketplace_path, "marketplace must point to the repository plugin root")
    if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        check.error(marketplace_path, "marketplace policy must be explicit and installation-safe")


def validate_python(check: Validation) -> None:
    stdlib = set(sys.stdlib_module_names)
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            check.error(path, f"invalid Python: {exc}")
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module.split(".", 1)[0]]
            for module in modules:
                if module not in stdlib:
                    check.error(path, f"third-party Python import is not allowed: {module}")


def workflow_policy_errors(text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    without_expressions = re.sub(r"\$\{\{.*?\}\}", "", text, flags=re.DOTALL)
    if "\t" in text or re.search(r"(?m)^\s*(?:-\s*)?[A-Za-z_][A-Za-z0-9_-]*\s+:.*$", text):
        errors.append("workflow must use canonical key syntax without tabs or space-before-colon aliases")
    if re.search(r'''(?m)^\s*(?:-\s*)?["'][^"']+["']\s*:.*$''', text):
        errors.append("quoted YAML mapping keys are forbidden")
    if re.search(r"(?m)(?:^|\s)(?:[&*][A-Za-z0-9_-]+|<<:)(?:\s|$)", text):
        errors.append("YAML anchors, aliases, and merge keys are forbidden")
    if "!" in without_expressions or re.search(r"(?m)^\s*%(?:YAML|TAG)\b", without_expressions):
        errors.append("YAML tags and directives are forbidden")
    if any(marker in without_expressions for marker in ("{", "}", "[", "]")):
        errors.append("YAML flow collections are forbidden")
    if re.search(r"(?m)^\s*\?\s+", text):
        errors.append("explicit complex YAML keys are forbidden")
    permission_roots = [index for index, line in enumerate(lines) if line == "permissions:"]
    if len(permission_roots) != 1:
        errors.append("workflow must contain exactly one top-level permissions block")
    else:
        index = permission_roots[0] + 1
        values: list[str] = []
        while index < len(lines) and (not lines[index] or lines[index].startswith(" ")):
            if lines[index]:
                values.append(lines[index])
            index += 1
        if values != ["  contents: read"]:
            errors.append("the sole effective permission must be contents: read")
    if any(line.startswith((" ", "\t")) and line.lstrip().startswith("permissions:") for line in lines):
        errors.append("job-level permissions are forbidden")
    if re.search(r"(?im)^\s*(?:permissions:\s*)?write-all\s*$|^\s*[a-z-]+:\s*write\s*$", text):
        errors.append("write permissions are forbidden")
    action_lines = [line for line in lines if re.search(r"\buses\s*:", line) and not line.lstrip().startswith("#")]
    if not action_lines:
        errors.append("workflow must declare at least one pinned action")
    for line in action_lines:
        if ACTION_LINE.fullmatch(line) is None:
            errors.append("every action must use canonical owner/repository@40-hex syntax")
    return errors


def validate_distribution_inventory(check: Validation) -> None:
    tracked = tracked_paths(check)
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if untracked.returncode != 0:
        check.error(ROOT, "unable to enumerate untracked files")
    else:
        for raw in (item for item in untracked.stdout.split(b"\0") if item):
            check.error(raw.decode("utf-8", "surrogateescape"), "untracked non-ignored file is outside the publication inventory")

    package_roots = (ROOT / ".agents", ROOT / ".codex-plugin", ROOT / "hooks")
    for package_root in package_roots:
        for path in package_root.rglob("*"):
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_symlink():
                check.error(path, "nested package symlinks are forbidden")
                continue
            if path.is_file():
                relative = path.relative_to(ROOT).as_posix()
                if relative not in tracked:
                    check.error(path, "package file is not tracked or staged")
    if "skills" not in tracked:
        check.error(ROOT / "skills", "plugin skills bridge is not tracked or staged")


def validate_workflows(check: Validation) -> None:
    directory = ROOT / ".github" / "workflows"
    workflows = sorted((*directory.glob("*.yml"), *directory.glob("*.yaml")))
    required_path = directory / "validate.yml"
    if required_path not in workflows:
        check.error(required_path, "validation workflow is missing")
        return
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        if "pull_request_target" in text:
            check.error(path, "pull_request_target is forbidden")
        for error in workflow_policy_errors(text):
            check.error(path, error)
        if "timeout-minutes:" not in text:
            check.error(path, "job timeout is required")

    text = required_path.read_text(encoding="utf-8")
    if "fetch-depth: 0" not in text:
        check.error(required_path, "checkout must fetch full history for secret scanning")
    for required in ("scripts/validate_repo.py", "unittest discover", "scripts/scan_secrets.py --all"):
        if required not in text:
            check.error(required_path, f"workflow does not run {required}")


def validate_content(check: Validation) -> None:
    unfinished_word = "TO" + "DO"
    placeholder_word = "PLACE" + "HOLDER"
    unfinished = re.compile(rf"\[(?:{unfinished_word}|{placeholder_word}):|{unfinished_word}:")
    private_prefix = "/" + "Users" + "/"
    file_uri = "file" + "://"
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if listed.returncode != 0:
        check.error(ROOT, "unable to enumerate publishable content")
        return
    paths = sorted(ROOT / item.decode("utf-8", "surrogateescape") for item in listed.stdout.split(b"\0") if item)
    for path in paths:
        if path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > 2_000_000:
            check.error(path, "file exceeds 2 MB repository limit")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if unfinished.search(text):
            check.error(path, "unfinished placeholder found")
        if private_prefix in text or file_uri in text:
            check.error(path, "machine-specific path or URI found")


def validate_evals(check: Validation) -> None:
    path = ROOT / "evals" / "router-cases.json"
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        check.error(path, f"invalid router fixture: {exc}")
        return
    required_routes = {"direct", "quickplan", "plan", "wayfinder", "grill", "debug", "triage", "review-council", "architecture"}
    found = {case.get("expected_route") for case in cases if isinstance(case, dict)}
    missing = required_routes - found
    if missing:
        check.error(path, f"missing router routes: {sorted(missing)}")
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        check.error(path, "router case IDs must be non-empty and unique")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"id", "prompt", "expected_route", "reason"}:
            check.error(path, "each router case must use the exact fixture fields")


def main() -> int:
    check = Validation()
    validate_skills(check)
    validate_links(check)
    validate_manifest(check)
    validate_distribution_inventory(check)
    validate_python(check)
    validate_workflows(check)
    validate_content(check)
    validate_evals(check)
    if check.errors:
        for error in check.errors:
            print(f"ERROR {error}")
        print(f"Validation failed with {len(check.errors)} error(s).")
        return 1
    skill_count = len([path for path in SKILLS.iterdir() if path.is_dir()])
    print(f"Validation passed: {skill_count} skills and repository contracts are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
