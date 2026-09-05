#!/usr/bin/env python3
"""Tests for the 8-Tier Hybrid Capability Execution Matrix under Phase 86."""

import unittest
from framework.core.tool import HybridCapabilityTier
from framework.core.tool_registry import ToolRegistry
from framework.core.tool_policy import (
    HybridCapabilityExecutionMatrix,
    HybridResolutionResult,
    MCPJustificationReport,
    MCPJustificationEngine,
)


class TestHybridCapabilityMatrix(unittest.TestCase):
    """Test suite for HybridCapabilityExecutionMatrix and MCP Justification Protocol."""

    def setUp(self):
        self.matrix = HybridCapabilityExecutionMatrix()

    def test_tier_enum_ordering(self):
        """Verify the 8 tiers are numbered and ordered 1 through 8."""
        self.assertEqual(HybridCapabilityTier.TIER_1_NATIVE_BUILTIN.value, 1)
        self.assertEqual(HybridCapabilityTier.TIER_2_PROJECT_NATIVE_SKILL.value, 2)
        self.assertEqual(HybridCapabilityTier.TIER_3_PROJECT_TOOL_SCRIPT.value, 3)
        self.assertEqual(HybridCapabilityTier.TIER_4_ANTIOS_CORE_RUNTIME.value, 4)
        self.assertEqual(HybridCapabilityTier.TIER_5_SPECIALIST_AGENT.value, 5)
        self.assertEqual(HybridCapabilityTier.TIER_6_STANDARD_CLI.value, 6)
        self.assertEqual(HybridCapabilityTier.TIER_7_EXTERNAL_SERVICE.value, 7)
        self.assertEqual(HybridCapabilityTier.TIER_8_MANAGED_MCP.value, 8)
        self.assertEqual(len(HybridCapabilityTier), 8)

    def test_tier_1_native_builtin_resolution(self):
        """Verify Tier 1 native tools are selected first and authorized."""
        for tool_name in ["view_file", "write_to_file", "grep_search", "find_by_name", "run_command"]:
            res = self.matrix.resolve(capability_sought=tool_name)
            self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_1_NATIVE_BUILTIN)
            self.assertTrue(res.is_authorized)
            self.assertFalse(res.requires_approval)
            self.assertIn("native:", res.target_identifier)

    def test_tier_2_project_native_skill_resolution(self):
        """Verify Tier 2 project-native skills are selected when requested."""
        for skill_name in ["antios-engineer", "antios-debug", "antios-verifier", "antios-adapt-project"]:
            res = self.matrix.resolve(capability_sought=skill_name)
            self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_2_PROJECT_NATIVE_SKILL)
            self.assertTrue(res.is_authorized)
            self.assertEqual(res.target_identifier, f"skill:{skill_name}")

    def test_tier_3_project_tool_script_resolution(self):
        """Verify Tier 3 project tools/scripts are selected over runtime/specialists."""
        res = self.matrix.resolve(capability_sought="run tests with tests/run_all.py")
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_3_PROJECT_TOOL_SCRIPT)
        self.assertTrue(res.is_authorized)
        self.assertEqual(res.target_identifier, "script:tests/run_all.py")

    def test_tier_4_antios_core_runtime_resolution(self):
        """Verify Tier 4 AntiOS core runtime services are selected."""
        for svc in ["wayfinder", "stop_gate", "runtime_closure", "workforce_planner"]:
            res = self.matrix.resolve(capability_sought=svc)
            self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_4_ANTIOS_CORE_RUNTIME)
            self.assertTrue(res.is_authorized)
            self.assertEqual(res.target_identifier, f"runtime:{svc}")

    def test_tier_5_specialist_agent_resolution(self):
        """Verify Tier 5 specialist agents are resolved when requested."""
        res = self.matrix.resolve(capability_sought="agent:research")
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_5_SPECIALIST_AGENT)
        self.assertTrue(res.is_authorized)
        self.assertEqual(res.target_identifier, "specialist:research")

    def test_tier_6_standard_cli_resolution(self):
        """Verify Tier 6 standard CLI execution (git, python, npm, cargo)."""
        res = self.matrix.resolve(capability_sought="cli:git")
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_6_STANDARD_CLI)
        self.assertTrue(res.is_authorized)
        self.assertEqual(res.target_identifier, "cli:git")

    def test_tier_7_external_service_requires_approval(self):
        """Verify Tier 7 external services require user approval and reject if missing."""
        # Without user approval
        res_no_appr = self.matrix.resolve(capability_sought="cloud_storage", context={"user_approval_granted": False})
        self.assertEqual(res_no_appr.resolved_tier, HybridCapabilityTier.TIER_7_EXTERNAL_SERVICE)
        self.assertFalse(res_no_appr.is_authorized)
        self.assertTrue(res_no_appr.requires_approval)
        self.assertIn("requires user approval", res_no_appr.rejection_reason)

        # With user approval
        res_appr = self.matrix.resolve(capability_sought="cloud_storage", context={"user_approval_granted": True})
        self.assertEqual(res_appr.resolved_tier, HybridCapabilityTier.TIER_7_EXTERNAL_SERVICE)
        self.assertTrue(res_appr.is_authorized)
        self.assertTrue(res_appr.requires_approval)
        self.assertIsNone(res_appr.rejection_reason)

    def test_tier_8_local_git_strictly_preferred_over_github_mcp(self):
        """Strict Enforcement: Local Git CLI must be chosen over GitHub MCP for local operations."""
        # 1. Direct local git request resolves to Tier 6 Local CLI
        res_cli = self.matrix.resolve(capability_sought="cli:git", task_intent="check git status")
        self.assertEqual(res_cli.resolved_tier, HybridCapabilityTier.TIER_6_STANDARD_CLI)
        self.assertTrue(res_cli.is_authorized)

        # 2. Attempting to use GitHub MCP for local git operations is strictly rejected
        res_mcp = self.matrix.resolve(
            capability_sought="mcp:github",
            task_intent="check git status and diff"
        )
        self.assertEqual(res_mcp.resolved_tier, HybridCapabilityTier.TIER_8_MANAGED_MCP)
        self.assertFalse(res_mcp.is_authorized)
        self.assertIsNotNone(res_mcp.justification_report)
        self.assertIn("Local Git CLI is authoritative", res_mcp.justification_report.why)
        self.assertEqual(res_mcp.justification_report.status, "NOT_NEEDED")

    def test_tier_8_mcp_escalation_protocol_seven_fields(self):
        """Verify 7 mandatory fields are validated on MCP escalation reports."""
        valid_report = MCPJustificationReport(
            provider_id="provider:github",
            status="OPTIONAL",
            is_needed=True,
            is_permitted=True,
            why="Creating remote GitHub PR",
            local_alternatives=["tool:native-git-cli"],
            why_insufficient="Local Git cannot open PR on github.com",
            fallback="NONE",
            on_unavailable="FAIL_CLOSED",
            capability_sought="create_pull_request",
            why_native_failed="No local git endpoint exists for github PR creation",
            least_privilege_scope=["create_pull_request"],
            risk_assessment="LOW: authenticated PR creation",
            rollback_plan="Close PR if incorrect",
            user_approval_required=False,
            audit_trail_entry={"action": "create_pr", "timestamp": "2026-09-05"},
        )
        is_valid, errs = valid_report.validate_escalation_audit()
        self.assertTrue(is_valid)
        self.assertEqual(len(errs), 0)

        # Incomplete report missing fields
        incomplete_report = MCPJustificationReport(
            provider_id="provider:github",
            status="OPTIONAL",
            is_needed=True,
            is_permitted=True,
            why="Creating PR",
            local_alternatives=[],
            why_insufficient="",
            fallback="NONE",
            on_unavailable="FAIL_CLOSED",
            capability_sought="",  # Missing field 1
            why_native_failed="",  # Missing field 2
            least_privilege_scope=[],  # Missing field 3
            risk_assessment="",  # Missing field 4
            rollback_plan="",  # Missing field 5
            user_approval_required=False,
            audit_trail_entry={},  # Missing field 7
        )
        is_valid, errs = incomplete_report.validate_escalation_audit()
        self.assertFalse(is_valid)
        self.assertGreaterEqual(len(errs), 5)

    def test_tier_8_rejected_provider_fails_closed(self):
        """Verify forbidden/unauthorized MCPs (e.g. PostHog or unauthorized) fail closed."""
        res = self.matrix.resolve(
            capability_sought="unauthorized-external-mcp",
            task_intent="connect to unauthorized external mcp"
        )
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_8_MANAGED_MCP)
        self.assertFalse(res.is_authorized)
        self.assertIn("REJECTED", res.rejection_reason)

    def test_evaluate_full_outputs_all_tiers(self):
        """Verify evaluate_full provides a comprehensive 8-tier audit dossier."""
        dossier = self.matrix.evaluate_full(capability_sought="view_file", task_intent="read source code")
        self.assertEqual(dossier["resolved_tier"], 1)
        self.assertEqual(dossier["tier_name"], "Native Antigravity Built-in Tool")
        self.assertTrue(dossier["is_authorized"])
        self.assertEqual(len(dossier["tier_evaluations"]), 8)
        selected_tiers = [t for t in dossier["tier_evaluations"] if t["selected"]]
        self.assertEqual(len(selected_tiers), 1)
        self.assertEqual(selected_tiers[0]["tier_number"], 1)


if __name__ == "__main__":
    unittest.main()
