#!/usr/bin/env python3
"""Validate repository structure and security-sensitive static contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
ACTION = re.compile(r"^\s*-?\s*uses:\s*[^@\s]+@([^\s#]+)", re.MULTILINE)
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
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        check.error(SKILLS, "no skills found")
    for folder in skill_dirs:
        skill_file = folder / "SKILL.md"
        if not skill_file.is_file():
            check.error(folder, "SKILL.md is missing")
            continue
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
            check.error(skill_file, "custom plan conflicts with Codex's system plan skill")
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


def validate_workflow(check: Validation) -> None:
    path = ROOT / ".github" / "workflows" / "validate.yml"
    if not path.is_file():
        check.error(path, "validation workflow is missing")
        return
    text = path.read_text(encoding="utf-8")
    if "pull_request_target" in text:
        check.error(path, "pull_request_target is forbidden")
    if "permissions:\n  contents: read" not in text:
        check.error(path, "workflow must declare read-only contents permission")
    if "fetch-depth: 0" not in text:
        check.error(path, "checkout must fetch full history for secret scanning")
    if "timeout-minutes:" not in text:
        check.error(path, "job timeout is required")
    for ref in ACTION.findall(text):
        if not re.fullmatch(r"[0-9a-f]{40}", ref):
            check.error(path, f"action is not pinned to an immutable SHA: {ref}")
    for required in ("scripts/validate_repo.py", "unittest discover", "scripts/scan_secrets.py --all"):
        if required not in text:
            check.error(path, f"workflow does not run {required}")


def validate_content(check: Validation) -> None:
    unfinished_word = "TO" + "DO"
    placeholder_word = "PLACE" + "HOLDER"
    unfinished = re.compile(rf"\[(?:{unfinished_word}|{placeholder_word}):|{unfinished_word}:")
    private_prefix = "/" + "Users" + "/"
    file_uri = "file" + "://"
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
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
    validate_python(check)
    validate_workflow(check)
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
