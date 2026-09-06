"""AntiOS 2.1 Architectural Boundary & Separation Test Suite (Phase 106).

CRITICAL NON-MUTATION CONTRACT:
Verifies and proves that executing Experience Intelligence (System B):
1. NEVER mutates learning observations (.antios/learning_observations.json).
2. NEVER mutates learning proposals (.antios/learning_proposals.json).
3. NEVER mutates project memory (docs/ACTIVE_CONTEXT.md, docs/HISTORICAL_RECORD.md).
4. NEVER mutates project knowledge (docs/PROJECT_KNOWLEDGE.md).
5. NEVER mutates decisions (DECISION_REGISTER.md).
6. NEVER mutates lessons (docs/LESSONS.md).
7. NEVER mutates durable proofs (.antios/proofs/proofs.json).
8. NEVER mutates project configuration (antios.config.json, .antios/manifest.json).
9. NEVER mutates skills, rules, or governance state (.agents/).
10. NEVER imports or invokes write methods in framework/core/learning.py or framework/core/memory.py.
11. NEVER writes database files or analysis caches into the target project repository.
"""

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from framework.cli import build_parser
from framework.core.experience import (
    AntiOSDataResolver,
    ExperienceRepository,
    init_data_directory,
    init_experience_db,
    register_project,
)
from framework.core.experience_analytics import (
    ExperienceAnalyticsEngine,
    ExperienceExporter,
    ExperienceReport,
)
from framework.core.sanitizer import SafeEngineeringEvent, SafeToolCall


def compute_tree_checksums(root_dir: Path) -> dict[str, str]:
    """Computes SHA-256 hash for every file in the directory tree."""
    checksums: dict[str, str] = {}
    for p in sorted(root_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(root_dir)).replace("\\", "/")
            with open(p, "rb") as f:
                checksums[rel] = hashlib.sha256(f.read()).hexdigest()
    return checksums


class TestExperienceLearningSeparation(unittest.TestCase):
    """Rigorous verification of the absolute separation between System A and System B."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_separation_test_")
        self.data_dir = Path(self.temp_dir) / "central_data"
        self.data_dir, self.db_path = init_data_directory(self.data_dir)
        self.repo = ExperienceRepository(self.db_path)

        # Setup populated target project
        self.proj_root = Path(self.temp_dir) / "target_project"
        self.proj_root.mkdir()
        (self.proj_root / "docs").mkdir()
        (self.proj_root / ".antios" / "proofs").mkdir(parents=True)
        (self.proj_root / ".agents" / "skills").mkdir(parents=True)
        (self.proj_root / ".agents" / "rules").mkdir(parents=True)

        # Seed System A Project Learning & Memory files
        self.active_context_file = self.proj_root / "docs" / "ACTIVE_CONTEXT.md"
        self.active_context_file.write_text("# Active Context\nInitial context line 1.\n", encoding="utf-8")

        self.project_knowledge_file = self.proj_root / "docs" / "PROJECT_KNOWLEDGE.md"
        self.project_knowledge_file.write_text("# Project Knowledge\n## Verified Facts\n- Initial fact.\n", encoding="utf-8")

        self.decision_register_file = self.proj_root / "DECISION_REGISTER.md"
        self.decision_register_file.write_text("# Decision Register\nADR-001: Initial Architecture\n", encoding="utf-8")

        self.lessons_file = self.proj_root / "docs" / "LESSONS.md"
        self.lessons_file.write_text("# Project Lessons\n## Durable Lessons\n- Lesson 1\n", encoding="utf-8")

        self.historical_record_file = self.proj_root / "docs" / "HISTORICAL_RECORD.md"
        self.historical_record_file.write_text("# Historical Record\nMilestone 1 completed.\n", encoding="utf-8")

        self.obs_file = self.proj_root / ".antios" / "learning_observations.json"
        self.obs_file.write_text(json.dumps({"schema": "2.0.0", "observations": []}), encoding="utf-8")

        self.prop_file = self.proj_root / ".antios" / "learning_proposals.json"
        self.prop_file.write_text(json.dumps({"schema": "2.0.0", "proposals": []}), encoding="utf-8")

        self.proofs_file = self.proj_root / ".antios" / "proofs" / "proofs.json"
        self.proofs_file.write_text(json.dumps({"schema": "2.0.0", "proofs": []}), encoding="utf-8")

        self.config_file = self.proj_root / "antios.config.json"
        self.config_file.write_text(json.dumps({
            "version": "2.0.0",
            "data_dir": str(self.data_dir),
            "telemetry": {"enabled": True, "mode": "ON"},
        }, indent=2), encoding="utf-8")

        self.manifest_file = self.proj_root / ".antios" / "manifest.json"
        self.manifest_file.write_text(json.dumps({
            "metadata": {"project_id": "proj_sep_test", "data_dir": str(self.data_dir)},
            "managed_paths": {},
        }, indent=2), encoding="utf-8")

        self.rule_file = self.proj_root / ".agents" / "rules" / "core_rules.md"
        self.rule_file.write_text("# Protected Rule\nDo not break invariants.\n", encoding="utf-8")

        self.skill_file = self.proj_root / ".agents" / "skills" / "SKILL.md"
        self.skill_file.write_text("# Test Skill\nSkill definition.\n", encoding="utf-8")

        self.proj_id = register_project(self.db_path, self.proj_root, "target_project")

        # Seed rich telemetry in System B
        self.repo.record_session("s_sep", self.proj_id, "DESKTOP")
        self.repo.record_mission("m_sep_1", "s_sep", self.proj_id, task_class="BUG_FIX", status="COMPLETED")
        self.repo.record_mission("m_sep_2", "s_sep", self.proj_id, task_class="FEATURE", status="FAILED")
        self.repo.record_turn("t_sep_1", "m_sep_1", step_idx=0)
        self.repo.record_turn("t_sep_2", "m_sep_2", step_idx=0)

        tc1 = SafeToolCall(
            call_id="c_sep_1",
            turn_id="t_sep_1",
            tool_name="view_file",
            sanitized_args_json=json.dumps({"path": "src/main.py"}),
            exit_code=0,
            status="SUCCESS",
            output_sha256="abc",
            output_summary="main file",
            duration_ms=80,
            created_at="2026-09-06T14:00:00Z",
        )
        tc2 = SafeToolCall(
            call_id="c_sep_2",
            turn_id="t_sep_2",
            tool_name="run_command",
            sanitized_args_json=json.dumps({"cmd": "pytest"}),
            exit_code=1,
            status="ERROR",
            output_sha256="def",
            output_summary="failure",
            duration_ms=250,
            created_at="2026-09-06T14:01:00Z",
        )
        self.repo.record_tool_calls([tc1, tc2])

        ev1 = SafeEngineeringEvent(
            event_id="e_sep_1",
            mission_id="m_sep_2",
            project_id=self.proj_id,
            event_type="TEST_FAILURE",
            epistemic_grade="FACT",
            affected_file="tests/test_main.py",
            event_signature="sig_sep_1",
            payload_json=json.dumps({"exit_code": 1}),
            created_at="2026-09-06T14:02:00Z",
        )
        self.repo.record_engineering_event(ev1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_cryptographic_non_mutation_proof(self):
        """Proves byte-for-byte immutability of the entire target project tree across all operations."""
        # 1. Capture exact cryptographic snapshot of all project files before analysis
        before_checksums = compute_tree_checksums(self.proj_root)

        # 2. Execute all Experience Intelligence operations
        engine = ExperienceAnalyticsEngine(self.db_path)
        report_proj = engine.analyze_project(self.proj_id)
        report_glob = engine.analyze_global()

        exports_dir = self.data_dir / "exports"
        ExperienceExporter.export(report_proj, exports_dir, export_format="json")
        ExperienceExporter.export(report_proj, exports_dir, export_format="markdown")
        ExperienceExporter.export(report_glob, exports_dir, export_format="json")

        # 3. Execute all CLI commands targeting the project
        parser = build_parser()
        args_analyze = parser.parse_args(["experience", "analyze", "--data-dir", str(self.data_dir), "--path", str(self.proj_root), "--json"])
        self.assertEqual(args_analyze.func(args_analyze), 0)

        args_report = parser.parse_args(["experience", "report", "--data-dir", str(self.data_dir), "--path", str(self.proj_root), "--format", "markdown"])
        self.assertEqual(args_report.func(args_report), 0)

        args_export = parser.parse_args(["experience", "export", "--data-dir", str(self.data_dir), "--path", str(self.proj_root), "--json"])
        self.assertEqual(args_export.func(args_export), 0)

        # 4. Capture cryptographic snapshot after all operations
        after_checksums = compute_tree_checksums(self.proj_root)

        # 5. Assert 100% identical tree state: No files added, no files deleted, zero bit changes
        self.assertEqual(
            before_checksums.keys(),
            after_checksums.keys(),
            f"Project file tree was altered! Added/removed: {set(before_checksums.keys()) ^ set(after_checksums.keys())}",
        )

        for rel_path, before_sha in before_checksums.items():
            after_sha = after_checksums[rel_path]
            self.assertEqual(
                before_sha,
                after_sha,
                f"File '{rel_path}' was mutated during Experience Intelligence execution! Before: {before_sha}, After: {after_sha}",
            )

    def test_02_no_learning_memory_imports_in_analytics(self):
        """Verifies that experience_analytics.py does NOT import learning.py or memory.py."""
        analytics_module_path = Path("framework/core/experience_analytics.py").resolve()
        with open(analytics_module_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Strict code check: must not import learning, memory, evidence, or project_proof
        forbidden_imports = [
            "framework.core.learning",
            "from framework.core.learning",
            "import framework.core.learning",
            "framework.core.memory",
            "from framework.core.memory",
            "import framework.core.memory",
            "EvidencePromotionEngine",
            "LearningEngine",
            "LessonDistillationEngine",
            "ProjectMemoryManager",
            "ControlledEvolutionGovernor",
        ]
        for fi in forbidden_imports:
            self.assertNotIn(
                fi,
                code,
                f"experience_analytics.py contains forbidden import/reference '{fi}' violating System A vs B separation!",
            )

    def test_03_zero_database_files_in_project_repo(self):
        """Verifies INV-10: zero SQLite database files or WAL journals exist inside project root."""
        engine = ExperienceAnalyticsEngine(self.db_path)
        engine.analyze_project(self.proj_id)

        # Scan project root for any .db, .db-wal, or .db-shm files
        db_files = list(self.proj_root.rglob("*.db*")) + list(self.proj_root.rglob("*.sqlite*"))
        self.assertEqual(
            db_files,
            [],
            f"Found forbidden database files inside project root: {db_files}",
        )


if __name__ == "__main__":
    unittest.main()
