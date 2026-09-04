"""Tests for AntiOS 2.0 Phase 67: Two-Way Adaptation Contract."""

from __future__ import annotations
import unittest

from framework.core.two_way_contract import (
    AdaptationSignal,
    AdaptationTier,
    AuthorityTier,
    EpistemicForm,
    SignalType,
    TransitionGateResult,
    TransitionGateVerdict,
    TwoWayAdaptationContract,
)


class TestTwoWayAdaptationContract(unittest.TestCase):
    """Unit tests for the Two-Way Adaptation Contract and Transition Gate."""

    def test_signal_creation_and_deterministic_hash(self):
        """Test creating an AdaptationSignal via helper and verifying hash computation."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.CAPABILITY_GAP,
            epistemic_form=EpistemicForm.OBSERVATION,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"issue": "missing_linter", "exit_code": 127},
            confidence=0.85,
            provenance="task_runner",
            risk="LOW",
        )
        self.assertTrue(sig.signal_id.startswith("sig-cap-"))
        self.assertIsNotNone(sig.signal_hash)
        self.assertEqual(len(sig.signal_hash), 64)
        self.assertEqual(sig.confidence, 0.85)

    def test_signal_dict_roundtrip(self):
        """Test serialization and deserialization of AdaptationSignal."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.TOOL_GAP,
            epistemic_form=EpistemicForm.INFERENCE,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"tool": "mvn", "supported": False},
            confidence=0.75,
            provenance="discovery_engine",
            risk="MEDIUM",
        )
        d = sig.to_dict()
        self.assertEqual(d["signal_type"], "TOOL_GAP")
        self.assertEqual(d["epistemic_form"], "INFERENCE")
        self.assertEqual(d["source_tier"], "TARGET_PROJECT")

        restored = AdaptationSignal.from_dict(d)
        self.assertEqual(restored.signal_id, sig.signal_id)
        self.assertEqual(restored.signal_hash, sig.signal_hash)
        self.assertEqual(restored.evidence_payload, sig.evidence_payload)

    def test_confidence_clamping(self):
        """Test that signal confidence is clamped between 0.0 and 1.0."""
        sig_low = AdaptationSignal(
            signal_id="sig-test-low",
            signal_type=SignalType.PROJECT_OBSERVATION,
            epistemic_form=EpistemicForm.OBSERVATION,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={},
            confidence=-0.5,
            provenance="test",
        )
        self.assertEqual(sig_low.confidence, 0.0)

        sig_high = AdaptationSignal(
            signal_id="sig-test-high",
            signal_type=SignalType.PROJECT_OBSERVATION,
            epistemic_form=EpistemicForm.OBSERVATION,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={},
            confidence=1.5,
            provenance="test",
        )
        self.assertEqual(sig_high.confidence, 1.0)

    def test_allowed_legal_transition(self):
        """Test an allowed transition within project-local boundaries."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.PROJECT_OBSERVATION,
            epistemic_form=EpistemicForm.OBSERVATION,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"observation": "build passes"},
            confidence=0.9,
            provenance="test_runner",
        )
        res = TwoWayAdaptationContract.evaluate_transition(
            signal=sig,
            proposed_action_target=".antios/observations.json",
        )
        self.assertEqual(res.verdict, TransitionGateVerdict.ALLOWED)
        self.assertTrue(res.is_allowed)
        self.assertEqual(len(res.violations), 0)

    def test_core_immutability_violation_rejected(self):
        """Test that mutations targeting protected core assets are strictly denied."""
        forbidden_targets = [
            "framework/core/guard.py",
            "framework/core/installation.py",
            "antios_constitution.md",
            "ANTIOS_CONSTITUTION.md",
            "antios_source_of_truth.md",
            ".agents/hooks.json",
            ".git/config",
        ]
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.EVOLUTION_PROPOSAL,
            epistemic_form=EpistemicForm.PROPOSAL,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.HUMAN_DIRECTIVE,
            evidence_payload={"intent": "modify core"},
            confidence=1.0,
            provenance="agent",
        )
        for target in forbidden_targets:
            res = TwoWayAdaptationContract.evaluate_transition(
                signal=sig,
                proposed_action_target=target,
            )
            self.assertEqual(res.verdict, TransitionGateVerdict.DENIED, f"Target '{target}' must be denied")
            self.assertFalse(res.is_allowed)
            self.assertTrue(any("Core Immutability" in v for v in res.violations))
            self.assertEqual(res.escalation_target, "HUMAN_GOVERNANCE")

    def test_upstream_source_read_only_escalation(self):
        """Test that signals targeting ANTIOS_SOURCE without file writes are routed as read-only RFCs."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.CAPABILITY_GAP,
            epistemic_form=EpistemicForm.INFERENCE,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.ANTIOS_SOURCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"suggestion": "Support Zig toolchain natively"},
            confidence=0.8,
            provenance="gap_detector",
        )
        res = TwoWayAdaptationContract.evaluate_transition(signal=sig, proposed_action_target=None)
        self.assertEqual(res.verdict, TransitionGateVerdict.ESCALATION_REQUIRED)
        self.assertTrue(res.is_allowed)
        self.assertEqual(res.escalation_target, "UPSTREAM_FRAMEWORK_MAINTAINERS")

    def test_upstream_source_direct_write_denied(self):
        """Test that attempting direct writes into ANTIOS_SOURCE from target project is denied."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.EVOLUTION_PROPOSAL,
            epistemic_form=EpistemicForm.APPROVED_CHANGE,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.ANTIOS_SOURCE,
            authority_level=AuthorityTier.HUMAN_DIRECTIVE,
            evidence_payload={"change": "patch core"},
            confidence=1.0,
            provenance="maintainer",
        )
        res = TwoWayAdaptationContract.evaluate_transition(
            signal=sig,
            proposed_action_target="framework/core/compiler.py",
        )
        self.assertEqual(res.verdict, TransitionGateVerdict.DENIED)
        self.assertFalse(res.is_allowed)

    def test_epistemic_agent_inference_weight_ceiling(self):
        """Test that AGENT_INFERENCE confidence cannot exceed 0.4."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.CAPABILITY_GAP,
            epistemic_form=EpistemicForm.INFERENCE,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.AGENT_INFERENCE,
            evidence_payload={"belief": "we might need rust"},
            confidence=0.9,  # Illegally high confidence for mere agent inference
            provenance="agent_reasoning",
        )
        res = TwoWayAdaptationContract.evaluate_transition(signal=sig)
        self.assertEqual(res.verdict, TransitionGateVerdict.DENIED)
        self.assertTrue(any("Epistemic Weight Violation" in v for v in res.violations))

    def test_epistemic_agent_inference_cannot_approve_change(self):
        """Test that AGENT_INFERENCE alone cannot produce APPROVED_CHANGE."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.EVOLUTION_PROPOSAL,
            epistemic_form=EpistemicForm.APPROVED_CHANGE,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.AGENT_INFERENCE,
            evidence_payload={},
            confidence=0.3,
            provenance="agent_self_action",
        )
        res = TwoWayAdaptationContract.evaluate_transition(signal=sig)
        self.assertEqual(res.verdict, TransitionGateVerdict.DENIED)
        self.assertTrue(any("Epistemic Boundary Violation" in v for v in res.violations))

    def test_shallow_depth_law_delegation_prohibited(self):
        """Test that proposals attempting can_delegate=True are rejected under Shallow Depth Law."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.EVOLUTION_PROPOSAL,
            epistemic_form=EpistemicForm.PROPOSAL,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"specialist": "deep_orchestrator", "can_delegate": True},
            confidence=0.8,
            provenance="agent_proposal",
        )
        res = TwoWayAdaptationContract.evaluate_transition(signal=sig)
        self.assertEqual(res.verdict, TransitionGateVerdict.DENIED)
        self.assertTrue(any("Shallow Depth Law Violation" in v for v in res.violations))

    def test_mcp_gap_bypass_justification_prohibited(self):
        """Test that MCP escalation attempting bypass_justification is rejected."""
        sig = TwoWayAdaptationContract.create_signal(
            signal_type=SignalType.MCP_GAP,
            epistemic_form=EpistemicForm.PROPOSAL,
            source_tier=AdaptationTier.TARGET_PROJECT,
            target_tier=AdaptationTier.PROJECT_INSTANCE,
            authority_level=AuthorityTier.PROJECT_LOCAL,
            evidence_payload={"mcp": "custom-mcp", "bypass_justification": True},
            confidence=0.7,
            provenance="agent",
        )
        res = TwoWayAdaptationContract.evaluate_transition(signal=sig)
        self.assertEqual(res.verdict, TransitionGateVerdict.DENIED)
        self.assertTrue(any("Tool Authority Violation" in v for v in res.violations))


if __name__ == "__main__":
    unittest.main()
