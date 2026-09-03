"""AntiOS Persistent Project Memory Model & Knowledge Authority Engine.

Formalizes 5 memory categories, knowledge authority progression, write policies,
and 100% transparent markdown serialization with zero vector databases and zero external services.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import os
import re
from typing import Any, Dict, List, Optional, Tuple


class MemoryCategory(str, Enum):
    """The 5 persistent memory tiers of AntiOS."""
    ACTIVE_STATE = "ACTIVE_STATE"             # Operational ledger: docs/ACTIVE_CONTEXT.md
    PROJECT_KNOWLEDGE = "PROJECT_KNOWLEDGE"   # Stable architecture/tooling facts: docs/PROJECT_KNOWLEDGE.md
    DECISIONS = "DECISIONS"                   # Architectural decisions: DECISION_REGISTER.md
    LESSONS = "LESSONS"                       # Failure lessons & candidate improvements: docs/LESSONS.md
    HISTORICAL_RECORD = "HISTORICAL_RECORD"   # Milestones & completed tasks: docs/HISTORICAL_RECORD.md


MEMORY_CATEGORY_DOCS: Dict[MemoryCategory, str] = {
    MemoryCategory.ACTIVE_STATE: "docs/ACTIVE_CONTEXT.md",
    MemoryCategory.PROJECT_KNOWLEDGE: "docs/PROJECT_KNOWLEDGE.md",
    MemoryCategory.DECISIONS: "DECISION_REGISTER.md",
    MemoryCategory.LESSONS: "docs/LESSONS.md",
    MemoryCategory.HISTORICAL_RECORD: "docs/HISTORICAL_RECORD.md",
}


class KnowledgeAuthority(str, Enum):
    """Progression of epistemic authority in AntiOS memory."""
    OBSERVED = "OBSERVED"     # Physical filesystem/manifest evidence (weight 1.0)
    CANDIDATE = "CANDIDATE"   # Provisional hypothesis, single failure, or temporary observation
    VALIDATED = "VALIDATED"   # Verified across 2+ runs or backed by independent verification verdict
    DURABLE = "DURABLE"       # Permanently committed into version-controlled knowledge documents


AUTHORITY_WEIGHTS: Dict[KnowledgeAuthority, float] = {
    KnowledgeAuthority.OBSERVED: 1.0,
    KnowledgeAuthority.CANDIDATE: 0.3,
    KnowledgeAuthority.VALIDATED: 0.8,
    KnowledgeAuthority.DURABLE: 1.0,
}


@dataclass
class MemoryRecord:
    """Generic memory record representing an observation, fact, or milestone."""
    category: MemoryCategory
    authority: KnowledgeAuthority
    content: str
    source: str = ""
    timestamp: str = ""
    is_ephemeral: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectKnowledgeFact:
    """Stable architecture, toolchain, or runtime fact in docs/PROJECT_KNOWLEDGE.md."""
    fact_id: str
    topic: str
    fact: str
    authority: KnowledgeAuthority = KnowledgeAuthority.VALIDATED
    source: str = ""
    last_verified: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionRecord:
    """Architectural decision recorded in DECISION_REGISTER.md."""
    decision_id: str
    title: str
    decision: str
    evidence: str = ""
    alternatives: str = ""
    why_selected: str = ""
    consequences: str = ""
    reversibility: str = ""
    authority: KnowledgeAuthority = KnowledgeAuthority.DURABLE
    date: str = ""
    status: str = "Authoritative Architectural Consensus"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LessonRecord:
    """Failure lesson or improvement proposal in docs/LESSONS.md."""
    lesson_id: str
    title: str
    trigger_or_failure: str
    rule_or_action: str
    authority: KnowledgeAuthority = KnowledgeAuthority.CANDIDATE
    evidence: str = ""
    date: str = ""
    category: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def promote_to_durable(
        self,
        evidence: str,
        authority: KnowledgeAuthority = KnowledgeAuthority.VALIDATED
    ) -> None:
        """Promotes a candidate lesson to durable status upon multi-run or verified evidence."""
        if authority not in (KnowledgeAuthority.VALIDATED, KnowledgeAuthority.DURABLE):
            raise ValueError("Lessons can only be promoted to VALIDATED or DURABLE authority.")
        self.authority = authority
        if evidence:
            self.evidence = f"{self.evidence}; {evidence}".strip("; ") if self.evidence else evidence


@dataclass
class HistoricalRecord:
    """Milestone or completed task in docs/HISTORICAL_RECORD.md."""
    record_id: str
    title: str
    description: str
    date: str = ""
    authority: KnowledgeAuthority = KnowledgeAuthority.DURABLE
    artifacts: List[str] = field(default_factory=list)
    verification_summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryWritePolicy:
    """Enforces write permissions and authority progression across memory tiers."""

    DURABLE_CATEGORIES = {
        MemoryCategory.PROJECT_KNOWLEDGE,
        MemoryCategory.DECISIONS,
        MemoryCategory.LESSONS,
        MemoryCategory.HISTORICAL_RECORD,
    }

    @staticmethod
    def can_write(
        category: MemoryCategory,
        authority: KnowledgeAuthority,
        is_ephemeral: bool = False,
        target_section: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Determines whether a fact or observation can be written to the specified memory category.

        Rules:
        1. is_ephemeral=True observations are strictly rejected from all durable categories
           (PROJECT_KNOWLEDGE, DECISIONS, LESSONS, HISTORICAL_RECORD).
        2. CANDIDATE facts cannot be written directly to PROJECT_KNOWLEDGE or DECISIONS
           without reaching VALIDATED or DURABLE authority.
        3. For LESSONS, CANDIDATE lessons are allowed in a dedicated "Candidate Improvements"
           section, but require VALIDATED (or DURABLE) for promotion to "Durable Lessons".
        4. For HISTORICAL_RECORD, CANDIDATE facts cannot be written without reaching VALIDATED or DURABLE.
        5. ACTIVE_STATE accepts observations of any authority and ephemeral status.
        """
        # Rule 1: Ephemeral observations cannot enter durable documents
        if is_ephemeral and category in MemoryWritePolicy.DURABLE_CATEGORIES:
            return False, f"Ephemeral observations cannot be written to durable category '{category.value}'."

        # Rule 5: Active state is the operational working ledger
        if category == MemoryCategory.ACTIVE_STATE:
            return True, "Permitted in ACTIVE_STATE operational ledger."

        # Rule 2: Project Knowledge & Decisions require non-candidate authority
        if category in (MemoryCategory.PROJECT_KNOWLEDGE, MemoryCategory.DECISIONS):
            if authority == KnowledgeAuthority.CANDIDATE:
                return False, (
                    f"CANDIDATE facts cannot be written directly to {category.value} "
                    f"without reaching VALIDATED or DURABLE authority."
                )
            return True, f"Authority '{authority.value}' permitted in {category.value}."

        # Rule 4: Historical records are permanent completed milestones
        if category == MemoryCategory.HISTORICAL_RECORD:
            if authority == KnowledgeAuthority.CANDIDATE:
                return False, (
                    "CANDIDATE facts cannot be written directly to HISTORICAL_RECORD "
                    "without reaching VALIDATED or DURABLE authority."
                )
            return True, f"Authority '{authority.value}' permitted in HISTORICAL_RECORD."

        # Rule 3: Lessons partition candidates from durable lessons
        if category == MemoryCategory.LESSONS:
            sec = (target_section or "").strip().lower()
            if "durable" in sec:
                if authority == KnowledgeAuthority.CANDIDATE:
                    return False, (
                        "Candidate lessons require VALIDATED or DURABLE authority for promotion "
                        "to Durable Lessons."
                    )
                return True, f"Authority '{authority.value}' permitted in Durable Lessons."
            elif "candidate" in sec:
                return True, "CANDIDATE lessons permitted in Candidate Improvements section."
            else:
                # Default: candidates allowed in Candidate section, validated in either
                if authority == KnowledgeAuthority.CANDIDATE:
                    return True, "CANDIDATE lessons permitted in Candidate Improvements section."
                return True, f"Authority '{authority.value}' permitted in LESSONS."

        return True, "Write permitted."

    @staticmethod
    def can_promote(
        current_authority: KnowledgeAuthority,
        target_authority: KnowledgeAuthority
    ) -> Tuple[bool, str]:
        """Validates progression between authority levels."""
        progression_order = {
            KnowledgeAuthority.CANDIDATE: 1,
            KnowledgeAuthority.OBSERVED: 2,
            KnowledgeAuthority.VALIDATED: 3,
            KnowledgeAuthority.DURABLE: 4,
        }
        curr_lvl = progression_order.get(current_authority, 0)
        tgt_lvl = progression_order.get(target_authority, 0)

        if tgt_lvl <= curr_lvl:
            return False, f"Cannot promote from {current_authority.value} to {target_authority.value} (target level must be higher)."

        return True, f"Promotion from {current_authority.value} to {target_authority.value} is valid."


# --- Serialization & Markdown Parsers ---

def format_project_knowledge(facts: List[ProjectKnowledgeFact], title: str = "Project Knowledge") -> str:
    """Serializes ProjectKnowledgeFacts into transparent markdown."""
    lines = [
        f"# {title} (`docs/PROJECT_KNOWLEDGE.md`)",
        "",
        "**Status**: Verified Architecture & Tooling Knowledge  ",
        "**Authority**: OBSERVED, VALIDATED, or DURABLE facts only  ",
        "",
    ]
    facts_by_topic: Dict[str, List[ProjectKnowledgeFact]] = {}
    for f in facts:
        facts_by_topic.setdefault(f.topic or "General Architecture", []).append(f)

    for topic, topic_facts in sorted(facts_by_topic.items()):
        lines.append(f"## {topic}")
        lines.append("")
        for f in topic_facts:
            lines.append(f"### [{f.fact_id}] {f.fact}")
            lines.append(f"- **Authority**: {f.authority.value}")
            if f.source:
                lines.append(f"- **Source**: {f.source}")
            if f.last_verified:
                lines.append(f"- **Last Verified**: {f.last_verified}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def parse_project_knowledge(content_or_path: str) -> List[ProjectKnowledgeFact]:
    """Parses docs/PROJECT_KNOWLEDGE.md content or file into ProjectKnowledgeFacts."""
    text = content_or_path
    if os.path.isfile(content_or_path):
        with open(content_or_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

    facts: List[ProjectKnowledgeFact] = []
    current_topic = "General Architecture"

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## ") and not line.startswith("### "):
            current_topic = line.replace("## ", "").strip()
            i += 1
            continue

        if line.startswith("### "):
            header = line.replace("### ", "").strip()
            id_match = re.match(r"\[([^\]]+)\]\s*(.*)", header)
            if id_match:
                fact_id = id_match.group(1).strip()
                fact_desc = id_match.group(2).strip()
            else:
                fact_id = f"PK-{len(facts)+1:02d}"
                fact_desc = header

            authority = KnowledgeAuthority.VALIDATED
            source = ""
            last_verified = ""

            i += 1
            while i < len(lines) and not lines[i].strip().startswith("##"):
                sub = lines[i].strip()
                auth_match = re.search(r"-\s*\*\*Authority\*\*:\s*([A-Z_]+)", sub)
                if auth_match and auth_match.group(1) in KnowledgeAuthority.__members__:
                    authority = KnowledgeAuthority(auth_match.group(1))

                src_match = re.search(r"-\s*\*\*Source\*\*:\s*(.*)", sub)
                if src_match:
                    source = src_match.group(1).strip()

                ver_match = re.search(r"-\s*\*\*Last Verified\*\*:\s*(.*)", sub)
                if ver_match:
                    last_verified = ver_match.group(1).strip()

                i += 1

            facts.append(ProjectKnowledgeFact(
                fact_id=fact_id,
                topic=current_topic,
                fact=fact_desc,
                authority=authority,
                source=source,
                last_verified=last_verified,
            ))
            continue

        i += 1

    return facts


def sync_project_knowledge(facts: List[ProjectKnowledgeFact], repo_root: str) -> str:
    """Writes ProjectKnowledgeFacts to docs/PROJECT_KNOWLEDGE.md."""
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    target_path = os.path.join(docs_dir, "PROJECT_KNOWLEDGE.md")
    content = format_project_knowledge(facts)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path


def format_lessons(lessons: List[LessonRecord]) -> str:
    """Serializes LessonRecords into transparent markdown with Candidate vs Durable sections."""
    lines = [
        "# Project Lessons & Improvements (`docs/LESSONS.md`)",
        "",
        "**Status**: Active Failure Prevention & Validated Patterns  ",
        "**Format**: Candidate hypotheses remain provisional until validated across multiple runs.  ",
        "",
        "## 1. Candidate Improvements",
        "",
    ]
    candidates = [l for l in lessons if l.authority == KnowledgeAuthority.CANDIDATE]
    if not candidates:
        lines.append("- None currently recorded.")
        lines.append("")
    else:
        for c in candidates:
            lines.append(f"### [{c.lesson_id}] {c.title}")
            lines.append(f"- **Trigger/Failure**: {c.trigger_or_failure}")
            lines.append(f"- **Rule/Action**: {c.rule_or_action}")
            lines.append(f"- **Authority**: {c.authority.value}")
            if c.evidence:
                lines.append(f"- **Evidence**: {c.evidence}")
            if c.date:
                lines.append(f"- **Date**: {c.date}")
            if c.category:
                lines.append(f"- **Category**: {c.category}")
            lines.append("")

    lines.append("## 2. Durable Lessons")
    lines.append("")
    durable = [l for l in lessons if l.authority != KnowledgeAuthority.CANDIDATE]
    if not durable:
        lines.append("- None currently recorded.")
        lines.append("")
    else:
        for d in durable:
            lines.append(f"### [{d.lesson_id}] {d.title}")
            lines.append(f"- **Trigger/Failure**: {d.trigger_or_failure}")
            lines.append(f"- **Rule/Action**: {d.rule_or_action}")
            lines.append(f"- **Authority**: {d.authority.value}")
            if d.evidence:
                lines.append(f"- **Evidence**: {d.evidence}")
            if d.date:
                lines.append(f"- **Date**: {d.date}")
            if d.category:
                lines.append(f"- **Category**: {d.category}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def parse_lessons(content_or_path: str) -> List[LessonRecord]:
    """Parses docs/LESSONS.md content or file into LessonRecords."""
    text = content_or_path
    if os.path.isfile(content_or_path):
        with open(content_or_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

    lessons: List[LessonRecord] = []
    current_section = "candidate"

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            sec_lower = line.lower()
            if "durable" in sec_lower:
                current_section = "durable"
            elif "candidate" in sec_lower:
                current_section = "candidate"
            i += 1
            continue

        if line.startswith("### "):
            header = line.replace("### ", "").strip()
            id_match = re.match(r"\[([^\]]+)\]\s*(.*)", header)
            if id_match:
                lesson_id = id_match.group(1).strip()
                title = id_match.group(2).strip()
            else:
                lesson_id = f"L-{len(lessons)+1:02d}"
                title = header

            default_auth = KnowledgeAuthority.DURABLE if current_section == "durable" else KnowledgeAuthority.CANDIDATE
            authority = default_auth
            trigger = ""
            action = ""
            evidence = ""
            date_str = ""
            category_str = ""

            i += 1
            while i < len(lines) and not lines[i].strip().startswith("##"):
                sub = lines[i].strip()
                trig_match = re.search(r"-\s*\*\*(?:Trigger/Failure|Failure|Trigger)\*\*:\s*(.*)", sub)
                if trig_match:
                    trigger = trig_match.group(1).strip()

                act_match = re.search(r"-\s*\*\*(?:Rule/Action|Action|Resolution|Rule)\*\*:\s*(.*)", sub)
                if act_match:
                    action = act_match.group(1).strip()

                auth_match = re.search(r"-\s*\*\*Authority\*\*:\s*([A-Z_]+)", sub)
                if auth_match and auth_match.group(1) in KnowledgeAuthority.__members__:
                    authority = KnowledgeAuthority(auth_match.group(1))

                ev_match = re.search(r"-\s*\*\*Evidence\*\*:\s*(.*)", sub)
                if ev_match:
                    evidence = ev_match.group(1).strip()

                dt_match = re.search(r"-\s*\*\*Date\*\*:\s*(.*)", sub)
                if dt_match:
                    date_str = dt_match.group(1).strip()

                cat_match = re.search(r"-\s*\*\*Category\*\*:\s*(.*)", sub)
                if cat_match:
                    category_str = cat_match.group(1).strip()

                i += 1

            lessons.append(LessonRecord(
                lesson_id=lesson_id,
                title=title,
                trigger_or_failure=trigger,
                rule_or_action=action,
                authority=authority,
                evidence=evidence,
                date=date_str,
                category=category_str,
            ))
            continue

        i += 1

    return lessons


def sync_lessons(lessons: List[LessonRecord], repo_root: str) -> str:
    """Writes LessonRecords to docs/LESSONS.md."""
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    target_path = os.path.join(docs_dir, "LESSONS.md")
    content = format_lessons(lessons)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path


def format_historical_record(records: List[HistoricalRecord], title: str = "Project Historical Record") -> str:
    """Serializes HistoricalRecords into transparent markdown."""
    lines = [
        f"# {title} (`docs/HISTORICAL_RECORD.md`)",
        "",
        "**Status**: Permanent Task & Milestone Archive  ",
        "**Authority**: Verified completed work and milestones.  ",
        "",
        "## Milestones & Completed Tasks",
        "",
    ]
    if not records:
        lines.append("- No completed milestones recorded.")
        lines.append("")
    else:
        for r in records:
            lines.append(f"### [{r.record_id}] {r.title}")
            lines.append(f"- **Description**: {r.description}")
            lines.append(f"- **Authority**: {r.authority.value}")
            if r.date:
                lines.append(f"- **Date**: {r.date}")
            if r.verification_summary:
                lines.append(f"- **Verification**: {r.verification_summary}")
            if r.artifacts:
                lines.append(f"- **Artifacts**: {', '.join(r.artifacts)}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def parse_historical_record(content_or_path: str) -> List[HistoricalRecord]:
    """Parses docs/HISTORICAL_RECORD.md content or file into HistoricalRecords."""
    text = content_or_path
    if os.path.isfile(content_or_path):
        with open(content_or_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

    records: List[HistoricalRecord] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("### "):
            header = line.replace("### ", "").strip()
            id_match = re.match(r"\[([^\]]+)\]\s*(.*)", header)
            if id_match:
                rec_id = id_match.group(1).strip()
                title = id_match.group(2).strip()
            else:
                rec_id = f"M-{len(records)+1:02d}"
                title = header

            description = ""
            authority = KnowledgeAuthority.DURABLE
            date_str = ""
            verification = ""
            artifacts: List[str] = []

            i += 1
            while i < len(lines) and not lines[i].strip().startswith("##"):
                sub = lines[i].strip()
                desc_match = re.search(r"-\s*\*\*Description\*\*:\s*(.*)", sub)
                if desc_match:
                    description = desc_match.group(1).strip()

                auth_match = re.search(r"-\s*\*\*Authority\*\*:\s*([A-Z_]+)", sub)
                if auth_match and auth_match.group(1) in KnowledgeAuthority.__members__:
                    authority = KnowledgeAuthority(auth_match.group(1))

                dt_match = re.search(r"-\s*\*\*Date\*\*:\s*(.*)", sub)
                if dt_match:
                    date_str = dt_match.group(1).strip()

                ver_match = re.search(r"-\s*\*\*Verification\*\*:\s*(.*)", sub)
                if ver_match:
                    verification = ver_match.group(1).strip()

                art_match = re.search(r"-\s*\*\*Artifacts\*\*:\s*(.*)", sub)
                if art_match:
                    art_val = art_match.group(1).strip()
                    artifacts = [a.strip() for a in art_val.split(",") if a.strip()]

                i += 1

            records.append(HistoricalRecord(
                record_id=rec_id,
                title=title,
                description=description,
                date=date_str,
                authority=authority,
                artifacts=artifacts,
                verification_summary=verification,
            ))
            continue

        i += 1

    return records


def sync_historical_record(records: List[HistoricalRecord], repo_root: str) -> str:
    """Writes HistoricalRecords to docs/HISTORICAL_RECORD.md."""
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    target_path = os.path.join(docs_dir, "HISTORICAL_RECORD.md")
    content = format_historical_record(records)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path


def format_decision_register(decisions: List[DecisionRecord], date_str: str = "2026-09-04") -> str:
    """Serializes DecisionRecords to DECISION_REGISTER.md format."""
    lines = [
        "# AntiOS Master Decision Register (`DECISION_REGISTER.md`)",
        "",
        f"**Date**: {date_str}  ",
        "**Status**: Authoritative Architectural Consensus  ",
        "**Format**: Every decision records `DECISION`, `EVIDENCE`, `ALTERNATIVES`, `WHY SELECTED`, `CONSEQUENCES`, and `REVERSIBILITY`.",
        "",
        "---",
        "",
    ]
    for d in decisions:
        lines.append(f"## {d.decision_id}: {d.title}")
        lines.append(f"- **DECISION**: {d.decision}")
        lines.append(f"- **EVIDENCE**: {d.evidence}")
        lines.append(f"- **ALTERNATIVES**: {d.alternatives}")
        lines.append(f"- **WHY SELECTED**: {d.why_selected}")
        lines.append(f"- **CONSEQUENCES**: {d.consequences}")
        lines.append(f"- **REVERSIBILITY**: {d.reversibility}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def parse_decision_register(content_or_path: str) -> List[DecisionRecord]:
    """Parses DECISION_REGISTER.md content or file into DecisionRecords."""
    text = content_or_path
    if os.path.isfile(content_or_path):
        with open(content_or_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

    decisions: List[DecisionRecord] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## ") and not line.startswith("### "):
            header = line.replace("## ", "").strip()
            if ":" in header:
                parts = header.split(":", 1)
                decision_id = parts[0].strip()
                title = parts[1].strip()
            else:
                decision_id = header
                title = header

            decision_text = ""
            evidence = ""
            alternatives = ""
            why_selected = ""
            consequences = ""
            reversibility = ""

            i += 1
            while i < len(lines) and not lines[i].strip().startswith("## ") and not lines[i].strip().startswith("# "):
                sub = lines[i].strip()
                dec_match = re.search(r"-\s*\*\*DECISION\*\*:\s*(.*)", sub)
                if dec_match:
                    decision_text = dec_match.group(1).strip()

                ev_match = re.search(r"-\s*\*\*EVIDENCE\*\*:\s*(.*)", sub)
                if ev_match:
                    evidence = ev_match.group(1).strip()

                alt_match = re.search(r"-\s*\*\*ALTERNATIVES\*\*:\s*(.*)", sub)
                if alt_match:
                    alternatives = alt_match.group(1).strip()

                why_match = re.search(r"-\s*\*\*WHY SELECTED\*\*:\s*(.*)", sub)
                if why_match:
                    why_selected = why_match.group(1).strip()

                csq_match = re.search(r"-\s*\*\*CONSEQUENCES\*\*:\s*(.*)", sub)
                if csq_match:
                    consequences = csq_match.group(1).strip()

                rev_match = re.search(r"-\s*\*\*REVERSIBILITY\*\*:\s*(.*)", sub)
                if rev_match:
                    reversibility = rev_match.group(1).strip()

                i += 1

            if decision_text or title:
                decisions.append(DecisionRecord(
                    decision_id=decision_id,
                    title=title,
                    decision=decision_text,
                    evidence=evidence,
                    alternatives=alternatives,
                    why_selected=why_selected,
                    consequences=consequences,
                    reversibility=reversibility,
                    authority=KnowledgeAuthority.DURABLE,
                ))
            continue

        i += 1

    return decisions


def sync_decision_register(decisions: List[DecisionRecord], repo_root: str, date_str: str = "2026-09-04") -> str:
    """Writes DecisionRecords to DECISION_REGISTER.md at repo root."""
    target_path = os.path.join(repo_root, "DECISION_REGISTER.md")
    content = format_decision_register(decisions, date_str=date_str)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path
