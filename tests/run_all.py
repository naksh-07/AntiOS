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

# Phase 31-33 Project Capability Layer test modules
import tests.test_capability_model as test_capability_model
import tests.test_capability_registry as test_capability_registry
import tests.test_capability_router as test_capability_router
import tests.test_capability_pack as test_capability_pack
import tests.test_golden_tasks as test_golden_tasks
import tests.test_capability_adversarial as test_capability_adversarial
import tests.test_capability_benchmark as test_capability_benchmark

# Phase 34-36 Agent Topology & Specialist Layer test modules
import tests.test_agent_role_model as test_agent_role_model
import tests.test_agent_topology as test_agent_topology
import tests.test_agent_router as test_agent_router
import tests.test_golden_agent_routing as test_golden_agent_routing
import tests.test_agent_negative as test_agent_negative
import tests.test_agent_adversarial as test_agent_adversarial
import tests.test_agent_benchmark as test_agent_benchmark

# Phase 37-39 Tool, Provider & MCP Architecture test modules
import tests.test_provider_model as test_provider_model
import tests.test_tool_registry as test_tool_registry
import tests.test_tool_policy as test_tool_policy
import tests.test_tool_pack as test_tool_pack
import tests.test_golden_tool_routing as test_golden_tool_routing
import tests.test_tool_negative as test_tool_negative
import tests.test_tool_failure as test_tool_failure
import tests.test_tool_benchmark as test_tool_benchmark

# Phase 43-48 Project Agent OS Foundation & Installation Contract
import tests.test_project_manifest as test_project_manifest
import tests.test_provenance_ownership as test_provenance_ownership
import tests.test_boundary_compiler as test_boundary_compiler
import tests.test_installation_lifecycle as test_installation_lifecycle
import tests.test_orchestration_constitution as test_orchestration_constitution
import tests.test_installation_certification_e2e as test_installation_certification_e2e

# Phase 49-54 Main antios Skill, Native Orchestration & Dispatch Pipeline
import tests.test_main_antios_skill as test_main_antios_skill
import tests.test_orchestration_adaptive as test_orchestration_adaptive
import tests.test_dispatch_pipeline as test_dispatch_pipeline
import tests.test_orchestration_adversarial as test_orchestration_adversarial

# Phase 55-60 Project Intelligence & Adaptive Generation
import tests.test_project_anatomy as test_project_anatomy
import tests.test_component_intelligence as test_component_intelligence
import tests.test_skill_generation as test_skill_generation
import tests.test_specialist_generation as test_specialist_generation
import tests.test_workflow_retirement as test_workflow_retirement
import tests.test_intelligence_verification as test_intelligence_verification
import tests.test_phase55_60_fixtures as test_phase55_60_fixtures

# Phase 61-66 Project Learning & Safe Intelligence Evolution
import tests.test_learning_observations as test_learning_observations
import tests.test_learning_distillation_promotion as test_learning_distillation_promotion
import tests.test_learning_evolution_proposals as test_learning_evolution_proposals
import tests.test_learning_decay_staleness as test_learning_decay_staleness
import tests.test_learning_safety_gate_adversarial as test_learning_safety_gate_adversarial

# Phase 67-72 Two-Way Adaptation, Capability Gap Detection & Controlled Evolution
import tests.test_two_way_contract as test_two_way_contract
import tests.test_capability_gap_detection as test_capability_gap_detection
import tests.test_tool_mcp_gap_analysis as test_tool_mcp_gap_analysis
import tests.test_capability_proposal_engine as test_capability_proposal_engine
import tests.test_controlled_evolution as test_controlled_evolution
import tests.test_migration_contract as test_migration_contract
import tests.test_phase67_72_adversarial as test_phase67_72_adversarial

# Phase 73-78 Agent-Native Transformation & Evidence-Based Certification
import tests.test_agent_native_score as test_agent_native_score
import tests.test_agent_friction as test_agent_friction
import tests.test_agent_improvement as test_agent_improvement
import tests.test_documentation_compiler as test_documentation_compiler
import tests.test_agent_refactoring as test_agent_refactoring
import tests.test_agent_native_certification as test_agent_native_certification
import tests.test_phase73_78_adversarial as test_phase73_78_adversarial

# Phase 79-82 Project Instance Runtime Closure
import tests.test_runtime_closure as test_runtime_closure

# Phase 83-86 Native Antigravity Orchestration & Teamwork-Grade Workforce Architecture
import tests.test_workforce_contract as test_workforce_contract
import tests.test_workforce_planner as test_workforce_planner
import tests.test_teamwork_wave_orchestration as test_teamwork_wave_orchestration
import tests.test_hybrid_capability_matrix as test_hybrid_capability_matrix
import tests.test_orchestration_phase83_86_adversarial as test_orchestration_phase83_86_adversarial
import tests.test_proving_ground_scenarios as test_proving_ground_scenarios

# Phase 87-89 Context Engineering, Context Freshness & Mission State Continuity
import tests.test_context_budget_governor as test_context_budget_governor
import tests.test_context_freshness_compaction as test_context_freshness_compaction
import tests.test_mission_state_continuity as test_mission_state_continuity
import tests.test_context_mission_adversarial as test_context_mission_adversarial

# Phase 90-92 Evidence Architecture, Mission Evaluation & Agent-Native Benchmarking
import tests.test_evidence_architecture as test_evidence_architecture
import tests.test_mission_evaluation as test_mission_evaluation
import tests.test_mission_benchmark as test_mission_benchmark
import tests.test_evidence_evaluation_adversarial as test_evidence_evaluation_adversarial

# Phase 93-95 Durable Proofs, Runtime Drift Detection & Long-Horizon Certification
import tests.test_project_proof as test_project_proof
import tests.test_drift_health as test_drift_health
import tests.test_release_certification as test_release_certification
import tests.test_phase93_95_adversarial as test_phase93_95_adversarial

# Phase 96-98 Real Proving Ground, Failure Injection & Long-Horizon Adaptive Engineering
import tests.test_proving_ground as test_proving_ground
import tests.test_failure_injection as test_failure_injection
import tests.test_long_horizon as test_long_horizon
import tests.test_phase96_98_adversarial as test_phase96_98_adversarial

# Phase 99-101 Full System Certification, Universal Adoption & Architecture Freeze
import tests.test_system_certification as test_system_certification
import tests.test_universal_adoption as test_universal_adoption
import tests.test_production_readiness as test_production_readiness

# Phase 102 Productization, Release Engineering & Beta Readiness
import tests.test_versioning as test_versioning
import tests.test_lifecycle_productization as test_lifecycle_productization
import tests.test_git_github_release_capabilities as test_git_github_release_capabilities
import tests.test_beta_productization_e2e as test_beta_productization_e2e

# Phase 103 Local Engineering Intelligence: Storage & Data Directory Foundation
import tests.test_experience_foundation as test_experience_foundation

# Phase 104 Telemetry Sanitizer & Privacy Engine
import tests.test_telemetry_sanitizer as test_telemetry_sanitizer

# Phase 105 Antigravity Event Bridge & Experience Ingestion
import tests.test_telemetry_bridge as test_telemetry_bridge

# Phase 106 Experience Intelligence Engine & Separation Verification
import tests.test_experience_intelligence as test_experience_intelligence
import tests.test_experience_learning_separation as test_experience_learning_separation

# Phase 107 Experience Operations, Hardening & Certification
import tests.test_experience_operations as test_experience_operations




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
        # Phase 31-33
        test_capability_model,
        test_capability_registry,
        test_capability_router,
        test_capability_pack,
        test_golden_tasks,
        test_capability_adversarial,
        test_capability_benchmark,
        # Phase 34-36
        test_agent_role_model,
        test_agent_topology,
        test_agent_router,
        test_golden_agent_routing,
        test_agent_negative,
        test_agent_adversarial,
        test_agent_benchmark,
        # Phase 37-39
        test_provider_model,
        test_tool_registry,
        test_tool_policy,
        test_tool_pack,
        test_golden_tool_routing,
        test_tool_negative,
        test_tool_failure,
        test_tool_benchmark,
        # Phase 43-48
        test_project_manifest,
        test_provenance_ownership,
        test_boundary_compiler,
        test_installation_lifecycle,
        test_orchestration_constitution,
        test_installation_certification_e2e,
        # Phase 49-54
        test_main_antios_skill,
        test_orchestration_adaptive,
        test_dispatch_pipeline,
        test_orchestration_adversarial,
        # Phase 55-60
        test_project_anatomy,
        test_component_intelligence,
        test_skill_generation,
        test_specialist_generation,
        test_workflow_retirement,
        test_intelligence_verification,
        test_phase55_60_fixtures,
        # Phase 61-66
        test_learning_observations,
        test_learning_distillation_promotion,
        test_learning_evolution_proposals,
        test_learning_decay_staleness,
        test_learning_safety_gate_adversarial,
        # Phase 67-72
        test_two_way_contract,
        test_capability_gap_detection,
        test_tool_mcp_gap_analysis,
        test_capability_proposal_engine,
        test_controlled_evolution,
        test_migration_contract,
        test_phase67_72_adversarial,
        # Phase 73-78
        test_agent_native_score,
        test_agent_friction,
        test_agent_improvement,
        test_documentation_compiler,
        test_agent_refactoring,
        test_agent_native_certification,
        test_phase73_78_adversarial,
        # Phase 79-82
        test_runtime_closure,
        # Phase 83-86
        test_workforce_contract,
        test_workforce_planner,
        test_teamwork_wave_orchestration,
        test_hybrid_capability_matrix,
        test_orchestration_phase83_86_adversarial,
        test_proving_ground_scenarios,
        # Phase 87-89
        test_context_budget_governor,
        test_context_freshness_compaction,
        test_mission_state_continuity,
        test_context_mission_adversarial,
        # Phase 90-92
        test_evidence_architecture,
        test_mission_evaluation,
        test_mission_benchmark,
        test_evidence_evaluation_adversarial,
        # Phase 93-95
        test_project_proof,
        test_drift_health,
        test_release_certification,
        test_phase93_95_adversarial,
        # Phase 96-98
        test_proving_ground,
        test_failure_injection,
        test_long_horizon,
        test_phase96_98_adversarial,
        # Phase 99-101
        test_system_certification,
        test_universal_adoption,
        test_production_readiness,
        # Phase 102 Productization, Release Engineering & Beta Readiness
        test_versioning,
        test_lifecycle_productization,
        test_git_github_release_capabilities,
        test_beta_productization_e2e,
        # Phase 103 Local Engineering Intelligence: Storage & Data Directory Foundation
        test_experience_foundation,
        # Phase 104 Telemetry Sanitizer & Privacy Engine
        test_telemetry_sanitizer,
        # Phase 105 Antigravity Event Bridge & Experience Ingestion
        test_telemetry_bridge,
        # Phase 106 Experience Intelligence Engine & Separation Verification
        test_experience_intelligence,
        test_experience_learning_separation,
        # Phase 107 Experience Operations, Hardening & Certification
        test_experience_operations,
    ]


    loader = unittest.defaultTestLoader
    for mod in modules:
        suite.addTests(loader.loadTestsFromModule(mod))
        for attr in dir(mod):
            val = getattr(mod, attr)
            if attr.startswith("test_") and callable(val) and not isinstance(val, type):
                suite.addTest(unittest.FunctionTestCase(val))

    return suite


if __name__ == "__main__":
    print(f"Executing AntiOS Test Suite on Python {sys.version.split()[0]}...")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = build_suite()
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
