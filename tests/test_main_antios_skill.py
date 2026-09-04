"""Unit tests for the canonical main AntiOS skill (.agents/skills/antios/SKILL.md)."""

from pathlib import Path
import tempfile
import unittest

from framework.core.compiler import ProjectBoundaryCompiler


class TestMainAntiOSSkill(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.canonical_skill_path = self.repo_root / ".agents" / "skills" / "antios" / "SKILL.md"
        self.template_skill_path = self.repo_root / "framework" / "templates" / "skills" / "antios" / "SKILL.md"

    def test_canonical_skill_exists_and_frontmatter_valid(self):
        self.assertTrue(self.canonical_skill_path.is_file(), f"Missing canonical skill at {self.canonical_skill_path}")
        content = self.canonical_skill_path.read_text(encoding="utf-8")
        
        # Verify YAML frontmatter
        self.assertTrue(content.startswith("---\n"), "Skill must begin with YAML frontmatter delimiter")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "Skill must have valid YAML frontmatter closing delimiter")
        frontmatter = parts[1]
        self.assertIn("name: antios", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_token_budget_line_count_bounded(self):
        content = self.canonical_skill_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        # Strictly bounded <= 80 lines for context-efficient single control plane
        self.assertLessEqual(len(lines), 80, f"Skill exceeds 80-line budget: currently {len(lines)} lines")

    def test_control_plane_canonical_structure(self):
        content = self.canonical_skill_path.read_text(encoding="utf-8")
        
        # Authoritative entrypoint
        self.assertIn("/antios", content)
        
        # Operating axioms
        self.assertIn("Platform (Antigravity)", content)
        self.assertIn("AntiOS Core", content)
        self.assertIn("Project Adapter", content)
        self.assertIn("Target Project", content)
        
        # 9-step pipeline stages
        stages = [
            "UNDERSTAND",
            "CHECK STATE",
            "LOCATE",
            "CLASSIFY",
            "SELECT CAPABILITIES",
            "SELECT WORKFORCE",
            "EXECUTE",
            "VERIFY",
            "REMEMBER",
        ]
        for stage in stages:
            self.assertIn(stage, content, f"Canonical dispatch pipeline missing stage: {stage}")

        # Adaptive workforce modes
        modes = ["SOLO", "FOCUSED", "SMALL", "PARALLEL", "STAGED", "HIERARCHICAL", "MAX"]
        for mode in modes:
            self.assertIn(mode, content, f"Workforce mode missing: {mode}")

        # Constitutional limits
        self.assertIn("Max Active Subagents Per Wave", content)
        self.assertIn("10", content)
        self.assertIn("Max Lifetime Launches Per Mission", content)
        self.assertIn("20", content)
        self.assertIn("Shallow Depth Law", content)
        self.assertIn("Mandatory Wave Collapse", content)

        # Read-parallel, write-controlled
        self.assertIn("Read-Parallel, Write-Controlled", content)
        self.assertIn("Single writer default", content)

        # Specialist skills referenced
        specialists = ["antios-debug", "antios-engineer", "antios-verifier", "antios-adapt-project"]
        for s in specialists:
            self.assertIn(s, content, f"Specialist skill reference missing: {s}")

        # Dispatch helper CLI referenced
        self.assertIn("dispatch_task.py", content)

    def test_template_skill_is_synchronized_with_canonical(self):
        self.assertTrue(self.template_skill_path.is_file(), f"Missing template skill at {self.template_skill_path}")
        canonical_text = self.canonical_skill_path.read_text(encoding="utf-8").strip()
        template_text = self.template_skill_path.read_text(encoding="utf-8").strip()
        self.assertEqual(canonical_text, template_text, "Template skill is not synchronized with canonical skill")

    def test_boundary_compiler_compiles_main_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            (target_root / "pyproject.toml").write_text("[project]\nname = 'target'\n", encoding="utf-8")
            
            compiler = ProjectBoundaryCompiler(
                source_root=self.repo_root,
                target_root=target_root,
                source_revision="v2.0.0-test",
            )
            result = compiler.compile()
            self.assertTrue(result.success)
            self.assertIn(".agents/skills/antios/SKILL.md", result.compiled_files)

            success, written, errors = compiler.emit(result)
            self.assertTrue(success, f"Emit failed: {errors}")
            self.assertIn(".agents/skills/antios/SKILL.md", written)

            compiled_skill = target_root / ".agents" / "skills" / "antios" / "SKILL.md"
            self.assertTrue(compiled_skill.is_file())
            self.assertEqual(
                compiled_skill.read_text(encoding="utf-8").strip(),
                self.canonical_skill_path.read_text(encoding="utf-8").strip(),
            )


if __name__ == "__main__":
    unittest.main()
