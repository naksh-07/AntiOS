"""AntiOS 2.0 Constitutional Orchestration Engine.

Authoritative AntiOS mission orchestration layer implementing:
- Hard Constitutional Limits:
    MAX_ACTIVE_AGENTS_PER_WAVE = 10
    MAX_TOTAL_SPAWNED_AGENTS = 20 (across entire mission delegation tree)
    MAX_DELEGATION_DEPTH = 2 (Shallow Depth Law: Root=0 -> Child=1 -> Grandchild=2)
- Adaptive Workforce Sizing:
    SOLO, FOCUSED, SMALL, PARALLEL, STAGED, HIERARCHICAL, MAX
- Dual Mandatory Dispatch Gates:
    Gate A: Pre-Planning Dispatch (checks multi-domain, independent lanes, file scope)
    Gate B: Execution Dispatch (checks implementation workstreams, independence, coupling)
- Mission Resource Ledger:
    Tracks mission_id, spawned_total, active_total, remaining_budget, current_wave,
    current_depth, active_workers, worker_roles, reserved_capacity, completed_workers,
    failed_workers, collapsed_workers. Fail-closed on uncertainty.
- Adaptive Wave Lifecycle & Mandatory Collapse:
    RECONNAISSANCE -> PLANNING -> IMPLEMENTATION -> VERIFICATION -> DELIVERY
    NEXT_WAVE_ALLOWED only when PREVIOUS_WAVE_STATE == COLLAPSED (active_total == 0)
- Read-Parallel / Write-Controlled Policy:
    Disjoint writes, isolated branches, controlled single-writer fallback.
- Hierarchical Capacity Reservation:
    Coordinators receive bounded child quotas from root; unused capacity reverts to root.
- Structured Evidence Handoffs:
    Objective, observations, logic chain, evidence, caveats, conclusion, verification method, next owner.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# Constitutional Hard Limits
MAX_ACTIVE_AGENTS_PER_WAVE = 10
MAX_TOTAL_SPAWNED_AGENTS = 20
MAX_DELEGATION_DEPTH = 2


class OrchestrationBudgetExceeded(Exception):
    """Raised when an operation attempts to exceed constitutional agent limits."""
    pass


class WorkforceMode(str, Enum):
    """Adaptive workforce sizing modes."""
    SOLO = "SOLO"                     # 0 subagents (parent handles directly)
    FOCUSED = "FOCUSED"               # 1 specialist (focused investigation / implementation)
    SMALL = "SMALL"                   # 2 specialists (paired streams)
    PARALLEL = "PARALLEL"             # 2-4 specialists across independent streams
    STAGED = "STAGED"                 # Multi-wave staged progression
    HIERARCHICAL = "HIERARCHICAL"     # Coordinator with delegated leaf children
    MAX = "MAX"                       # Budget-capped ceiling (<=10 active, <=20 total)


class WaveState(str, Enum):
    """State of an execution wave."""
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    CONSOLIDATING = "CONSOLIDATING"
    COLLAPSED = "COLLAPSED"


class CanonicalWave(str, Enum):
    """Canonical mission wave stages."""
    RECONNAISSANCE = "RECONNAISSANCE"
    PLANNING = "PLANNING"
    IMPLEMENTATION = "IMPLEMENTATION"
    VERIFICATION = "VERIFICATION"
    DELIVERY = "DELIVERY"


class CoordinationLevel(str, Enum):
    """Progressive coordination depth matching task complexity."""
    L0 = "L0"  # Tiny / Solo: No persistent coordination files
    L1 = "L1"  # Focused / Small: Lightweight structured summaries
    L2 = "L2"  # Multi-Wave: Artifact-based state (mission.md, progress.md, dead-ends.md)
    L3 = "L3"  # Large / Hierarchical: Full mission ledger, gates, and final audit


class WriteSafetyPolicy(str, Enum):
    """Policy governing concurrent write safety."""
    READ_ONLY = "READ_ONLY"
    CONTROLLED_SINGLE_WRITER = "CONTROLLED_SINGLE_WRITER"
    SAFELY_PARALLELIZABLE = "SAFELY_PARALLELIZABLE"
    UNSAFE_TO_PARALLELIZE = "UNSAFE_TO_PARALLELIZE"


class DispatchGateType(str, Enum):
    """Types of mandatory dispatch gates."""
    PRE_PLANNING = "PRE_PLANNING"
    EXECUTION_DISPATCH = "EXECUTION_DISPATCH"


class GateDecision(str, Enum):
    """Outcomes of dispatch gate evaluation."""
    SOLO_AUTHORIZED = "SOLO_AUTHORIZED"
    DELEGATION_MANDATORY = "DELEGATION_MANDATORY"
    COORDINATOR_AUTHORIZED = "COORDINATOR_AUTHORIZED"
    BLOCKED = "BLOCKED"


@dataclass
class StructuredHandoff:
    """Standardized evidence handoff contract returned by specialists."""
    objective: str
    observations: List[str] = field(default_factory=list)
    logic_chain: str = ""
    evidence: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    conclusion: str = ""
    verification_method: str = ""
    next_owner: str = "primary-engineer"

    def validate(self) -> Tuple[bool, List[str]]:
        """Deterministically validates handoff completeness and evidence grounding."""
        errors: List[str] = []
        if not self.objective or not self.objective.strip():
            errors.append("Handoff missing required objective.")
        if not self.conclusion or not self.conclusion.strip():
            errors.append("Handoff missing required conclusion.")
        if not self.verification_method or not self.verification_method.strip():
            errors.append("Handoff missing required verification_method.")
        if not self.evidence or len(self.evidence) == 0:
            errors.append("Handoff missing concrete evidence (must include file paths, diffs, or commands).")
        else:
            has_grounding = any(
                any(marker in str(e) for marker in (":", "/", "\\", "diff", "exit", "test", "line", "def ", "class "))
                for e in self.evidence if isinstance(e, str)
            )
            if not has_grounding:
                errors.append("Evidence lacks grounding (no file paths, symbols, lines, or command outputs found).")
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "observations": list(self.observations),
            "logic_chain": self.logic_chain,
            "evidence": list(self.evidence),
            "caveats": list(self.caveats),
            "conclusion": self.conclusion,
            "verification_method": self.verification_method,
            "next_owner": self.next_owner,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StructuredHandoff:
        return cls(
            objective=str(data.get("objective", "")),
            observations=list(data.get("observations", [])),
            logic_chain=str(data.get("logic_chain", "")),
            evidence=list(data.get("evidence", [])),
            caveats=list(data.get("caveats", [])),
            conclusion=str(data.get("conclusion", "")),
            verification_method=str(data.get("verification_method", "")),
            next_owner=str(data.get("next_owner", "primary-engineer")),
        )


@dataclass
class AgentRecord:
    """Tracking record for a spawned subagent in the mission tree."""
    agent_id: str
    role: str
    depth: int
    wave_number: int
    spawned_at: float = field(default_factory=time.time)
    terminated_at: Optional[float] = None
    is_active: bool = True
    handoff: Optional[StructuredHandoff] = None
    parent_id: Optional[str] = None
    is_coordinator: bool = False
    reserved_quota: int = 0
    actually_spawned: int = 0
    failure_reason: Optional[str] = None


@dataclass
class DispatchGateResult:
    """Structured evaluation from a Pre-Planning or Execution Dispatch Gate."""
    gate_type: DispatchGateType
    decision: GateDecision
    mode: WorkforceMode
    recommended_workers: int
    reasons: List[str]
    checklist: Dict[str, Any] = field(default_factory=dict)
    budget_reserved: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_type": self.gate_type.value,
            "decision": self.decision.value,
            "mode": self.mode.value,
            "recommended_workers": self.recommended_workers,
            "reasons": list(self.reasons),
            "checklist": dict(self.checklist),
            "budget_reserved": self.budget_reserved,
        }


@dataclass
class MissionLedger:
    """Authoritative mission-wide resource ledger for AntiOS orchestration.
    
    Tracks global launches, active concurrency, coordinator reservations,
    wave states, and worker outcomes.
    """
    mission_id: str = "mission-001"
    max_active_per_wave: int = MAX_ACTIVE_AGENTS_PER_WAVE
    max_total_spawned: int = MAX_TOTAL_SPAWNED_AGENTS
    max_depth: int = MAX_DELEGATION_DEPTH
    spawned_total: int = 0
    active_total: int = 0
    current_wave: int = 0
    current_depth: int = 0
    active_workers: List[str] = field(default_factory=list)
    worker_roles: Dict[str, str] = field(default_factory=dict)
    reserved_capacity: Dict[str, int] = field(default_factory=dict)
    completed_workers: List[str] = field(default_factory=list)
    failed_workers: List[str] = field(default_factory=list)
    collapsed_workers: List[str] = field(default_factory=list)
    records: Dict[str, AgentRecord] = field(default_factory=dict)

    @property
    def remaining_budget(self) -> int:
        """Global launches remaining across Root + Children."""
        return max(0, self.max_total_spawned - self.spawned_total)

    @property
    def available_active_slots(self) -> int:
        """Available concurrency slots in the current wave."""
        return max(0, self.max_active_per_wave - self.active_total)

    def can_spawn(self, depth: int = 1, parent_id: Optional[str] = None) -> Tuple[bool, str]:
        """Pre-spawn gate verifying all constitutional constraints."""
        if depth > self.max_depth:
            return False, f"Shallow Depth Law violation: depth {depth} exceeds constitutional limit {self.max_depth}"
        if self.spawned_total >= self.max_total_spawned:
            return False, f"Constitutional ceiling reached: spawned {self.spawned_total}/{self.max_total_spawned} total agents"
        if self.active_total >= self.max_active_per_wave:
            return False, f"Wave concurrency limit reached: active {self.active_total}/{self.max_active_per_wave} agents"

        if parent_id and parent_id in self.records:
            parent_rec = self.records[parent_id]
            if parent_rec.is_coordinator:
                reserved = self.reserved_capacity.get(parent_id, 0)
                if parent_rec.actually_spawned >= reserved:
                    return False, f"Coordinator '{parent_id}' exceeded reserved child quota ({reserved})"

        return True, "Spawn authorized within constitutional limits"

    def can_activate(self) -> Tuple[bool, str]:
        """Verifies whether a new worker can be activated concurrently."""
        if self.active_total >= self.max_active_per_wave:
            return False, f"Cannot activate: active total {self.active_total} at wave ceiling {self.max_active_per_wave}"
        return True, "Concurrency capacity available"

    def can_enter_next_wave(self, previous_wave_collapsed: bool) -> Tuple[bool, str]:
        """Enforces mandatory wave collapse before advancing."""
        if not previous_wave_collapsed:
            return False, "Previous wave has not been collapsed"
        if self.active_total > 0:
            return False, f"Cannot advance wave: {self.active_total} uncollapsed active workers remain"
        return True, "Next wave entry authorized"

    def can_retry(self, agent_id: str) -> Tuple[bool, str]:
        """Verifies whether an agent operation can be retried via new worker launch."""
        if self.remaining_budget <= 0:
            return False, "Cannot retry: mission launch budget exhausted (0 remaining)"
        return True, "Retry authorized (will consume 1 launch slot)"

    def can_delegate(self, coordinator_id: str) -> Tuple[bool, str]:
        """Verifies if a coordinator has reserved delegation capacity."""
        if coordinator_id not in self.records:
            return False, f"Unknown coordinator '{coordinator_id}'"
        rec = self.records[coordinator_id]
        if not rec.is_coordinator:
            return False, f"Agent '{coordinator_id}' is not designated as a coordinator"
        quota = self.reserved_capacity.get(coordinator_id, 0)
        if rec.actually_spawned >= quota:
            return False, f"Coordinator quota exhausted ({rec.actually_spawned}/{quota})"
        if self.remaining_budget <= 0:
            return False, "Global mission budget exhausted"
        return True, "Delegation authorized"

    def reserve_capacity(self, coordinator_id: str, quota: int) -> Tuple[bool, str]:
        """Pre-allocates a local child quota for a coordinator from unreserved global budget."""
        if quota <= 0:
            return False, "Quota must be greater than zero"
        total_reserved = sum(self.reserved_capacity.values())
        unreserved_budget = self.remaining_budget - total_reserved
        if quota > unreserved_budget:
            return False, f"Requested quota {quota} exceeds unreserved budget {unreserved_budget}"
        if quota > 4:
            return False, "Coordinator quota cannot exceed 4 to ensure shallow, bounded execution"

        self.reserved_capacity[coordinator_id] = quota
        if coordinator_id in self.records:
            self.records[coordinator_id].is_coordinator = True
            self.records[coordinator_id].reserved_quota = quota
        return True, f"Reserved {quota} child slots for coordinator '{coordinator_id}'"

    def release_capacity(self, coordinator_id: str) -> int:
        """Reverts unused coordinator quota back to the unreserved mission pool."""
        if coordinator_id not in self.reserved_capacity:
            return 0
        quota = self.reserved_capacity.pop(coordinator_id)
        actually_used = 0
        if coordinator_id in self.records:
            actually_used = self.records[coordinator_id].actually_spawned
        unused = max(0, quota - actually_used)
        return unused

    def record_spawn(
        self,
        agent_id: str,
        role: str,
        depth: int,
        wave_number: int,
        parent_id: Optional[str] = None,
        is_coordinator: bool = False,
    ) -> AgentRecord:
        """Consumes a launch slot and increments active count."""
        can_do, reason = self.can_spawn(depth=depth, parent_id=parent_id)
        if not can_do:
            raise OrchestrationBudgetExceeded(reason)

        record = AgentRecord(
            agent_id=agent_id,
            role=role,
            depth=depth,
            wave_number=wave_number,
            parent_id=parent_id,
            is_coordinator=is_coordinator,
        )
        self.records[agent_id] = record
        self.spawned_total += 1
        self.active_total += 1
        self.active_workers.append(agent_id)
        self.worker_roles[agent_id] = role
        self.current_depth = max(self.current_depth, depth)

        if parent_id and parent_id in self.records:
            self.records[parent_id].actually_spawned += 1

        return record

    def record_termination(self, agent_id: str) -> None:
        """Marks an agent as terminated, decrementing active count."""
        if agent_id in self.records and self.records[agent_id].is_active:
            self.records[agent_id].is_active = False
            self.records[agent_id].terminated_at = time.time()
            self.active_total = max(0, self.active_total - 1)
            if agent_id in self.active_workers:
                self.active_workers.remove(agent_id)
            if agent_id not in self.completed_workers and agent_id not in self.failed_workers:
                self.completed_workers.append(agent_id)

    def record_failure(self, agent_id: str, reason: str) -> None:
        """Records a worker failure."""
        if agent_id in self.records:
            self.records[agent_id].failure_reason = reason
            self.record_termination(agent_id)
            if agent_id in self.completed_workers:
                self.completed_workers.remove(agent_id)
            if agent_id not in self.failed_workers:
                self.failed_workers.append(agent_id)

    def collapse_all_active(self) -> int:
        """Aggressively collapses all active workers to 0."""
        collapsed_count = 0
        for aid in list(self.active_workers):
            if aid in self.records and self.records[aid].is_active:
                self.records[aid].is_active = False
                self.records[aid].terminated_at = time.time()
                collapsed_count += 1
                if aid not in self.collapsed_workers:
                    self.collapsed_workers.append(aid)
        self.active_workers.clear()
        self.active_total = 0
        return collapsed_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "spawned_total": self.spawned_total,
            "active_total": self.active_total,
            "remaining_budget": self.remaining_budget,
            "max_active_per_wave": self.max_active_per_wave,
            "max_total_spawned": self.max_total_spawned,
            "max_depth": self.max_depth,
            "current_wave": self.current_wave,
            "current_depth": self.current_depth,
            "active_workers": list(self.active_workers),
            "worker_roles": dict(self.worker_roles),
            "reserved_capacity": dict(self.reserved_capacity),
            "completed_workers": list(self.completed_workers),
            "failed_workers": list(self.failed_workers),
            "collapsed_workers": list(self.collapsed_workers),
        }


# Backwards compatibility alias
OrchestrationBudget = MissionLedger


@dataclass
class Wave:
    """A single bounded execution wave within a mission."""
    wave_number: int
    name: str  # RECONNAISSANCE, PLANNING, IMPLEMENTATION, VERIFICATION, DELIVERY
    state: WaveState = WaveState.INITIALIZING
    agent_ids: List[str] = field(default_factory=list)
    handoffs: List[StructuredHandoff] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    collapsed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wave_number": self.wave_number,
            "name": self.name,
            "state": self.state.value,
            "agent_ids": list(self.agent_ids),
            "handoff_count": len(self.handoffs),
            "created_at": self.created_at,
            "collapsed_at": self.collapsed_at,
        }


class WaveManager:
    """Orchestrates waves, ensuring mandatory consolidation and collapse."""

    def __init__(self, ledger: Optional[MissionLedger] = None, budget: Optional[MissionLedger] = None):
        self.ledger = ledger or budget or MissionLedger()
        self.waves: List[Wave] = []
        self.current_wave_idx: int = -1

    @property
    def budget(self) -> MissionLedger:
        """Alias for backwards compatibility."""
        return self.ledger

    @property
    def current_wave(self) -> Optional[Wave]:
        if 0 <= self.current_wave_idx < len(self.waves):
            return self.waves[self.current_wave_idx]
        return None

    def start_wave(self, name: str) -> Wave:
        """Begins a new wave. Strictly requires previous wave to be collapsed."""
        if self.current_wave and self.current_wave.state != WaveState.COLLAPSED:
            if self.ledger.active_total > 0:
                raise RuntimeError(
                    f"Cannot start wave '{name}': previous wave #{self.current_wave.wave_number} "
                    f"has {self.ledger.active_total} uncollapsed active workers."
                )
            self.current_wave.state = WaveState.COLLAPSED
            self.current_wave.collapsed_at = time.time()

        wave_num = len(self.waves) + 1
        wave = Wave(wave_number=wave_num, name=name, state=WaveState.ACTIVE)
        self.waves.append(wave)
        self.current_wave_idx = len(self.waves) - 1
        self.ledger.current_wave = wave_num
        return wave

    def spawn_worker(
        self,
        agent_id: str,
        role: str,
        depth: int = 1,
        parent_id: Optional[str] = None,
        is_coordinator: bool = False,
    ) -> AgentRecord:
        """Spawns a worker inside the current wave."""
        if not self.current_wave or self.current_wave.state != WaveState.ACTIVE:
            raise RuntimeError("Cannot spawn worker: no active wave started.")

        rec = self.ledger.record_spawn(
            agent_id=agent_id,
            role=role,
            depth=depth,
            wave_number=self.current_wave.wave_number,
            parent_id=parent_id,
            is_coordinator=is_coordinator,
        )
        self.current_wave.agent_ids.append(agent_id)
        return rec

    def record_handoff(self, agent_id: str, handoff: StructuredHandoff) -> None:
        """Records structured evidence handoff from worker and terminates it."""
        if not self.current_wave:
            raise RuntimeError("No active wave.")

        valid, errs = handoff.validate()
        if not valid:
            raise ValueError(f"Invalid handoff from '{agent_id}': {'; '.join(errs)}")

        if agent_id in self.ledger.records:
            self.ledger.records[agent_id].handoff = handoff
        self.current_wave.handoffs.append(handoff)
        self.ledger.record_termination(agent_id)

    def collapse_wave(self) -> int:
        """Collapses the current wave: active workers -> 0, state -> COLLAPSED."""
        if not self.current_wave:
            return 0

        self.current_wave.state = WaveState.CONSOLIDATING
        collapsed = self.ledger.collapse_all_active()
        self.current_wave.state = WaveState.COLLAPSED
        self.current_wave.collapsed_at = time.time()
        return collapsed


class DualDispatchGates:
    """Evaluates Gate A (Pre-Planning) and Gate B (Execution Dispatch)."""

    @staticmethod
    def evaluate_pre_planning(
        domain_count: int = 1,
        independent_lanes: int = 1,
        file_count: int = 1,
        module_count: int = 1,
        is_research_and_impl: bool = False,
        explicit_delegation_request: bool = False,
        is_high_risk_investigation: bool = False,
    ) -> DispatchGateResult:
        """Gate A: Evaluates reconnaissance delegation requirements before planning."""
        reasons: List[str] = []
        rec_workers = 0
        mode = WorkforceMode.SOLO

        # Trigger A: Multiple domains (3+)
        if domain_count >= 3:
            reasons.append(f"Touches {domain_count} distinct problem domains (Threshold >= 3)")
            rec_workers = max(rec_workers, 2)
            mode = WorkforceMode.PARALLEL

        # Trigger B: Multiple independent lanes (2+)
        if independent_lanes >= 2:
            reasons.append(f"Contains {independent_lanes} independent investigation lanes (Threshold >= 2)")
            rec_workers = max(rec_workers, 2)
            mode = WorkforceMode.PARALLEL if independent_lanes >= 3 else WorkforceMode.SMALL

        # Trigger C: Large multi-file scope (5+ files across 2+ modules)
        if file_count >= 5 and module_count >= 2:
            reasons.append(f"Touches {file_count} files across {module_count} modules (Threshold 5+ files, 2+ modules)")
            rec_workers = max(rec_workers, 2 if independent_lanes >= 2 else 1)
            mode = WorkforceMode.SMALL if independent_lanes >= 2 else WorkforceMode.FOCUSED

        # Trigger D: Substantial research + implementation
        if is_research_and_impl:
            reasons.append("Requires substantial research/investigation AND implementation")
            rec_workers = max(rec_workers, 1)
            if mode == WorkforceMode.SOLO:
                mode = WorkforceMode.FOCUSED

        # Trigger E: High-risk investigation
        if is_high_risk_investigation:
            reasons.append("High-risk or security-sensitive investigation warrants dedicated specialist")
            rec_workers = max(rec_workers, 1)
            if mode == WorkforceMode.SOLO:
                mode = WorkforceMode.FOCUSED

        # Trigger F: Explicit user delegation request
        if explicit_delegation_request:
            reasons.append("Explicit human user request for delegation/parallel execution")
            rec_workers = max(rec_workers, 2)
            mode = WorkforceMode.PARALLEL

        if reasons:
            decision = GateDecision.DELEGATION_MANDATORY
        else:
            decision = GateDecision.SOLO_AUTHORIZED
            reasons.append("Task is focused and narrow; solo reconnaissance authorized")
            rec_workers = 0
            mode = WorkforceMode.SOLO

        return DispatchGateResult(
            gate_type=DispatchGateType.PRE_PLANNING,
            decision=decision,
            mode=mode,
            recommended_workers=rec_workers,
            reasons=reasons,
            checklist={
                "domain_count": domain_count,
                "independent_lanes": independent_lanes,
                "file_count": file_count,
                "module_count": module_count,
                "is_research_and_impl": is_research_and_impl,
                "explicit_delegation_request": explicit_delegation_request,
                "is_high_risk_investigation": is_high_risk_investigation,
            },
            budget_reserved=rec_workers,
        )

    @staticmethod
    def evaluate_execution_dispatch(
        workstream_count: int = 1,
        independent_streams: int = 1,
        is_tightly_coupled: bool = False,
        file_ownership_disjoint: bool = True,
        risk_tier: str = "LOW",
        remaining_budget: int = 20,
        active_capacity: int = 10,
    ) -> DispatchGateResult:
        """Gate B: Evaluates implementation delegation requirements from approved plan."""
        reasons: List[str] = []
        rec_workers = 0
        mode = WorkforceMode.SOLO

        if remaining_budget <= 0:
            return DispatchGateResult(
                gate_type=DispatchGateType.EXECUTION_DISPATCH,
                decision=GateDecision.BLOCKED,
                mode=WorkforceMode.SOLO,
                recommended_workers=0,
                reasons=["Mission budget exhausted (0 launches remaining)"],
                checklist={"budget_available": False},
            )

        if is_tightly_coupled:
            reasons.append("Tightly coupled changes require Controlled Single Writer to prevent merge conflicts")
            mode = WorkforceMode.FOCUSED
            rec_workers = min(1, remaining_budget, active_capacity)
            decision = GateDecision.SOLO_AUTHORIZED
        elif independent_streams >= 3:
            reasons.append(f"{independent_streams} independent implementation streams justify PARALLEL execution")
            rec_workers = min(independent_streams, 4, remaining_budget, active_capacity)
            mode = WorkforceMode.PARALLEL
            decision = GateDecision.DELEGATION_MANDATORY
        elif independent_streams == 2:
            reasons.append("2 independent implementation streams mandate at least 2 workers (SOLO is forbidden)")
            rec_workers = min(2, remaining_budget, active_capacity)
            mode = WorkforceMode.SMALL
            decision = GateDecision.DELEGATION_MANDATORY
        else:
            reasons.append("Single implementation stream: controlled single writer (Parent or 1 Implementer)")
            mode = WorkforceMode.SOLO
            rec_workers = 0
            decision = GateDecision.SOLO_AUTHORIZED

        return DispatchGateResult(
            gate_type=DispatchGateType.EXECUTION_DISPATCH,
            decision=decision,
            mode=mode,
            recommended_workers=rec_workers,
            reasons=reasons,
            checklist={
                "workstream_count": workstream_count,
                "independent_streams": independent_streams,
                "is_tightly_coupled": is_tightly_coupled,
                "file_ownership_disjoint": file_ownership_disjoint,
                "risk_tier": risk_tier,
                "remaining_budget": remaining_budget,
            },
            budget_reserved=rec_workers,
        )


class WriteSafetyEvaluator:
    """Evaluates task file targets and workstreams to enforce write safety."""

    @staticmethod
    def evaluate(
        target_files: List[str],
        worker_file_assignments: Optional[Dict[str, List[str]]] = None,
        is_read_only: bool = False,
    ) -> Tuple[WriteSafetyPolicy, str]:
        """Evaluates whether concurrent writing is safe, disjoint, or unsafe."""
        if is_read_only or len(target_files) == 0:
            return WriteSafetyPolicy.READ_ONLY, "Task is read-only; zero write hazards."

        if not worker_file_assignments or len(worker_file_assignments) <= 1:
            return WriteSafetyPolicy.CONTROLLED_SINGLE_WRITER, "Single writer owns all modifications."

        seen_files: Dict[str, str] = {}
        overlaps: List[str] = []
        for worker_id, files in worker_file_assignments.items():
            for f in files:
                norm_f = f.replace("\\", "/").strip().lower()
                if norm_f in seen_files:
                    overlaps.append(f"'{norm_f}' assigned to both '{seen_files[norm_f]}' and '{worker_id}'")
                else:
                    seen_files[norm_f] = worker_id

        if overlaps:
            return (
                WriteSafetyPolicy.UNSAFE_TO_PARALLELIZE,
                f"Overlapping writers detected: {'; '.join(overlaps)}. Fallback to CONTROLLED_SINGLE_WRITER.",
            )

        return (
            WriteSafetyPolicy.SAFELY_PARALLELIZABLE,
            f"All {len(worker_file_assignments)} workers have strictly disjoint file boundaries. Use isolated workspaces.",
        )


class WorkforceSizer:
    """Deterministically sizes workforce based on task classification and risk."""

    @staticmethod
    def select_mode(
        task_class: str,
        risk_tier: str,
        pre_gate: DispatchGateResult,
        exec_gate: Optional[DispatchGateResult] = None,
    ) -> WorkforceMode:
        """Selects the authoritative WorkforceMode optimizing useful progress per token."""
        if task_class.upper() == "DOCUMENTATION" and risk_tier.upper() == "LOW":
            return WorkforceMode.SOLO

        if exec_gate:
            return exec_gate.mode

        return pre_gate.mode


def determine_coordination_level(mode: WorkforceMode, wave_count: int = 1) -> CoordinationLevel:
    """Maps workforce sizing and wave count to coordination artifact level (L0-L3)."""
    if mode == WorkforceMode.SOLO:
        return CoordinationLevel.L0
    if mode in (WorkforceMode.FOCUSED, WorkforceMode.SMALL) and wave_count <= 2:
        return CoordinationLevel.L1
    if mode in (WorkforceMode.PARALLEL, WorkforceMode.STAGED) or (wave_count >= 3 and mode not in (WorkforceMode.HIERARCHICAL, WorkforceMode.MAX)):
        return CoordinationLevel.L2
    if mode in (WorkforceMode.HIERARCHICAL, WorkforceMode.MAX):
        return CoordinationLevel.L3
    return CoordinationLevel.L1
