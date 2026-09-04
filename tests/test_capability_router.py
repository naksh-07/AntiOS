"""Unit tests for AntiOS Task-to-Capability Router (Phase 31–33)."""

from __future__ import annotations

from framework.core.capability import MCPStatus
from framework.core.capability_router import CapabilityRouter
from framework.core.lifecycle import TaskClass


def test_classify_task_intent_bug():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent = router.classify_task_intent("Fix crash in authentication timeout")
    assert intent.task_class == TaskClass.BUG
    assert intent.confidence >= 0.7


def test_classify_task_intent_refactor():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent = router.classify_task_intent("Refactor and decouple payment module")
    assert intent.task_class == TaskClass.REFACTOR
    assert intent.confidence >= 0.7


def test_classify_task_intent_documentation():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent = router.classify_task_intent("Update architecture documentation and guide")
    assert intent.task_class == TaskClass.DOCUMENTATION
    assert intent.confidence >= 0.7


def test_classify_task_intent_investigation():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent = router.classify_task_intent("Investigate why memory spikes during large test runs")
    assert intent.task_class == TaskClass.INVESTIGATION
    assert intent.confidence >= 0.7


def test_classify_task_intent_release():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent = router.classify_task_intent("Prepare release version bump and changelog")
    assert intent.task_class == TaskClass.RELEASE
    assert intent.confidence >= 0.7


def test_classify_task_intent_empty_or_gibberish():
    router = CapabilityRouter(project_name="AntiOS-Test")
    intent1 = router.classify_task_intent("")
    assert intent1.is_unknown is True
    assert intent1.confidence == 0.0

    intent2 = router.classify_task_intent("12345 !@#$%")
    assert intent2.is_unknown is True
    assert intent2.confidence == 0.0


def test_mcp_evaluation_useful_browser():
    router = CapabilityRouter(project_name="AntiOS-Test")
    decision = router.evaluate_mcp_justification("Inspect browser DOM layout and a11y tree", ["ui"])
    assert decision.status == MCPStatus.USEFUL
    assert decision.provider_id == "mcp:chrome-devtools"
    assert decision.is_permitted is True


def test_mcp_evaluation_useful_gemini_docs():
    router = CapabilityRouter(project_name="AntiOS-Test")
    decision = router.evaluate_mcp_justification("Search Gemini SDK API documentation", ["core"])
    assert decision.status == MCPStatus.USEFUL
    assert decision.provider_id == "mcp:gemini-api-docs"
    assert decision.is_permitted is True


def test_mcp_evaluation_rejected_provider():
    router = CapabilityRouter(project_name="AntiOS-Test")
    decision = router.evaluate_mcp_justification("Export pages to notion workspace", ["core"])
    assert decision.status == MCPStatus.REJECTED
    assert decision.is_permitted is False


def test_mcp_evaluation_not_needed_for_standard_code():
    router = CapabilityRouter(project_name="AntiOS-Test")
    decision = router.evaluate_mcp_justification("Implement user service function", ["core"])
    assert decision.status == MCPStatus.NOT_NEEDED
    assert decision.is_permitted is False


def test_resolve_capabilities_full_pipeline():
    router = CapabilityRouter(project_name="AntiOS-Test")
    pack = router.resolve_capabilities("Fix crash in sqlite database migration")
    assert pack.task_class == "BUG"
    assert "database" in pack.matched_subsystems
    assert pack.workflow["id"] == "workflow:bug"

    skill_ids = [s["capability_id"] for s in pack.skills]
    assert "skill:antios-engineer" in skill_ids
    assert "skill:antios-debug" in skill_ids

    assert "skill:antios-debug" in pack.why_selected
    assert "workflow" in pack.why_selected
    assert pack.verifier["metadata"]["verifier_type"] == "MAKER_CHECKER"
    assert pack.irrelevant_capabilities_filtered > 0
