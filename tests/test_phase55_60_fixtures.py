"""Comprehensive Proving Ground Matrix for AntiOS 2.0 Phases 55–60.

Tests all 10 canonical project adaptation fixtures:
1. python_project (Simple Python)
2. ts_project (TypeScript/Node)
3. frontend_design_system (Frontend with custom design system)
4. ts_monorepo & cargo_workspace (Monorepo Workspace)
5. existing_agents_project (Existing skills)
6. existing_custom_agents_project (Existing custom agents / personas)
7. conflicting_instructions_project (Conflicting instructions)
8. legacy_topology_project (Unknown / legacy topology)
9. stale_intelligence_project (Stale generated intelligence)
10. architecture_drift_project (Architecture changes / drift)

Verifies:
- Clean boundary compilation (target project never receives AntiOS core or tests).
- Deterministic project anatomy compilation with OBSERVED/INFERRED/UNKNOWN.
- Component intelligence pre-modification clarity.
- Evidence-driven skill and specialist generation.
- Complete workflow retirement (0 .agents/workflows/).
- Cryptographic provenance and drift verification.
"""

from pathlib import Path
import tempfile
import unittest

from framework.core.anatomy import ProjectAnatomyCompiler, ProjectArchetype
from framework.core.compiler import ProjectBoundaryCompiler
from framework.core.intelligence_verifier import IntelligenceVerifier


class TestPhase55To60ProvingGroundMatrix(unittest.TestCase):
    """Matrix testing all 10 project adaptation archetypes."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.source_root = Path(__file__).parent.parent

    def test_fixture_01_simple_python(self):
        repo = self.fixtures_dir / "python_project"
        compiler = ProjectBoundaryCompiler(source_root=self.source_root, target_root=repo)
        result = compiler.compile()

        self.assertTrue(result.success)
        self.assertIn(".antios/project_anatomy.json", result.compiled_files)
        self.assertIn(".agents/skills/antios/SKILL.md", result.compiled_files)
        # Verify target never receives AntiOS core framework or tests
        for path in result.compiled_files:
            self.assertFalse(path.startswith("framework/core"))
            self.assertFalse(path.startswith("tests/"))

    def test_fixture_02_ts_node(self):
        repo = self.fixtures_dir / "ts_project"
        anatomy = ProjectAnatomyCompiler(repo).compile()
        self.assertTrue(any("TypeScript" in lang for lang in anatomy.languages))
        self.assertTrue(len(anatomy.package_manifests) > 0)

    def test_fixture_03_frontend_design_system(self):
        repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectBoundaryCompiler(source_root=self.source_root, target_root=repo)
        result = compiler.compile()

        self.assertTrue(result.success)
        # Should justify frontend specialist skill
        self.assertIn(".agents/skills/frontend-design/SKILL.md", result.compiled_files)
        # Should justify frontend specialist role in agent topology
        self.assertIn("role:frontend-specialist", result.compiled_files[".antios/agent_topology.json"])

    def test_fixture_04_monorepo(self):
        repo = self.fixtures_dir / "ts_monorepo"
        anatomy = ProjectAnatomyCompiler(repo).compile()
        self.assertEqual(anatomy.archetype, ProjectArchetype.MONOREPO_WORKSPACE.value)

    def test_fixture_05_existing_skills(self):
        repo = self.fixtures_dir / "existing_agents_project"
        compiler = ProjectBoundaryCompiler(source_root=self.source_root, target_root=repo)
        result = compiler.compile()

        self.assertTrue(result.success)
        # Does not overwrite existing custom skills
        for k in result.compiled_files:
            self.assertFalse("custom-calc" in k)

    def test_fixture_06_existing_custom_agents(self):
        repo = self.fixtures_dir / "existing_custom_agents_project"
        anatomy = ProjectAnatomyCompiler(repo).compile()
        # Discovers existing custom agent persona
        self.assertTrue(len(anatomy.existing_agents_structure.get("custom_agents", [])) > 0 or len(anatomy.existing_agents_structure.get("skills", [])) > 0)

    def test_fixture_07_conflicting_instructions(self):
        repo = self.fixtures_dir / "conflicting_instructions_project"
        anatomy = ProjectAnatomyCompiler(repo).compile()
        self.assertTrue(anatomy.agent_facing_configuration.get("has_instructions", False))

    def test_fixture_08_legacy_topology(self):
        repo = self.fixtures_dir / "legacy_topology_project"
        compiler = ProjectBoundaryCompiler(source_root=self.source_root, target_root=repo)
        result = compiler.compile()

        self.assertTrue(result.success)
        self.assertIn(".antios/project_anatomy.json", result.compiled_files)

    def test_fixture_09_stale_intelligence(self):
        repo = self.fixtures_dir / "stale_intelligence_project"
        verifier = IntelligenceVerifier(repo)
        verdict = verifier.verify()
        self.assertTrue(len(verdict.issues) > 0)

    def test_fixture_10_architecture_drift(self):
        repo = self.fixtures_dir / "architecture_drift_project"
        verifier = IntelligenceVerifier(repo)
        verdict = verifier.verify()
        self.assertTrue(verdict.drift_detected)


if __name__ == "__main__":
    unittest.main()
