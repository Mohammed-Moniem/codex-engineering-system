from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent


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


if __name__ == "__main__":
    unittest.main()
