"""Tests for AntiOS 2.0 Phase 58: Project-Specific Specialist Generation.

Verifies:
- Evidence-driven specialist role synthesis.
- Rejection of spurious generation ("React exists" / "Python exists").
- Strict enforcement of Shallow Depth Law (max_depth <= 2, can_delegate == False).
- Mandatory inclusion of core forbidden boundaries (rule:core-immutable:override, etc.).
- Integration with AgentRouter task routing.
"""

from pathlib import Path
import unittest

from framework.core.agent_role import AgentRole, AgentRoleType
from framework.core.agent_router import AgentRouter
from framework.core.agent_topology import AgentTopologyRegistry, build_default_agent_topology
from framework.core.anatomy import ProjectAnatomy, ProjectAnatomyCompiler
from framework.core.capability_pack import CapabilityPack
from framework.core.lifecycle import RiskTier, TaskClass
from framework.core.specialist_generator import SpecialistGenerator
from framework.core.subsystem import SubsystemDeclaration


class TestSpecialistGeneration(unittest.TestCase):
    """Unit tests for SpecialistGenerator."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_frontend_specialist_generation_on_frontend_design_system(self):
        fe_repo = self.fixtures_dir / "frontend_design_system"
        compiler = ProjectAnatomyCompiler(fe_repo)
        anatomy = compiler.compile()

        subsystems = [
            SubsystemDeclaration.from_dict({
                "subsystem_id": "components",
                "name": "UI Components",
                "area": "ui",
                "description": "Frontend components with Tailwind and Vitest",
                "root_paths": ["src/components"],
                "entrypoints": ["src/components/Button.tsx"],
                "covering_tests": ["tests/Button.test.tsx"],
                "test_commands": ["vitest run"],
                "risk_tier": "MEDIUM",
            })
        ]

        roles = SpecialistGenerator.evaluate_specialist_justification(anatomy, subsystems=subsystems)
        self.assertTrue(len(roles) > 0)
        fe_spec = next((r for r in roles if r.role_id == "role:frontend-specialist"), None)
        self.assertIsNotNone(fe_spec)
        self.assertEqual(fe_spec.role_type, AgentRoleType.SPECIALIST)

        # SHALLOW DEPTH LAW
        self.assertLessEqual(fe_spec.max_depth, 2)
        self.assertFalse(fe_spec.can_delegate)

        # Mandatory forbidden core capabilities
        self.assertIn("rule:core-immutable:override", fe_spec.boundary.forbidden_capabilities)
        self.assertIn("rule:stop-gate-ratchet:override", fe_spec.boundary.forbidden_capabilities)

    def test_no_spurious_specialist_on_simple_python(self):
        py_repo = self.fixtures_dir / "python_project"
        compiler = ProjectAnatomyCompiler(py_repo)
        anatomy = compiler.compile()

        # No dedicated UI or complex migrations subsystems
        roles = SpecialistGenerator.evaluate_specialist_justification(anatomy, subsystems=[])
        self.assertFalse(any(r.role_id == "role:frontend-specialist" for r in roles))
        self.assertFalse(any(r.role_id == "role:database-specialist" for r in roles))

    def test_specialist_routing_via_agent_router(self):
        # Build registry with generated specialist
        reg = build_default_agent_topology()
        fe_role = AgentRole(
            role_id="role:frontend-specialist",
            name="Frontend Specialist",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Frontend UI component development",
            applies_to_task_types=["FEATURE", "BUG"],
            applies_to_subsystems=["components", "ui"],
            max_depth=2,
            can_delegate=False,
            enabled=True,
        )
        reg.register(fe_role)

        router = AgentRouter(topology_registry=reg)
        pack = CapabilityPack(
            pack_id="pack-fe-01",
            project_name="frontend_design_system",
            task_intent="Change the login button styling",
            task_class=TaskClass.FEATURE.value,
            risk_tier=RiskTier.MEDIUM.value,
            matched_subsystems=["components"],
            matched_components=["Button"],
            workflow={"id": "wf:feature", "name": "Feature"},
            skills=[{"capability_id": "skill:frontend-design", "name": "frontend-design"}],
            rules=[{"capability_id": "rule:design-system-tokens", "name": "design-system-tokens"}],
            tools=[{"capability_id": "tool:replace_file_content", "name": "replace_file_content"}],
            verifier={"capability_id": "verifier:solo", "name": "Solo Verifier"},
            specialists=[],
            providers=[],
            mcp_decision={"status": "NOT_NEEDED", "justification": "Local edit"},
            why_selected={"subsystem": "Direct match"},
        )

        routing_pack = router.route_task(pack, target_files=["src/components/Button.tsx"])
        self.assertEqual(routing_pack.delegation_decision, "DELEGATE_SPECIALIST")
        self.assertIsNotNone(routing_pack.selected_specialist)
        self.assertEqual(routing_pack.selected_specialist["role_id"], "role:frontend-specialist")


if __name__ == "__main__":
    unittest.main()
