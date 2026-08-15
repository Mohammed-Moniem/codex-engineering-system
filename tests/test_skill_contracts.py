from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent


def load_validator():
    path = ROOT / "scripts" / "validate_repo.py"
    spec = importlib.util.spec_from_file_location("validate_repo", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load repository validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class SkillContractTests(unittest.TestCase):
    def test_repository_validator(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_repo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_every_skill_has_smoke_prompts(self) -> None:
        skills = {path.name for path in (ROOT / ".agents" / "skills").iterdir() if path.is_dir()}
        fixtures = json.loads((ROOT / "evals" / "skill-smoke.json").read_text(encoding="utf-8"))
        self.assertEqual(skills, {item["skill"] for item in fixtures})
        for item in fixtures:
            with self.subTest(skill=item["skill"]):
                self.assertIn(f"${item['skill']}", item["explicit"])
                self.assertTrue(item["positive"].strip())
                self.assertTrue(item["negative"].strip())

    def test_workflow_policy_rejects_effective_write_and_mutable_actions(self) -> None:
        safe = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        self.assertEqual([], validator.workflow_policy_errors(safe))
        job_override = safe.replace("  validate:\n", "  validate:\n    permissions: write-all\n", 1)
        self.assertTrue(validator.workflow_policy_errors(job_override))
        mutable = safe.replace("actions/checkout@11d5960a326750d5838078e36cf38b85af677262", "actions/checkout@v4")
        self.assertTrue(validator.workflow_policy_errors(mutable))
        alternate_key = safe.replace("uses: actions/checkout", "uses : actions/checkout", 1)
        self.assertTrue(validator.workflow_policy_errors(alternate_key))
        spaced_permission = safe.replace("permissions:", "permissions :", 1)
        self.assertTrue(validator.workflow_policy_errors(spaced_permission))
        quoted_action = safe.replace("uses: actions/checkout", '"uses": actions/checkout', 1)
        self.assertTrue(validator.workflow_policy_errors(quoted_action))

    def test_every_workflow_is_covered_by_policy_validation(self) -> None:
        source = (ROOT / "scripts" / "validate_repo.py").read_text(encoding="utf-8")
        self.assertIn('directory.glob("*.yml")', source)
        self.assertIn('directory.glob("*.yaml")', source)

    def test_distribution_inventory_is_tracked(self) -> None:
        check = validator.Validation()
        validator.validate_distribution_inventory(check)
        self.assertEqual([], check.errors)

    def test_debug_preserves_diagnosis_only_authority(self) -> None:
        text = (ROOT / ".agents" / "skills" / "debug" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("For diagnosis-only requests", text)
        self.assertIn("do not implement a fix", text)


if __name__ == "__main__":
    unittest.main()
