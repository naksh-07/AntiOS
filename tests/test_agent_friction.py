"""Tests for Phase 74 Agent Friction Detection Engine."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.agent_friction import (
    AgentFrictionDetector,
    AgentFrictionReport,
    FrictionCategory,
    FrictionClassification,
    FrictionSeverity,
)


class TestAgentFriction(unittest.TestCase):
    """Test suite for AgentFrictionDetector."""

    def test_clean_workspace_false_positive_control(self):
        """Current repository contains zero critical friction findings."""
        report = AgentFrictionDetector.detect_frictions(".")
        self.assertIsInstance(report, AgentFrictionReport)
        self.assertEqual(report.by_severity["CRITICAL"], 0)

    def test_legacy_workflow_friction_detection(self):
        """Detects legacy .agents/workflows/ as CRITICAL friction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wf_dir = Path(tmpdir) / ".agents" / "workflows"
            wf_dir.mkdir(parents=True)
            (wf_dir / "legacy_step.md").write_text("step", encoding="utf-8")

            report = AgentFrictionDetector.detect_frictions(tmpdir)
            wf_findings = [f for f in report.findings if f.category == FrictionCategory.CONFLICTING_INSTRUCTIONS]
            self.assertTrue(len(wf_findings) > 0)
            self.assertEqual(wf_findings[0].severity, FrictionSeverity.CRITICAL)

    def test_unnecessary_mcp_escalation_detection(self):
        """Detects git MCP escalation when Tier 4 CLI is standard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "antios.config.json"
            cfg.write_text(json.dumps({"mcp_servers": {"github": {"command": "npx"}}}), encoding="utf-8")

            report = AgentFrictionDetector.detect_frictions(tmpdir)
            mcp_findings = [f for f in report.findings if f.category == FrictionCategory.UNNECESSARY_MCP_ESCALATION]
            self.assertTrue(len(mcp_findings) > 0)
            self.assertEqual(mcp_findings[0].severity, FrictionSeverity.MEDIUM)

    def test_ambiguous_ownership_detection_without_manifest(self):
        """Detects missing .antios/manifest.json as AMBIGUOUS_OWNERSHIP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = AgentFrictionDetector.detect_frictions(tmpdir)
            own_findings = [f for f in report.findings if f.category == FrictionCategory.AMBIGUOUS_OWNERSHIP]
            self.assertTrue(len(own_findings) > 0)
            self.assertEqual(own_findings[0].classification, FrictionClassification.OBSERVED_FRICTION)

    def test_duplicate_skills_detection(self):
        """Detects skills with heavily overlapping descriptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = Path(tmpdir) / ".agents" / "skills" / "skill_alpha"
            s2 = Path(tmpdir) / ".agents" / "skills" / "skill_beta"
            s1.mkdir(parents=True)
            s2.mkdir(parents=True)

            desc = "Automate unit tests for python modules and verify coverage thoroughly."
            (s1 / "SKILL.md").write_text(f"---\nname: skill_alpha\ndescription: {desc}\n---\nBody", encoding="utf-8")
            (s2 / "SKILL.md").write_text(f"---\nname: skill_beta\ndescription: {desc}\n---\nBody", encoding="utf-8")

            report = AgentFrictionDetector.detect_frictions(tmpdir)
            dup_findings = [f for f in report.findings if f.category == FrictionCategory.DUPLICATE_SKILLS]
            self.assertTrue(len(dup_findings) > 0)
            self.assertIn("skill_alpha", dup_findings[0].affected_paths[0])


if __name__ == "__main__":
    unittest.main()
