"""Tests for AntiOS 2.0 Phase 69: Tool & MCP Gap Analysis Engine."""

from __future__ import annotations
import unittest

from framework.core.capability_gap import CapabilityGap, GapClassification
from framework.core.tool_gap import (
    ToolAlternativeEvaluation,
    ToolEscalationTier,
    ToolGapAnalyzer,
    ToolGapReport,
)


class TestToolMCPGapAnalysis(unittest.TestCase):
    """Unit tests for the 6-tier Tool Escalation and MCP Gap Analyzer."""

    def setUp(self):
        self.analyzer = ToolGapAnalyzer()

    def test_escalation_tier_ordering(self):
        """Verify strict ordering of the 6 escalation tiers."""
        self.assertLess(ToolEscalationTier.TIER_1_NATIVE, ToolEscalationTier.TIER_2_LOCAL_SCRIPT)
        self.assertLess(ToolEscalationTier.TIER_2_LOCAL_SCRIPT, ToolEscalationTier.TIER_3_PROJECT_TOOL)
        self.assertLess(ToolEscalationTier.TIER_3_PROJECT_TOOL, ToolEscalationTier.TIER_4_STANDARD_CLI)
        self.assertLess(ToolEscalationTier.TIER_4_STANDARD_CLI, ToolEscalationTier.TIER_5_EXTERNAL_SERVICE)
        self.assertLess(ToolEscalationTier.TIER_5_EXTERNAL_SERVICE, ToolEscalationTier.TIER_6_MCP)

    def test_report_serialization(self):
        """Test ToolGapReport serialization to dict."""
        alt = ToolAlternativeEvaluation(
            tier=ToolEscalationTier.TIER_1_NATIVE,
            tier_name="NATIVE",
            candidates_considered=["grep_search"],
            is_viable=True,
            rejection_reason=None,
            estimated_cost="ZERO",
            estimated_latency_ms=5,
            requires_network=False,
            security_risk="MINIMAL",
        )
        report = ToolGapReport(
            gap_id="gap-001",
            required_capability_id="search_code",
            task_intent="grep for functions",
            deficit_type="RESOLVED_LOCAL_TIER",
            lowest_viable_tier=ToolEscalationTier.TIER_1_NATIVE,
            recommended_tool_id="tool:antigravity-native",
            alternatives_evaluated=[alt],
            rejected_alternatives={},
            escalation_justified=False,
            escalation_reason="Resolved locally",
            security_boundaries_respected=True,
        )
        d = report.to_dict()
        self.assertEqual(d["gap_id"], "gap-001")
        self.assertEqual(d["lowest_viable_tier"], 1)
        self.assertEqual(len(d["alternatives_evaluated"]), 1)
        self.assertFalse(d["escalation_justified"])

    def test_tier_1_native_preferred_for_reading_and_search(self):
        """File inspection or search tasks must resolve to Tier 1 Native."""
        report = self.analyzer.analyze_tool_deficit(
            capability_id="view_source",
            task_intent="view and inspect file contents",
        )
        self.assertEqual(report.lowest_viable_tier, ToolEscalationTier.TIER_1_NATIVE)
        self.assertEqual(report.recommended_tool_id, "tool:antigravity-native")
        self.assertEqual(report.deficit_type, "RESOLVED_LOCAL_TIER")
        self.assertFalse(report.escalation_justified)

    def test_tier_2_local_script_preferred_for_wayfinding_and_audits(self):
        """Wayfinding and doc audits resolve to Tier 2 Local Script."""
        report = self.analyzer.analyze_tool_deficit(
            capability_id="audit_documentation",
            task_intent="run doc audit to find broken links",
        )
        self.assertEqual(report.lowest_viable_tier, ToolEscalationTier.TIER_2_LOCAL_SCRIPT)
        self.assertEqual(report.recommended_tool_id, "tool:antios-script")
        self.assertFalse(report.escalation_justified)

    def test_tier_3_project_tool_preferred_for_testing(self):
        """Unit test execution resolves to Tier 3 Project Tool."""
        report = self.analyzer.analyze_tool_deficit(
            capability_id="run_tests",
            task_intent="run pytest test suite for project",
        )
        self.assertEqual(report.lowest_viable_tier, ToolEscalationTier.TIER_3_PROJECT_TOOL)
        self.assertEqual(report.recommended_tool_id, "tool:project-runner")
        self.assertFalse(report.escalation_justified)

    def test_tier_4_cli_preferred_over_github_mcp(self):
        """Local Git CLI must strictly outrank remote GitHub MCP."""
        report = self.analyzer.analyze_tool_deficit(
            capability_id="git_operations",
            task_intent="git commit and create branch",
        )
        self.assertEqual(report.lowest_viable_tier, ToolEscalationTier.TIER_4_STANDARD_CLI)
        self.assertEqual(report.recommended_tool_id, "tool:native-git-cli")
        self.assertIn("provider:github-mcp", report.rejected_alternatives)
        self.assertIn("local git CLI rather than remote GitHub MCP", report.rejected_alternatives["provider:github-mcp"])
        self.assertFalse(report.escalation_justified)

    def test_unauthorized_mcps_rejected(self):
        """Prohibited MCP providers (Notion, Postman, PostHog) are rejected."""
        prohibited_intents = [
            ("notion_doc", "create a page in notion"),
            ("postman_test", "run postman collection"),
            ("posthog_analytics", "query posthog analytics"),
        ]
        for cap_id, intent in prohibited_intents:
            report = self.analyzer.analyze_tool_deficit(capability_id=cap_id, task_intent=intent)
            self.assertFalse(report.escalation_justified)
            # MCP justification should reject it
            mcp_eval = [e for e in report.alternatives_evaluated if e.tier == ToolEscalationTier.TIER_6_MCP][0]
            self.assertFalse(mcp_eval.is_viable)

    def test_offline_mode_prohibits_mcp(self):
        """Offline mode prevents any MCP escalation even if needed."""
        report = self.analyzer.analyze_tool_deficit(
            capability_id="browser_automation",
            task_intent="run playwright browser tests",
            offline_mode=True,
        )
        mcp_eval = [e for e in report.alternatives_evaluated if e.tier == ToolEscalationTier.TIER_6_MCP][0]
        self.assertFalse(mcp_eval.is_viable)
        self.assertFalse(report.escalation_justified)


if __name__ == "__main__":
    unittest.main()
