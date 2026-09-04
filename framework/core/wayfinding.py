"""AntiOS Component Wayfinding & Locality Engine.

Provides deterministic architectural navigation and locality resolution:
resolves task intent, queries, or file paths into authoritative subsystem
manifests, entrypoints, covering test suites, invariants, and blast radius.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from framework.core.subsystem import SubsystemDeclaration


@dataclass(frozen=True)
class LocalityResolution:
    """The structured wayfinding resolution returned to an agent."""
    query: str
    matched_subsystem_id: str
    confidence: float
    area: str
    name: str
    description: str
    entrypoints: List[str]
    authoritative_files: List[str]
    covering_tests: List[str]
    test_commands: List[str]
    applicable_skills: List[str]
    applicable_workflows: List[str]
    governing_rules: List[str]
    protected_invariants: List[str]
    dependencies: List[str]
    consumers: List[str]
    documentation_paths: List[str]
    blast_radius_summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Converts resolution to dictionary."""
        return asdict(self)


class WayfindingEngine:
    """Deterministic repository wayfinding and architectural locality engine."""

    def __init__(self, workspace_root: str = ""):
        self.workspace_root = os.path.normcase(os.path.abspath(workspace_root)) if workspace_root else ""
        self._subsystems: Dict[str, SubsystemDeclaration] = {}
        self._path_to_subsystem: List[Tuple[str, str]] = []  # (prefix, subsystem_id) sorted by length desc
        self._keyword_index: Dict[str, Set[str]] = {}

    def register_subsystem(self, decl: SubsystemDeclaration) -> None:
        """Registers a subsystem declaration and updates inverted indices."""
        sub_id = decl.subsystem_id.lower()
        self._subsystems[sub_id] = decl

        # Register root paths and specific files
        all_paths = decl.root_paths + decl.entrypoints + decl.authoritative_files + decl.covering_tests
        for p in all_paths:
            norm_p = p.replace("\\", "/").lower().strip("/")
            if norm_p:
                self._path_to_subsystem.append((norm_p, sub_id))

        # Re-sort path index so longest prefixes match first
        self._path_to_subsystem.sort(key=lambda x: len(x[0]), reverse=True)

        # Index keywords
        all_tokens = set(decl.keywords)
        all_tokens.add(decl.subsystem_id.lower())
        all_tokens.add(decl.name.lower())
        all_tokens.add(decl.area.lower())
        # Add words from description
        desc_words = re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", decl.description.lower())
        all_tokens.update(desc_words)

        for token in all_tokens:
            token_clean = token.strip().lower()
            if len(token_clean) >= 2:
                if token_clean not in self._keyword_index:
                    self._keyword_index[token_clean] = set()
                self._keyword_index[token_clean].add(sub_id)

    def get_subsystem(self, subsystem_id: str) -> Optional[SubsystemDeclaration]:
        """Retrieves a subsystem declaration by ID."""
        return self._subsystems.get(subsystem_id.lower())

    def list_subsystems(self) -> List[SubsystemDeclaration]:
        """Returns all registered subsystem declarations."""
        return list(self._subsystems.values())

    def resolve_file(self, file_path: str) -> Optional[LocalityResolution]:
        """Resolves a file path to its owning subsystem using longest prefix matching."""
        if not file_path or not isinstance(file_path, str):
            return None

        clean_path = file_path.strip()
        if self.workspace_root and os.path.isabs(clean_path):
            try:
                rel = os.path.relpath(clean_path, self.workspace_root)
                clean_path = rel
            except ValueError:
                pass

        norm_path = clean_path.replace("\\", "/").lower().strip("/")

        # Check path prefix matches
        for prefix, sub_id in self._path_to_subsystem:
            if norm_path == prefix or norm_path.startswith(prefix + "/"):
                decl = self._subsystems.get(sub_id)
                if decl:
                    return self._build_resolution(query=file_path, decl=decl, confidence=1.0)

        return None

    def locate(self, query: str) -> Optional[LocalityResolution]:
        """Determines the most relevant subsystem from a query string.
        
        Query can be:
        1. An exact subsystem ID
        2. A file or directory path
        3. Natural language keywords / intent tokens
        """
        if not query or not isinstance(query, str) or not query.strip():
            return None

        clean_query = query.strip()

        # 1. Check exact subsystem ID
        q_lower = clean_query.lower()
        if q_lower in self._subsystems:
            return self._build_resolution(query=clean_query, decl=self._subsystems[q_lower], confidence=1.0)

        # 2. Check if query is a file path
        if "/" in clean_query or "\\" in clean_query or "." in clean_query:
            file_res = self.resolve_file(clean_query)
            if file_res:
                return file_res

        # 3. Token-based ranking over keyword index
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", q_lower)
        if not tokens:
            return None

        scores: Dict[str, float] = {sub_id: 0.0 for sub_id in self._subsystems}

        for token in tokens:
            # Check direct keyword hits
            if token in self._keyword_index:
                for sub_id in self._keyword_index[token]:
                    decl = self._subsystems[sub_id]
                    # Score weights
                    if token in [k.lower() for k in decl.keywords]:
                        scores[sub_id] += 3.0
                    elif token == decl.subsystem_id.lower():
                        scores[sub_id] += 4.0
                    elif token in decl.name.lower():
                        scores[sub_id] += 2.5
                    elif token == decl.area.lower():
                        scores[sub_id] += 1.5
                    else:
                        scores[sub_id] += 1.0

            # Substring matching in subsystem IDs or root paths
            for sub_id, decl in self._subsystems.items():
                if token in sub_id:
                    scores[sub_id] += 2.0
                for rp in decl.root_paths:
                    if token in rp.lower():
                        scores[sub_id] += 1.5

        if not scores:
            return None

        best_sub_id, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score <= 0.0:
            return None

        decl = self._subsystems[best_sub_id]
        confidence = min(0.95, round(best_score / (len(tokens) * 3.0), 2))
        confidence = max(0.40, confidence)

        return self._build_resolution(query=clean_query, decl=decl, confidence=confidence)

    def _build_resolution(
        self, query: str, decl: SubsystemDeclaration, confidence: float
    ) -> LocalityResolution:
        """Constructs a LocalityResolution from a matched SubsystemDeclaration."""
        # Calculate blast radius summary
        deps_count = len(decl.dependencies)
        cons_count = len(decl.consumers)
        if cons_count > 3:
            blast = f"CRITICAL: {cons_count} downstream consumers ({', '.join(decl.consumers[:3])}...)"
        elif cons_count > 0:
            blast = f"MODERATE: {cons_count} downstream consumers ({', '.join(decl.consumers)})"
        else:
            blast = "ISOLATED: Leaf component with 0 downstream consumers"

        return LocalityResolution(
            query=query,
            matched_subsystem_id=decl.subsystem_id,
            confidence=confidence,
            area=decl.area,
            name=decl.name,
            description=decl.description,
            entrypoints=decl.entrypoints,
            authoritative_files=decl.authoritative_files,
            covering_tests=decl.covering_tests,
            test_commands=decl.test_commands,
            applicable_skills=decl.applicable_skills,
            applicable_workflows=decl.applicable_workflows,
            governing_rules=decl.governing_rules,
            protected_invariants=decl.protected_invariants,
            dependencies=decl.dependencies,
            consumers=decl.consumers,
            documentation_paths=decl.documentation_paths,
            blast_radius_summary=blast,
        )

    def format_locator_card(self, resolution: LocalityResolution) -> str:
        """Renders a compact, high-density <= 20 line summary for agent context injection."""
        ep_str = ", ".join(resolution.entrypoints[:3]) if resolution.entrypoints else "None registered"
        key_str = ", ".join(resolution.authoritative_files[:3]) if resolution.authoritative_files else "None registered"
        test_str = ", ".join(resolution.covering_tests[:3]) if resolution.covering_tests else "None registered"
        cmd_str = "; ".join(resolution.test_commands[:2]) if resolution.test_commands else "None registered"
        rules_str = "; ".join(resolution.governing_rules[:2]) if resolution.governing_rules else "Standard project rules"
        inv_str = ", ".join(resolution.protected_invariants[:2]) if resolution.protected_invariants else "None"
        doc_str = ", ".join(resolution.documentation_paths[:2]) if resolution.documentation_paths else "docs/ACTIVE_CONTEXT.md"

        card = [
            "=== ANTIOS WAYFINDING LOCATOR ===",
            f"Query:       {resolution.query} (Confidence: {resolution.confidence:.2f})",
            f"Subsystem:   {resolution.matched_subsystem_id} ({resolution.name}) [Area: {resolution.area}]",
            f"Description: {resolution.description}",
            f"Entrypoints: {ep_str}",
            f"Key Files:   {key_str}",
            f"Tests:       {test_str}",
            f"Runners:     {cmd_str}",
            f"Skills:      {', '.join(resolution.applicable_skills)} | Workflows: {', '.join(resolution.applicable_workflows)}",
            f"Invariants:  Immutable: {inv_str}",
            f"Rules:       {rules_str}",
            f"Radius:      {resolution.blast_radius_summary}",
            f"Docs:        {doc_str}",
            "=================================",
        ]
        return "\n".join(card)
