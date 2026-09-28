import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_FIXTURE = REPO_ROOT / "evals" / "skill-routing.json"
EXPECTED_SKILLS = {
    "app-service-planning",
    "source-analyzer",
    "register-analysis-context",
    "publish-analysis-wiki",
    "implement",
    "plan",
    "refactor",
    "review",
    "github-flow",
}
EXPECTED_KINDS = {"positive", "negative", "confusion"}


class SkillRoutingEvalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(EVAL_FIXTURE.read_text(encoding="utf-8"))["cases"]

    def test_case_ids_are_unique(self):
        case_ids = [case["id"] for case in self.cases]
        self.assertEqual(len(case_ids), len(set(case_ids)))

    def test_every_case_has_required_fields(self):
        for case in self.cases:
            self.assertTrue(case["id"])
            self.assertTrue(case["prompt"])
            self.assertIn(case["kind"], EXPECTED_KINDS)
            self.assertIn(case["expected_skill"], EXPECTED_SKILLS | {None})
            self.assertIsInstance(case["must_not_select"], list)

    def test_every_skill_has_positive_and_confusion_coverage(self):
        for skill_name in EXPECTED_SKILLS:
            positive_cases = [
                case
                for case in self.cases
                if case["expected_skill"] == skill_name and case["kind"] == "positive"
            ]
            confusion_cases = [
                case
                for case in self.cases
                if skill_name in case["must_not_select"] and case["kind"] == "confusion"
            ]

            self.assertGreaterEqual(
                len(positive_cases),
                2,
                msg=f"{skill_name} needs at least two positive cases",
            )
            self.assertGreaterEqual(
                len(confusion_cases),
                1,
                msg=f"{skill_name} needs at least one confusion boundary",
            )


if __name__ == "__main__":
    unittest.main()
