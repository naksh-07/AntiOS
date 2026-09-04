"""Unit tests for AntiOS Capability Pack & Progressive Disclosure (Phase 31–33)."""

from __future__ import annotations
import json

from framework.core.capability_pack import CapabilityPack
from framework.core.knowledge import ProgressiveDisclosureEngine, ProgressiveDisclosureLevel


def _sample_pack() -> CapabilityPack:
    return CapabilityPack(
        pack_id="pack-000123",
        project_name="AntiOS-Test",
        task_intent="Change the login button color",
        task_class="FEATURE",
        risk_tier="LOW",
        matched_subsystems=["ui"],
        matched_components=["login-button"],
        workflow={"name": "Feature Implementation Workflow", "id": "workflow:feature"},
        skills=[{"capability_id": "skill:antios-engineer", "name": "Universal Engineer"}],
        rules=[{"capability_id": "rule:core-guard", "name": "Path Guard"}],
        tools=[{"capability_id": "tool:navigate-repo", "name": "Navigate Repo"}],
        verifier={"name": "Maker-Checker Verifier", "metadata": {"verifier_type": "MAKER_CHECKER"}},
        specialists=[{"name": "Core Engineer"}],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED", "justification": "Local tools suffice"},
        why_selected={"subsystem": "Inferred from intent", "workflow": "Governs FEATURE"},
        confidence=0.85,
        epistemic_state="OBSERVED",
        irrelevant_capabilities_filtered=24,
    )


def test_card_line_budget_strict_ceiling():
    pack = _sample_pack()
    card = pack.format_card(max_lines=25)
    lines = card.strip().split("\n")
    assert len(lines) <= 25
    assert "=== ANTIOS CAPABILITY PACK ===" in lines[0]
    assert "Project:      AntiOS-Test" in lines[1]


def test_summary_card_line_budget_strict_ceiling():
    pack = _sample_pack()
    summary = pack.format_summary()
    lines = summary.strip().split("\n")
    assert len(lines) <= 15
    assert "=== ANTIOS CAPABILITY SUMMARY ===" in lines[0]


def test_json_serialization_and_deserialization():
    pack = _sample_pack()
    json_str = pack.to_json()
    data = json.loads(json_str)
    assert data["pack_id"] == "pack-000123"
    assert data["task_class"] == "FEATURE"
    assert data["confidence"] == 0.85

    reconstructed = CapabilityPack.from_dict(data)
    assert reconstructed.pack_id == pack.pack_id
    assert reconstructed.task_intent == pack.task_intent


def test_progressive_disclosure_engine_l4_rendering():
    pack = _sample_pack()
    rendered_l4 = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L4_CAPABILITIES, pack)
    lines = rendered_l4.strip().split("\n")
    assert len(lines) <= 25
    assert "=== ANTIOS CAPABILITY PACK ===" in lines[0]


def test_progressive_disclosure_engine_l5_rendering():
    pack = _sample_pack()
    rendered_l5 = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L5_DETAILED_EVIDENCE, pack)
    data = json.loads(rendered_l5)
    assert data["pack_id"] == "pack-000123"
    assert data["project_name"] == "AntiOS-Test"
