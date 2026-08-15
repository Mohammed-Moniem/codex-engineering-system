from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


router = load_module("evaluate_router", ROOT / "scripts" / "evaluate_router.py")


class RouterTests(unittest.TestCase):
    def test_all_contract_cases(self) -> None:
        cases = json.loads((ROOT / "evals" / "router-cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["expected_route"], router.route(case["prompt"]))

    def test_planning_depth_boundaries(self) -> None:
        self.assertNotEqual("wayfinder", router.route("Fix this typo in one string."))
        self.assertEqual("plan", router.route("Add saved searches with persistence and tests."))
        self.assertEqual("wayfinder", router.route("A foggy multi-session effort across several systems."))

    def test_route_is_deterministic(self) -> None:
        prompt = "Review this branch against the ticket."
        self.assertEqual(router.route(prompt), router.route(prompt))


if __name__ == "__main__":
    unittest.main()
