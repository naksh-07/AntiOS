"""Unit tests for Phase 83 AntiOS-to-Antigravity Workforce Contract."""

import unittest

from framework.core.workforce_contract import (
    CANONICAL_RESPONSIBILITY_ALLOCATIONS,
    CapabilityHierarchyStep,
    DEFAULT_WORKFORCE_CONTRACT,
    ResponsibilityAllocation,
    ResponsibilityDomain,
    WorkforceContract,
)


class TestWorkforceContract(unittest.TestCase):
    """Verifies Phase 83 Native Workforce Contract and responsibility demarcation."""

    def test_default_workforce_contract_is_valid(self):
        """Default contract must pass self-validation."""
        valid, errors = DEFAULT_WORKFORCE_CONTRACT.validate()
        self.assertTrue(valid, f"Contract validation failed: {errors}")
        self.assertEqual(len(errors), 0)

    def test_responsibility_domains_segregation(self):
        """Verifies clear ownership boundaries between AntiOS and Antigravity."""
        c = DEFAULT_WORKFORCE_CONTRACT

        # Platform owns execution primitives and runtime
        self.assertTrue(c.is_antigravity_responsibility("subagent_lifecycle"))
        self.assertTrue(c.is_antigravity_responsibility("tool_execution_transport"))
        self.assertTrue(c.is_antigravity_responsibility("agent_execution_runtime"))
        self.assertTrue(c.is_antigravity_responsibility("background_execution"))

        # AntiOS Core owns engineering governance, planning, and verification gates
        self.assertTrue(c.is_antios_responsibility("user_intent_clarification"))
        self.assertTrue(c.is_antios_responsibility("task_classification"))
        self.assertTrue(c.is_antios_responsibility("workforce_planning"))
        self.assertTrue(c.is_antios_responsibility("delegation_policy"))
        self.assertTrue(c.is_antios_responsibility("verification_governance"))
        self.assertTrue(c.is_antios_responsibility("risk_analysis"))

    def test_canonical_11_step_hierarchy_sequence(self):
        """Verifies canonical 11-step capability hierarchy order."""
        steps = list(CapabilityHierarchyStep)
        self.assertEqual(len(steps), 11)

        expected_order = [
            CapabilityHierarchyStep.STEP_01_USER,
            CapabilityHierarchyStep.STEP_02_CONTROL_PLANE,
            CapabilityHierarchyStep.STEP_03_MISSION_UNDERSTANDING,
            CapabilityHierarchyStep.STEP_04_PROJECT_INTELLIGENCE,
            CapabilityHierarchyStep.STEP_05_CAPABILITY_SELECTION,
            CapabilityHierarchyStep.STEP_06_WORKFORCE_PLAN,
            CapabilityHierarchyStep.STEP_07_NATIVE_EXECUTION,
            CapabilityHierarchyStep.STEP_08_SPECIALIST_SUBAGENT,
            CapabilityHierarchyStep.STEP_09_TOOL_CLI_MCP,
            CapabilityHierarchyStep.STEP_10_EVIDENCE_COLLECTION,
            CapabilityHierarchyStep.STEP_11_VERIFICATION_MEMORY,
        ]
        self.assertEqual(steps, expected_order)

    def test_validate_capability_hierarchy_enforces_order(self):
        """Sequential hierarchy validation catches out-of-order execution."""
        c = DEFAULT_WORKFORCE_CONTRACT
        valid_trace = [
            "USER",
            "CONTROL_PLANE_ANTIOS",
            "MISSION_UNDERSTANDING",
            "CAPABILITY_SELECTION",
            "NATIVE_ANTIGRAVITY_EXECUTION",
            "VERIFICATION_AND_MEMORY",
        ]
        valid, violations = c.validate_capability_hierarchy(valid_trace)
        self.assertTrue(valid, f"Expected valid trace but got: {violations}")

        # Inverted trace: executing verification before mission understanding
        inverted_trace = [
            "USER",
            "VERIFICATION_AND_MEMORY",
            "MISSION_UNDERSTANDING",
        ]
        valid, violations = c.validate_capability_hierarchy(inverted_trace)
        self.assertFalse(valid)
        self.assertTrue(any("inversion" in v for v in violations))

    def test_contract_rejects_antios_claiming_platform_primitives(self):
        """Contract must fail validation if AntiOS attempts to own Antigravity primitives."""
        usurped_allocs = [
            ResponsibilityAllocation(
                responsibility="invoke_subagent",
                owner=ResponsibilityDomain.ANTIOS,  # Usurped!
                rationale="AntiOS claims native subagent execution.",
            )
        ]
        usurped_contract = WorkforceContract(
            version="2.0.0",
            allocations=usurped_allocs,
        )
        valid, errors = usurped_contract.validate()
        self.assertFalse(valid)
        self.assertTrue(any("Usurpation violation" in err for err in errors))

    def test_check_emulation_violation_detects_prohibited_mechanisms(self):
        """Detects custom daemons, workflow engines, or background pollers."""
        c = DEFAULT_WORKFORCE_CONTRACT

        violation, msg = c.check_emulation_violation("spawn custom_daemon for background task")
        self.assertTrue(violation)
        self.assertIn("Contract Violation", msg)

        violation, msg = c.check_emulation_violation("create custom workflow_engine")
        self.assertTrue(violation)
        self.assertIn("Contract Violation", msg)

        violation, msg = c.check_emulation_violation("run while true polling_loop")
        self.assertTrue(violation)
        self.assertIn("Contract Violation", msg)

        violation, msg = c.check_emulation_violation("read file and run unit test")
        self.assertFalse(violation)

    def test_to_dict_and_from_dict_roundtrip(self):
        """Serialization roundtrip produces identical contract."""
        data = DEFAULT_WORKFORCE_CONTRACT.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["version"], "2.0.0")
        self.assertEqual(len(data["canonical_hierarchy"]), 11)

        restored = WorkforceContract.from_dict(data)
        valid, errors = restored.validate()
        self.assertTrue(valid)
        self.assertEqual(len(restored.allocations), len(DEFAULT_WORKFORCE_CONTRACT.allocations))


if __name__ == "__main__":
    unittest.main()
