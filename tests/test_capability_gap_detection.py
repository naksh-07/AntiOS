"""Tests for AntiOS 2.0 Phase 68: Capability Gap Detection & Lifecycle."""

from __future__ import annotations
import unittest

from framework.core.capability_gap import (
    CapabilityGap,
    CapabilityGapDetector,
    GapClassification,
    GapLifecycleEngine,
    GapStatus,
)


class TestCapabilityGapDetection(unittest.TestCase):
    """Unit tests for Capability Gap Detection, Classification, and Lifecycle."""

    def test_capability_gap_serialization(self):
        """Test CapabilityGap serialization and roundtrip deserialization."""
        gap = CapabilityGap(
            gap_id="gap-comp-12345678",
            task_signature="sig-abc-123",
            required_capability="rust_compiler",
            current_capabilities=["python_runtime", "bash_runner"],
            evidence={"exit_code": 127, "cmd": "cargo build"},
            confidence=0.9,
            affected_subsystem="compiler",
            risk="HIGH",
            recommended_next_analysis="Evaluate local cargo binary vs container runner",
            status=GapStatus.DETECTED,
            classification=GapClassification.MISSING_CAPABILITY,
        )
        d = gap.to_dict()
        self.assertEqual(d["gap_id"], "gap-comp-12345678")
        self.assertEqual(d["classification"], "MISSING_CAPABILITY")
        self.assertEqual(d["status"], "DETECTED")

        restored = CapabilityGap.from_dict(d)
        self.assertEqual(restored.gap_id, gap.gap_id)
        self.assertEqual(restored.task_signature, gap.task_signature)
        self.assertEqual(restored.required_capability, gap.required_capability)
        self.assertEqual(restored.confidence, 0.9)
        self.assertEqual(restored.risk, "HIGH")

    def test_deterministic_task_signature(self):
        """Test that task signatures are deterministic and normalize case/tokens."""
        sig1 = CapabilityGapDetector.compute_task_signature(
            task_intent="Compile Rust library for WebAssembly",
            subsystem="compiler",
            target_files=["src/lib.rs", "Cargo.toml"],
        )
        sig2 = CapabilityGapDetector.compute_task_signature(
            task_intent="compile rust library for webassembly",
            subsystem="compiler",
            target_files=["src\\lib.rs", "Cargo.toml"],
        )
        self.assertEqual(sig1, sig2)
        self.assertEqual(len(sig1), 16)

    def test_classify_ordinary_implementation_failure(self):
        """Ordinary syntax/runtime bug must NOT be classified as capability gap."""
        cls, reason = CapabilityGapDetector.classify_deficit(
            task_intent="write parser",
            failure_evidence={"error": "SyntaxError: invalid syntax at line 42"},
            available_capabilities=["python_runtime"],
            available_tools=["run_command"],
            is_syntax_or_unit_test_failure=True,
        )
        self.assertEqual(cls, GapClassification.ORDINARY_IMPLEMENTATION_FAILURE)
        self.assertIn("Ordinary implementation failure", reason)

    def test_classify_verification_failure(self):
        """Standard test assertion caught by verification suite must not be a capability gap."""
        cls, reason = CapabilityGapDetector.classify_deficit(
            task_intent="run unit tests",
            failure_evidence={"exit_code": 1, "output": "FAILED (failures=1)"},
            available_capabilities=["python_test_runner"],
            available_tools=["run_command"],
            is_syntax_or_unit_test_failure=True,
        )
        self.assertEqual(cls, GapClassification.VERIFICATION_FAILURE)
        self.assertIn("Verification failure", reason)

    def test_classify_unavailable_and_unauthorized_tool(self):
        """Binary missing in host PATH vs policy blocked must be segregated."""
        cls_unavail, _ = CapabilityGapDetector.classify_deficit(
            task_intent="compile c code",
            failure_evidence={"cmd": "gcc"},
            available_capabilities=[],
            available_tools=[],
            is_binary_missing=True,
        )
        self.assertEqual(cls_unavail, GapClassification.UNAVAILABLE_TOOL)

        cls_unauth, _ = CapabilityGapDetector.classify_deficit(
            task_intent="run dangerous command",
            failure_evidence={"tool": "external_api"},
            available_capabilities=[],
            available_tools=[],
            is_policy_denied=True,
        )
        self.assertEqual(cls_unauth, GapClassification.UNAUTHORIZED_TOOL)

    def test_classify_stale_intelligence_and_missing_knowledge(self):
        """Stale intelligence and unindexed knowledge segregation."""
        cls_stale, _ = CapabilityGapDetector.classify_deficit(
            task_intent="find routes",
            failure_evidence={"error": "manifest out of date"},
            available_capabilities=[],
            available_tools=[],
            is_intelligence_stale=True,
        )
        self.assertEqual(cls_stale, GapClassification.STALE_INTELLIGENCE)

        cls_know, _ = CapabilityGapDetector.classify_deficit(
            task_intent="lookup api docs",
            failure_evidence={"error": "file not in index"},
            available_capabilities=[],
            available_tools=[],
            is_knowledge_unindexed=True,
        )
        self.assertEqual(cls_know, GapClassification.MISSING_KNOWLEDGE)

    def test_classify_wrong_routing_and_insufficient_evidence(self):
        """Wrong routing and vague unsubstantiated claims."""
        cls_route, _ = CapabilityGapDetector.classify_deficit(
            task_intent="database migration",
            failure_evidence={},
            available_capabilities=[],
            available_tools=[],
            is_routing_mismatch=True,
        )
        self.assertEqual(cls_route, GapClassification.WRONG_ROUTING)

        cls_no_ev, _ = CapabilityGapDetector.classify_deficit(
            task_intent="deploy app",
            failure_evidence={"unsubstantiated": True},
            available_capabilities=[],
            available_tools=[],
        )
        self.assertEqual(cls_no_ev, GapClassification.INSUFFICIENT_EVIDENCE)

    def test_classify_genuine_missing_capability(self):
        """Genuine missing capability when no false-positive condition matches."""
        cls_gap, reason = CapabilityGapDetector.classify_deficit(
            task_intent="run playwright e2e browser tests",
            failure_evidence={"exit_code": 127, "error": "playwright not supported in project OS"},
            available_capabilities=["pytest", "unittest"],
            available_tools=["run_command"],
        )
        self.assertEqual(cls_gap, GapClassification.MISSING_CAPABILITY)
        self.assertIn("Genuine capability gap", reason)

    def test_gap_creation_helper(self):
        """Test create_gap generates proper identifiers and structure."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="compile protobuf files",
            subsystem="codegen",
            required_capability="protoc_compiler",
            current_capabilities=["python_runtime"],
            failure_evidence={"exit_code": 127},
            confidence=0.95,
            risk="HIGH",
            target_files=["proto/service.proto"],
        )
        self.assertTrue(gap.gap_id.startswith("gap-code-"))
        self.assertEqual(gap.required_capability, "protoc_compiler")
        self.assertEqual(gap.status, GapStatus.DETECTED)
        self.assertEqual(gap.classification, GapClassification.MISSING_CAPABILITY)

    def test_lifecycle_engine_transitions_and_recurrence(self):
        """Test legal transitions, invalid transitions, and duplicate recurrence bumping."""
        engine = GapLifecycleEngine()

        gap1 = CapabilityGapDetector.create_gap(
            task_intent="lint terraform",
            subsystem="infrastructure",
            required_capability="tflint",
            current_capabilities=[],
            failure_evidence={"run": 1},
            confidence=0.8,
        )
        engine.register_gap(gap1)
        self.assertEqual(len(engine.list_gaps()), 1)

        # Re-register identical gap -> increments recurrence
        gap1_dup = CapabilityGapDetector.create_gap(
            task_intent="lint terraform",
            subsystem="infrastructure",
            required_capability="tflint",
            current_capabilities=[],
            failure_evidence={"run": 2},
            confidence=0.8,
        )
        registered = engine.register_gap(gap1_dup)
        self.assertEqual(registered.recurrence_count, 2)
        self.assertAlmostEqual(registered.confidence, 0.9)
        self.assertEqual(len(engine.list_gaps()), 1)

        # Legal lifecycle transitions: DETECTED -> VALIDATING -> CONFIRMED -> PROPOSED -> RESOLVED
        ok, msg, g = engine.transition_gap(gap1.gap_id, GapStatus.VALIDATING, "Checking PATH")
        self.assertTrue(ok)
        self.assertEqual(g.status, GapStatus.VALIDATING)

        ok, msg, g = engine.transition_gap(gap1.gap_id, GapStatus.CONFIRMED, "Empirically confirmed absent")
        self.assertTrue(ok)
        self.assertEqual(g.status, GapStatus.CONFIRMED)

        ok, msg, g = engine.transition_gap(gap1.gap_id, GapStatus.PROPOSED, "Emitted proposal")
        self.assertTrue(ok)
        self.assertEqual(g.status, GapStatus.PROPOSED)

        ok, msg, g = engine.transition_gap(gap1.gap_id, GapStatus.RESOLVED, "Installed tflint tool")
        self.assertTrue(ok)
        self.assertEqual(g.status, GapStatus.RESOLVED)
        self.assertIsNotNone(g.resolved_at)

        # Terminal state check: cannot transition out of RESOLVED
        ok, msg, g = engine.transition_gap(gap1.gap_id, GapStatus.DETECTED)
        self.assertFalse(ok)
        self.assertIn("Illegal transition", msg)

    def test_lifecycle_illegal_jump_rejected(self):
        """Attempting to jump from DETECTED directly to RESOLVED must be rejected."""
        engine = GapLifecycleEngine()
        gap = CapabilityGapDetector.create_gap(
            task_intent="run docker compose",
            subsystem="deployment",
            required_capability="docker",
            current_capabilities=[],
            failure_evidence={},
        )
        engine.register_gap(gap)

        ok, msg, _ = engine.transition_gap(gap.gap_id, GapStatus.RESOLVED)
        self.assertFalse(ok)
        self.assertIn("Illegal transition", msg)


if __name__ == "__main__":
    unittest.main()
