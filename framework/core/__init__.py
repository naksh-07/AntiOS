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
from framework.core.gate import evaluate_stop_gate
from framework.core.verdict import VerificationVerdict, parse_verdict, format_verdict
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
    analyze_adaptation,
    generate_adapter_config,
    apply_project_adaptation,
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
    "analyze_adaptation",
    "generate_adapter_config",
    "apply_project_adaptation",
]
