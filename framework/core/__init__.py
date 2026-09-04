"""AntiOS v1 Core Framework Package.

This package provides the governance and capability primitives for AntiOS:
- config: Declarative adapter configuration and defaults
- guard: Deterministic path protection and boundary enforcement
- gate: Dynamic test runner execution and verification ratchets
- verdict: Structured verifier verdict data model and parsing
- governance: Governance model primitives (RULE/SKILL/WORKFLOW/HOOK/TOOL/ADAPTER)
- tool: Minimal tool abstraction with selection policy and failure taxonomy
- changeset: Same Change Set integrity evaluation engine
- worktree: Git working tree state inspection and conflict detection
"""

from framework.core.config import AntiOSConfig, load_config
from framework.core.guard import evaluate_tool_call
from framework.core.gate import evaluate_stop_gate, resolve_verification_scope
from framework.core.verdict import (
    VerificationVerdict,
    parse_verdict,
    format_verdict,
    prepare_checker_context,
    evaluate_checker_verdict,
)
from framework.core.governance import (
    GovernancePrimitiveType,
    GovernancePrimitiveDefinition,
    GOVERNANCE_TAXONOMY,
    get_governance_primitive,
    validate_governance_boundaries,
)
from framework.core.tool import (
    ToolTier,
    ToolStatus,
    FailureClass,
    ToolIdentity,
    ToolResult,
    ToolSelectionPolicy,
)
from framework.core.changeset import (
    ChangesetPolicy,
    ChangeSetEvaluation,
    evaluate_changeset,
)
from framework.core.worktree import (
    WorktreeDisposition,
    WorktreeSnapshot,
    WorktreeAuditResult,
    capture_worktree_snapshot,
    inspect_all_conflicts,
    audit_worktree,
)
from framework.core.profile import (
    EvidenceTier,
    ConfidenceLevel,
    ToolCategory,
    ConflictType,
    EvidenceFact,
    InferredFact,
    UnknownFact,
    ToolFact,
    GuidanceFact,
    ConflictFact,
    ProjectIdentity,
    ProjectProfile,
)
from framework.core.discovery import (
    ProjectDiscoveryEngine,
    discover_project,
)
from framework.core.adapter import (
    ActionType,
    ChangeTarget,
    ProposalRisk,
    AdaptationProposalItem,
    AdaptationProposal,
    AdapterVerificationResult,
    analyze_adaptation,
    generate_adapter_config,
    apply_project_adaptation,
    verify_adapter,
)
from framework.core.lifecycle import (
    TaskStage,
    TaskStatus,
    TaskClass,
    RiskTier,
    TaskState,
    create_task,
    transition_stage,
    interrupt_task,
    block_task,
    recover_task,
    fail_task,
    sync_to_active_context,
    parse_active_context,
)
from framework.core.workflow import (
    WorkflowSpec,
    WORKFLOW_REGISTRY,
    get_workflow,
    list_workflows,
)
from framework.core.topology import (
    WorkspaceTopology,
    WorkspaceMember,
    detect_workspace_topology,
)
from framework.core.memory import (
    MemoryCategory,
    KnowledgeAuthority,
    MemoryRecord,
    ProjectKnowledgeFact,
    DecisionRecord,
    LessonRecord,
    HistoricalRecord,
    MemoryWritePolicy,
    sync_project_knowledge,
    parse_project_knowledge,
    sync_lessons,
    parse_lessons,
    sync_historical_record,
    parse_historical_record,
    sync_decision_register,
    parse_decision_register,
    DeterministicLessonMatcher,
    DistillationResult,
    LessonDistillationEngine,
)
from framework.core.recovery import (
    ContradictionType,
    Contradiction,
    RecoveryPlan,
    reconstruct_session_state,
    detect_state_contradictions,
    is_verification_stale,
    generate_recovery_plan,
    recover_session,
)
from framework.core.telemetry import (
    ExecutionTelemetryRecord,
    record_telemetry,
    load_telemetry,
    summarize_telemetry,
)
from framework.core.subsystem import (
    SubsystemDeclaration,
    validate_subsystem_declaration,
)
from framework.core.wayfinding import (
    WayfindingEngine,
    LocalityResolution,
)
from framework.core.docaudit import (
    DocReference,
    DocAuditResult,
    audit_documentation_references,
    audit_all_documentation,
)
from framework.core.knowledge import (
    KnowledgeEpistemicTier,
    RelationshipType,
    KnowledgeEdge,
    KnowledgeGraph,
    OwnershipResolution,
    OwnershipDeriver,
    DocCategory,
    DocArtifactFact,
    DocKnowledgeClassifier,
    ChangeIntent,
    ChangeIntentAnalyzer,
    ProgressiveDisclosureLevel,
    ProgressiveDisclosureEngine,
)
from framework.core.capability import (
    Capability,
    CapabilityType,
    CapabilityScope,
    RulePrecedence,
    RuleConflictStatus,
    VerifierType,
    MCPStatus,
    RuleCapability,
    SpecialistCapability,
    MCPDecision,
)
from framework.core.capability_registry import (
    CapabilityRegistry,
    build_default_registry,
)
from framework.core.capability_router import (
    CapabilityRouter,
    TaskIntent,
)
from framework.core.capability_pack import (
    CapabilityPack,
)
from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    DelegationDecisionType,
    EscalationPolicyType,
    AgentHandoffContract,
    SpecialistResultReport,
    SpecialistCandidate,
)
from framework.core.agent_topology import (
    AgentTopologyRegistry,
    build_default_agent_topology,
    SpecialistDiscoveryEngine,
)
from framework.core.agent_routing_pack import (
    AgentRoutingPack,
)
from framework.core.agent_router import (
    AgentRouter,
)
from framework.core.tool import (
    ExecutionMode,
    Locality,
    ProviderAvailability,
    CostHint,
    LatencyHint,
    ToolPolicyStatus,
    ToolDefinition,
)
from framework.core.provider import (
    ProviderType,
    ProviderPolicyStatus,
    ProviderDefinition,
)
from framework.core.tool_registry import (
    ToolRegistry,
    build_default_tool_registry,
)
from framework.core.tool_policy import (
    MCPJustificationReport,
    MCPJustificationEngine,
    DeterministicToolSelector,
)
from framework.core.tool_pack import (
    ToolRoutingPack,
)

__all__ = [
    # Phase 12-15
    "AntiOSConfig",
    "load_config",
    "evaluate_tool_call",
    "evaluate_stop_gate",
    "VerificationVerdict",
    "parse_verdict",
    "format_verdict",
    "TaskStage",
    "TaskStatus",
    "TaskClass",
    "RiskTier",
    "TaskState",
    "create_task",
    "transition_stage",
    "interrupt_task",
    "block_task",
    "recover_task",
    "fail_task",
    "sync_to_active_context",
    "parse_active_context",
    "WorkflowSpec",
    "WORKFLOW_REGISTRY",
    "get_workflow",
    "list_workflows",
    # Phase 16-18: Governance
    "GovernancePrimitiveType",
    "GovernancePrimitiveDefinition",
    "GOVERNANCE_TAXONOMY",
    "get_governance_primitive",
    "validate_governance_boundaries",
    # Phase 16-18: Tool
    "ToolTier",
    "ToolStatus",
    "FailureClass",
    "ToolIdentity",
    "ToolResult",
    "ToolSelectionPolicy",
    # Phase 16-18: Changeset
    "ChangesetPolicy",
    "ChangeSetEvaluation",
    "evaluate_changeset",
    # Phase 16-18: Worktree
    "WorktreeDisposition",
    "WorktreeSnapshot",
    "WorktreeAuditResult",
    "capture_worktree_snapshot",
    "inspect_all_conflicts",
    "audit_worktree",
    # Phase 19-20: Project Intelligence & Adaptation
    "EvidenceTier",
    "ConfidenceLevel",
    "ToolCategory",
    "ConflictType",
    "EvidenceFact",
    "InferredFact",
    "UnknownFact",
    "ToolFact",
    "GuidanceFact",
    "ConflictFact",
    "ProjectIdentity",
    "ProjectProfile",
    "ProjectDiscoveryEngine",
    "discover_project",
    "ActionType",
    "ChangeTarget",
    "ProposalRisk",
    "AdaptationProposalItem",
    "AdaptationProposal",
    "AdapterVerificationResult",
    "analyze_adaptation",
    "generate_adapter_config",
    "apply_project_adaptation",
    "verify_adapter",
    # Phase 21-22: Workspace Topology, Memory & Recovery
    "WorkspaceTopology",
    "WorkspaceMember",
    "detect_workspace_topology",
    "MemoryCategory",
    "KnowledgeAuthority",
    "MemoryRecord",
    "ProjectKnowledgeFact",
    "DecisionRecord",
    "LessonRecord",
    "HistoricalRecord",
    "MemoryWritePolicy",
    "sync_project_knowledge",
    "parse_project_knowledge",
    "sync_lessons",
    "parse_lessons",
    "sync_historical_record",
    "parse_historical_record",
    "sync_decision_register",
    "parse_decision_register",
    "DeterministicLessonMatcher",
    "DistillationResult",
    "LessonDistillationEngine",
    "prepare_checker_context",
    "evaluate_checker_verdict",
    "resolve_verification_scope",
    "ContradictionType",
    "Contradiction",
    "RecoveryPlan",
    "reconstruct_session_state",
    "detect_state_contradictions",
    "is_verification_stale",
    "generate_recovery_plan",
    "recover_session",
    "ExecutionTelemetryRecord",
    "record_telemetry",
    "load_telemetry",
    "summarize_telemetry",
    # Phase 27: Wayfinding, Subsystems & Doc Audit
    "SubsystemDeclaration",
    "validate_subsystem_declaration",
    "WayfindingEngine",
    "LocalityResolution",
    "DocReference",
    "DocAuditResult",
    "audit_documentation_references",
    "audit_all_documentation",
    # Phase 28-30: Project Knowledge & Wayfinding
    "KnowledgeEpistemicTier",
    "RelationshipType",
    "KnowledgeEdge",
    "KnowledgeGraph",
    "OwnershipResolution",
    "OwnershipDeriver",
    "DocCategory",
    "DocArtifactFact",
    "DocKnowledgeClassifier",
    "ChangeIntent",
    "ChangeIntentAnalyzer",
    "ProgressiveDisclosureLevel",
    "ProgressiveDisclosureEngine",
    # Phase 31-33: Project Capability Layer
    "Capability",
    "CapabilityType",
    "CapabilityScope",
    "RulePrecedence",
    "RuleConflictStatus",
    "VerifierType",
    "MCPStatus",
    "RuleCapability",
    "SpecialistCapability",
    "MCPDecision",
    "CapabilityRegistry",
    "build_default_registry",
    "CapabilityRouter",
    "TaskIntent",
    "CapabilityPack",
    # Phase 34-36: Agent Topology & Specialist Layer
    "AgentRole",
    "AgentRoleType",
    "AgentCapabilityBoundary",
    "DelegationDecisionType",
    "EscalationPolicyType",
    "AgentHandoffContract",
    "SpecialistResultReport",
    "SpecialistCandidate",
    "AgentTopologyRegistry",
    "build_default_agent_topology",
    "SpecialistDiscoveryEngine",
    "AgentRoutingPack",
    "AgentRouter",
    # Phase 37-39: Tool, Provider & MCP Architecture
    "ExecutionMode",
    "Locality",
    "ProviderAvailability",
    "CostHint",
    "LatencyHint",
    "ToolPolicyStatus",
    "ToolDefinition",
    "ProviderType",
    "ProviderPolicyStatus",
    "ProviderDefinition",
    "ToolRegistry",
    "build_default_tool_registry",
    "MCPJustificationReport",
    "MCPJustificationEngine",
    "DeterministicToolSelector",
    "ToolRoutingPack",
]
