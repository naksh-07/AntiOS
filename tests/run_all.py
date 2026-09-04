"""Zero-Dependency Test Runner for AntiOS Core Framework & Skills."""

import os
import sys
import unittest

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import all test modules — baseline (Phase 12-15)
import tests.test_config as test_config
import tests.test_guard as test_guard
import tests.test_gate as test_gate
import tests.test_verdict as test_verdict
import tests.test_skills as test_skills
import tests.test_lifecycle as test_lifecycle
import tests.test_workflows as test_workflows

# Phase 16-18 hardened/new test modules
import tests.test_guard_hardened as test_guard_hardened
import tests.test_gate_hardened as test_gate_hardened
import tests.test_changeset as test_changeset
import tests.test_tool as test_tool
import tests.test_worktree as test_worktree
import tests.test_governance as test_governance

# Phase 19-20 Project Intelligence & Adaptation test modules
import tests.test_profile as test_profile
import tests.test_discovery as test_discovery
import tests.test_adapter as test_adapter
import tests.test_conflict as test_conflict
import tests.test_fixtures as test_fixtures

# Phase 21-22 Memory, Topology, Recovery & Adapter Verification test modules
import tests.test_memory as test_memory
import tests.test_topology as test_topology
import tests.test_recovery as test_recovery
import tests.test_adapter_verification as test_adapter_verification

# Phase 23-24 External Proving Ground, Maker-Checker & Learning Loop test modules
import tests.test_maker_checker_dispatch as test_maker_checker_dispatch
import tests.test_member_scoped_verification as test_member_scoped_verification
import tests.test_lesson_distillation as test_lesson_distillation
import tests.test_adversarial_verification as test_adversarial_verification
import tests.test_external_proving_ground as test_external_proving_ground

# Phase 25 Full-System Integration & Adversarial Certification test modules
import tests.test_subsystem_contracts as test_subsystem_contracts
import tests.test_e2e_scenarios as test_e2e_scenarios
import tests.test_false_done_campaign as test_false_done_campaign
import tests.test_failure_injection_campaign as test_failure_injection_campaign
import tests.test_performance_benchmarks as test_performance_benchmarks

# Phase 27 Agent-Native Engineering Environment test modules
import tests.test_subsystem as test_subsystem
import tests.test_wayfinding as test_wayfinding
import tests.test_docaudit as test_docaudit
import tests.test_wayfinding_adversarial as test_wayfinding_adversarial
import tests.test_phase27_integration as test_phase27_integration

# Phase 28-30 Agent-Native Project Knowledge & Wayfinding test modules
import tests.test_project_knowledge as test_project_knowledge
import tests.test_change_intent as test_change_intent
import tests.test_progressive_disclosure as test_progressive_disclosure
import tests.test_ownership_derivation as test_ownership_derivation
import tests.test_doc_infrastructure as test_doc_infrastructure
import tests.test_knowledge_wayfinding as test_knowledge_wayfinding
import tests.test_knowledge_adversarial as test_knowledge_adversarial
import tests.test_performance_phase28_30 as test_performance_phase28_30
import tests.test_phase28_30_integration as test_phase28_30_integration


def build_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    modules = [
        # Phase 12-15 baseline
        test_config,
        test_guard,
        test_gate,
        test_verdict,
        test_skills,
        test_lifecycle,
        test_workflows,
        # Phase 16-18 hardened/new
        test_guard_hardened,
        test_gate_hardened,
        test_changeset,
        test_tool,
        test_worktree,
        test_governance,
        # Phase 19-20
        test_profile,
        test_discovery,
        test_adapter,
        test_conflict,
        test_fixtures,
        # Phase 21-22
        test_memory,
        test_topology,
        test_recovery,
        test_adapter_verification,
        # Phase 23-24
        test_maker_checker_dispatch,
        test_member_scoped_verification,
        test_lesson_distillation,
        test_adversarial_verification,
        test_external_proving_ground,
        # Phase 25
        test_subsystem_contracts,
        test_e2e_scenarios,
        test_false_done_campaign,
        test_failure_injection_campaign,
        test_performance_benchmarks,
        # Phase 27
        test_subsystem,
        test_wayfinding,
        test_docaudit,
        test_wayfinding_adversarial,
        test_phase27_integration,
        # Phase 28-30
        test_project_knowledge,
        test_change_intent,
        test_progressive_disclosure,
        test_ownership_derivation,
        test_doc_infrastructure,
        test_knowledge_wayfinding,
        test_knowledge_adversarial,
        test_performance_phase28_30,
        test_phase28_30_integration,
    ]

    for mod in modules:
        for attr in dir(mod):
            if attr.startswith("test_") and callable(getattr(mod, attr)):
                func = getattr(mod, attr)
                suite.addTest(unittest.FunctionTestCase(func))

    return suite


if __name__ == "__main__":
    print(f"Executing AntiOS Test Suite on Python {sys.version.split()[0]}...")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = build_suite()
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
