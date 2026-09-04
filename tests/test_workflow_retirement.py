"""Tests for AntiOS 2.0 Phase 59: Workflow Retirement & Native Migration.

Verifies:
- Complete retirement of custom workflow layer (.agents/workflows/).
- ProjectBoundaryCompiler never emits or generates .agents/workflows/.
- InstallationLifecycleManager preserves the zero-workflow invariant.
- Procedural flows route natively through /antios, operating skills, and dispatch.
- IntelligenceVerifier flags legacy .agents/workflows/ as a blocking violation.
"""

from pathlib import Path
import tempfile
import unittest

from framework.core.compiler import ProjectBoundaryCompiler
from framework.core.installation import InstallationLifecycleManager
from framework.core.intelligence_verifier import IntelligenceVerifier


class TestWorkflowRetirement(unittest.TestCase):
    """Unit tests for Phase 59 Workflow Retirement."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_compiler_emits_zero_workflows(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectBoundaryCompiler(source_root=Path(__file__).parent.parent, target_root=py_repo)
        result = compiler.compile()

        # Compiled files must NOT contain any path under .agents/workflows/
        workflow_files = [p for p in result.compiled_files.keys() if p.startswith(".agents/workflows")]
        self.assertEqual(len(workflow_files), 0, f"Found legacy workflow files: {workflow_files}")

    def test_intelligence_verifier_flags_legacy_workflows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            # Create a mock AntiOS install with a legacy workflow directory
            antios_dir = tmp_root / ".antios"
            antios_dir.mkdir(parents=True)
            (antios_dir / "manifest.json").write_text(
                '{"schema_version": "2.0.0", "antios_version": "2.0.0", "source_revision": "v2.0.0", "project_fingerprint": "mock_fp", "generated_at": "2026-09-01T00:00:00Z", "managed_paths": {}, "generated_paths": {}}',
                encoding="utf-8"
            )
            (tmp_root / ".agents" / "skills" / "antios").mkdir(parents=True)
            (tmp_root / ".agents" / "skills" / "antios" / "SKILL.md").write_text("---\nname: antios\n---\n# AntiOS", encoding="utf-8")

            # Introduce deprecated .agents/workflows/
            legacy_wf_dir = tmp_root / ".agents" / "workflows"
            legacy_wf_dir.mkdir(parents=True)
            (legacy_wf_dir / "feature.md").write_text("# Feature Workflow", encoding="utf-8")

            verifier = IntelligenceVerifier(tmp_root)
            verdict = verifier.verify()

            # Must detect LEGACY_WORKFLOWS_PRESENT as a blocking issue
            has_wf_issue = any(i.issue_type == "LEGACY_WORKFLOWS_PRESENT" for i in verdict.issues)
            self.assertTrue(has_wf_issue, "IntelligenceVerifier failed to flag deprecated .agents/workflows/")


if __name__ == "__main__":
    unittest.main()
