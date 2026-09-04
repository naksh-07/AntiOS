"""AntiOS 2.0 Constitutional Orchestration Engine.

Codifies the Antigravity-native orchestration constitution inspired by
the Adaptive Orchestrator research:
- Hard Constitutional Limits:
    MAX_ACTIVE_AGENTS_PER_WAVE = 10
    MAX_TOTAL_SPAWNED_AGENTS = 20 (across entire delegation tree)
    MAX_DELEGATION_DEPTH = 2 (Shallow Depth Law: Parent -> Subagent)
- Wave Lifecycle:
    WAVE -> DISCOVER/INVESTIGATE -> CONSOLIDATE -> COLLAPSE -> NEXT WAVE
- Invariant:
    No next wave may spawn until the previous wave has:
    - results consolidated
    - state persisted
    - workers terminated (active total = 0)
    - budget reconciled
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class OrchestrationBudgetExceeded(Exception):
    """Raised when an operation attempts to exceed constitutional agent limits."""
    pass


class WaveState(str, Enum):
    """State of an execution wave."""
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    CONSOLIDATING = "CONSOLIDATING"
    COLLAPSED = "COLLAPSED"


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


@dataclass
class OrchestrationBudget:
    """Global shared budget across the entire delegation tree."""
    max_active_per_wave: int = 10
    max_total_spawned: int = 20
    max_depth: int = 2
    spawned_total: int = 0
    active_total: int = 0
    records: Dict[str, AgentRecord] = field(default_factory=dict)

    @property
    def remaining_budget(self) -> int:
        return max(0, self.max_total_spawned - self.spawned_total)

    def can_spawn(self, depth: int = 1) -> Tuple[bool, str]:
        """Pre-spawn gate verifying all constitutional constraints."""
        if depth > self.max_depth:
            return False, f"Shallow Depth Law violation: depth {depth} exceeds max depth {self.max_depth}"
        if self.spawned_total >= self.max_total_spawned:
            return False, f"Constitutional ceiling reached: spawned {self.spawned_total}/{self.max_total_spawned} total agents"
        if self.active_total >= self.max_active_per_wave:
            return False, f"Wave concurrency limit reached: active {self.active_total}/{self.max_active_per_wave} agents"
        return True, "Spawn authorized within constitutional limits"

    def record_spawn(self, agent_id: str, role: str, depth: int, wave_number: int) -> AgentRecord:
        """Consumes a launch slot and increments active count."""
        can_do, reason = self.can_spawn(depth=depth)
        if not can_do:
            raise OrchestrationBudgetExceeded(reason)

        record = AgentRecord(
            agent_id=agent_id,
            role=role,
            depth=depth,
            wave_number=wave_number,
        )
        self.records[agent_id] = record
        self.spawned_total += 1
        self.active_total += 1
        return record

    def record_termination(self, agent_id: str) -> None:
        """Marks an agent as terminated, decrementing active count."""
        if agent_id in self.records and self.records[agent_id].is_active:
            self.records[agent_id].is_active = False
            self.records[agent_id].terminated_at = time.time()
            self.active_total = max(0, self.active_total - 1)

    def collapse_all_active(self) -> int:
        """Aggressively collapses all active agents to 0."""
        collapsed_count = 0
        for rec in self.records.values():
            if rec.is_active:
                rec.is_active = False
                rec.terminated_at = time.time()
                collapsed_count += 1
        self.active_total = 0
        return collapsed_count


@dataclass
class Wave:
    """A single bounded execution wave within a mission."""
    wave_number: int
    name: str  # DISCOVER, INVESTIGATE, IMPLEMENT, VERIFY, CONSOLIDATE
    state: WaveState = WaveState.INITIALIZING
    agent_ids: List[str] = field(default_factory=list)
    handoffs: List[StructuredHandoff] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    collapsed_at: Optional[float] = None


class WaveManager:
    """Orchestrates waves, ensuring mandatory consolidation and collapse."""

    def __init__(self, budget: Optional[OrchestrationBudget] = None):
        self.budget = budget or OrchestrationBudget()
        self.waves: List[Wave] = []
        self.current_wave_idx: int = -1

    @property
    def current_wave(self) -> Optional[Wave]:
        if 0 <= self.current_wave_idx < len(self.waves):
            return self.waves[self.current_wave_idx]
        return None

    def start_wave(self, name: str) -> Wave:
        """Begins a new wave. Strictly requires previous wave to be collapsed."""
        if self.current_wave and self.current_wave.state != WaveState.COLLAPSED:
            # Check if active count is 0
            if self.budget.active_total > 0:
                raise RuntimeError(
                    f"Cannot start wave '{name}': previous wave #{self.current_wave.wave_number} "
                    f"has {self.budget.active_total} uncollapsed active workers."
                )
            self.current_wave.state = WaveState.COLLAPSED
            self.current_wave.collapsed_at = time.time()

        wave_num = len(self.waves) + 1
        wave = Wave(wave_number=wave_num, name=name, state=WaveState.ACTIVE)
        self.waves.append(wave)
        self.current_wave_idx = len(self.waves) - 1
        return wave

    def spawn_worker(self, agent_id: str, role: str, depth: int = 1) -> AgentRecord:
        """Spawns a worker inside the current wave."""
        if not self.current_wave or self.current_wave.state != WaveState.ACTIVE:
            raise RuntimeError("Cannot spawn worker: no active wave started.")

        rec = self.budget.record_spawn(
            agent_id=agent_id,
            role=role,
            depth=depth,
            wave_number=self.current_wave.wave_number,
        )
        self.current_wave.agent_ids.append(agent_id)
        return rec

    def record_handoff(self, agent_id: str, handoff: StructuredHandoff) -> None:
        """Records structured evidence handoff from worker and terminates it."""
        if not self.current_wave:
            raise RuntimeError("No active wave.")

        if agent_id in self.budget.records:
            self.budget.records[agent_id].handoff = handoff
        self.current_wave.handoffs.append(handoff)
        self.budget.record_termination(agent_id)

    def collapse_wave(self) -> int:
        """Collapses the current wave: active workers -> 0, state -> COLLAPSED."""
        if not self.current_wave:
            return 0

        self.current_wave.state = WaveState.CONSOLIDATING
        collapsed = self.budget.collapse_all_active()
        self.current_wave.state = WaveState.COLLAPSED
        self.current_wave.collapsed_at = time.time()
        return collapsed
