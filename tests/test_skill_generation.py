"""Tests for AntiOS 2.0 Phase 57: Project-Specific Skill Generation.

Verifies:
- Main operating skill (.agents/skills/antios/SKILL.md) bounded to <= 80 lines.
- Evidence-driven specialist skill generation criteria.
- Duplicate avoidance: does not overwrite or duplicate existing user-authored skills.
- Generated skill format adheres to native Antigravity skill structure.
- Concise line budget (< 70 lines).
"""

from pathlib import Path
import unittest

from framework.core.anatomy import ProjectAnatomy, ProjectAnatomyCompiler
from framework.core.skill_generator import SkillGenerator, SkillGenerationSpec


class TestSkillGeneration(unittest.TestCase):
    """Unit tests for SkillGenerator."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_main_skill_compilation_and_boundedness(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectAnatomyCompiler(py_repo)
        anatomy = compiler.compile()

        main_skill = SkillGenerator.compile_main_skill(anatomy)
        self.assertIsInstance(main_skill, str)
        self.assertIn("name: antios", main_skill)
        self.assertIn(anatomy.project_name, main_skill)
        self.assertIn("Tool Tier Preference", main_skill)

        # Check strict <= 80 line budget
        lines = main_skill.splitlines()
        self.assertLessEqual(len(lines), 80)

    def test_evidence_driven_skill_justification(self):
        fe_repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectAnatomyCompiler(fe_repo)
        anatomy = compiler.compile()

        specs = SkillGenerator.evaluate_skill_justification(anatomy)
        self.assertTrue(len(specs) > 0)
        frontend_spec = next((s for s in specs if s.name == "frontend-design"), None)
        self.assertIsNotNone(frontend_spec)
        self.assertIn("components/", frontend_spec.scope)
        self.assertIn("vitest", " ".join(frontend_spec.verification_expectations))

    def test_duplicate_avoidance_with_existing_skills(self):
        fe_repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectAnatomyCompiler(fe_repo)
        anatomy = compiler.compile()

        # If project already has 'frontend-design' or 'design-system', generator must NOT duplicate it
        specs = SkillGenerator.evaluate_skill_justification(
            anatomy, existing_skills=["frontend-design", "antios"]
        )
        self.assertFalse(any(s.name == "frontend-design" for s in specs))

    def test_no_spurious_skill_generation_on_plain_python(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectAnatomyCompiler(py_repo)
        anatomy = compiler.compile()

        specs = SkillGenerator.evaluate_skill_justification(anatomy)
        # Python project without migrations or UI should not produce frontend or db skills
        self.assertFalse(any(s.name == "frontend-design" for s in specs))

    def test_generated_skill_content_structure_and_conciseness(self):
        fe_repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectAnatomyCompiler(fe_repo)
        anatomy = compiler.compile()

        specs = SkillGenerator.evaluate_skill_justification(anatomy)
        self.assertTrue(len(specs) > 0)
        content = SkillGenerator.generate_skill_content(specs[0], anatomy)

        self.assertIn(f"name: {specs[0].name}", content)
        self.assertIn("## 1. Scope & Boundaries", content)
        self.assertIn("## 2. Project Evidence", content)
        self.assertIn("## 4. Allowed Operations", content)
        self.assertIn("## 5. Verification Expectations", content)
        self.assertIn("## 6. Provenance & Lifecycle", content)

        lines = content.splitlines()
        self.assertLessEqual(len(lines), 70)


if __name__ == "__main__":
    unittest.main()
