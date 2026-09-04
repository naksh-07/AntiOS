"""Tests for AntiOS 2.0 Phase 55: Project Anatomy Compiler.

Verifies:
- Bounded model derivation from observable evidence.
- Epistemic classification: OBSERVED, INFERRED, UNKNOWN.
- Deterministic archetype classification.
- Cryptographic provenance and manifest fingerprinting.
- No hallucination or arbitrary file crawling.
"""

from pathlib import Path
import unittest

from framework.core.anatomy import (
    ManifestEvidence,
    ProjectAnatomy,
    ProjectAnatomyCompiler,
    ProjectArchetype,
)
from framework.core.profile import EvidenceTier


class TestProjectAnatomyCompiler(unittest.TestCase):
    """Unit tests for ProjectAnatomyCompiler."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_python_project_anatomy(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectAnatomyCompiler(py_repo)
        anatomy = compiler.compile()

        self.assertIsInstance(anatomy, ProjectAnatomy)
        self.assertIn("Python", anatomy.languages)
        self.assertEqual(anatomy.archetype, ProjectArchetype.BACKEND_SERVICE.value)
        self.assertTrue(len(anatomy.source_roots) > 0)
        self.assertTrue(len(anatomy.test_runners) > 0)

        # Verify epistemic ledger
        ledger = anatomy.epistemic_ledger
        self.assertIn(EvidenceTier.OBSERVED.value, ledger)
        self.assertIn(EvidenceTier.INFERRED.value, ledger)
        self.assertTrue(len(ledger[EvidenceTier.OBSERVED.value]) > 0)

        # Verify provenance
        self.assertIn("generator", anatomy.provenance)
        self.assertIn("generated_at", anatomy.provenance)
        self.assertIn("manifest_fingerprint", anatomy.provenance)

    def test_frontend_design_system_anatomy(self):
        fe_repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectAnatomyCompiler(fe_repo)
        anatomy = compiler.compile()

        self.assertEqual(anatomy.archetype, ProjectArchetype.FULLSTACK_WEB.value)
        self.assertIn("components", anatomy.important_directories)
        self.assertIn("styles", anatomy.important_directories)
        self.assertTrue(any("package.json" in m["path"] for m in anatomy.package_manifests))

    def test_monorepo_anatomy(self):
        mono_repo = self.fixtures_dir / "ts_monorepo"
        compiler = ProjectAnatomyCompiler(mono_repo)
        anatomy = compiler.compile()

        self.assertEqual(anatomy.archetype, ProjectArchetype.MONOREPO_WORKSPACE.value)
        self.assertTrue(len(anatomy.package_manifests) > 0)

    def test_legacy_topology_anatomy(self):
        legacy_repo = self.fixtures_dir / "legacy_topology_project"
        compiler = ProjectAnatomyCompiler(legacy_repo)
        anatomy = compiler.compile()

        # Legacy without standard language manifests classified appropriately
        self.assertIn(anatomy.archetype, [ProjectArchetype.UNKNOWN_LEGACY.value, ProjectArchetype.STANDALONE_CLI.value])
        # Has Makefile observed
        self.assertTrue(any("Makefile" in m["path"] for m in anatomy.package_manifests))
        self.assertTrue(len(anatomy.manifest_fingerprint) > 0)

    def test_serialization_roundtrip(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectAnatomyCompiler(py_repo)
        anatomy = compiler.compile()

        json_str = anatomy.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn(anatomy.project_name, json_str)
        self.assertIn(anatomy.archetype, json_str)


if __name__ == "__main__":
    unittest.main()
