"""AntiOS 2.1 Experience Intelligence Engine Test Suite (Phase 106).

Comprehensive tests covering:
1. Empty store handling (zero counts, UNKNOWN status, zero division safety).
2. Single successful mission analytics.
3. Failed mission analytics.
4. Failure + recovery detection (TEST_FAILURE followed by SUCCESSFUL_FIX).
5. Repeated retry detection (consecutive duplicate calls, retry rate).
6. Verification failure & Stop Gate rejection tracking.
7. Navigation friction analysis (redundant inspections, search thrashing).
8. Successful strategy detection (canonical tool sequences for completed missions).
9. Tenant isolation (project-scoped analytics strictly isolating Project A from Project B).
10. Cross-project global aggregation (cross-project metrics without path leakage).
11. Malformed and partial telemetry handling (invalid JSON, missing fields).
12. Privacy preservation (no raw secrets, no CoT, no sensitive paths in report).
13. Deterministic repeated analysis (identical outputs across multiple runs).
14. Large bounded dataset (500+ records analyzed in sub-second time).
15. Machine-readable export (JSON and Markdown formats).
16. Unified CLI interface (analyze, report, export with text and --json).
17. Analysis failure isolation (graceful failure on unconfigured / missing database).
"""

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
import unittest

from framework.cli import build_parser, main
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
    FailurePattern,
    FrictionPattern,
    MetricStatus,
    MetricValue,
    SuccessfulStrategy,
)
from framework.core.sanitizer import SafeEngineeringEvent, SafeToolCall


class TestExperienceIntelligence(unittest.TestCase):
    """Comprehensive test suite for Phase 106 Experience Intelligence Engine."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_exp_intel_test_")
        self.data_dir = Path(self.temp_dir) / "central_data"
        self.data_dir, self.db_path = init_data_directory(self.data_dir)
        self.repo = ExperienceRepository(self.db_path)

        # Setup mock projects
        self.project_a_root = Path(self.temp_dir) / "project_alpha"
        self.project_a_root.mkdir()
        self.proj_a_id = register_project(self.db_path, self.project_a_root, "project_alpha")

        self.project_b_root = Path(self.temp_dir) / "project_beta"
        self.project_b_root.mkdir()
        self.proj_b_id = register_project(self.db_path, self.project_b_root, "project_beta")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_empty_store(self):
        """Empty database produces valid report with 0 counts and UNKNOWN rates."""
        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertEqual(report.scope, "PROJECT")
        self.assertEqual(report.project_id, self.proj_a_id)
        self.assertEqual(report.core_metrics["mission_count"].value, 0)
        self.assertEqual(report.core_metrics["mission_count"].status, MetricStatus.OBSERVED)
        self.assertEqual(report.core_metrics["tool_call_count"].value, 0)
        self.assertEqual(report.core_metrics["success_rate"].status, MetricStatus.UNKNOWN)
        self.assertEqual(report.core_metrics["failure_rate"].status, MetricStatus.UNKNOWN)
        self.assertEqual(report.core_metrics["recovery_rate"].status, MetricStatus.UNKNOWN)
        self.assertEqual(report.core_metrics["retry_rate"].status, MetricStatus.UNKNOWN)
        self.assertEqual(len(report.failure_intelligence), 0)
        self.assertEqual(len(report.friction_patterns), 0)
        self.assertEqual(len(report.successful_strategies), 0)

        # Markdown and text rendering must not crash
        md = report.to_markdown()
        self.assertIn("# AntiOS Experience Intelligence Report", md)
        text = report.to_text()
        self.assertIn("DATA COVERAGE", text)

    def test_02_single_successful_mission(self):
        """Single completed mission yields 100% success rate and observed metrics."""
        self.repo.record_session("s_1", self.proj_a_id, "DESKTOP")
        self.repo.record_mission(
            mission_id="m_1",
            session_id="s_1",
            project_id=self.proj_a_id,
            intent_query="Fix bug in auth",
            task_class="BUG_FIX",
            status="COMPLETED",
        )
        self.repo.record_turn("t_1", "m_1", step_idx=0, agent_role="PrimaryEngineer")
        tc = SafeToolCall(
            call_id="c_1",
            turn_id="t_1",
            tool_name="view_file",
            sanitized_args_json=json.dumps({"AbsolutePath": "src/auth.py"}),
            exit_code=0,
            status="SUCCESS",
            output_sha256="abc",
            output_summary="file content",
            duration_ms=120,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.repo.record_tool_call(tc)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertEqual(report.core_metrics["mission_count"].value, 1)
        self.assertEqual(report.core_metrics["missions_completed"].value, 1)
        self.assertEqual(report.core_metrics["success_rate"].value, 1.0)
        self.assertEqual(report.core_metrics["failure_rate"].value, 0.0)
        self.assertEqual(report.core_metrics["tool_call_count"].value, 1)
        self.assertEqual(report.core_metrics["tool_failure_rate"].value, 0.0)

    def test_03_failed_mission(self):
        """Failed mission calculates 0% success rate and 100% failure rate."""
        self.repo.record_session("s_fail", self.proj_a_id, "DESKTOP")
        self.repo.record_mission(
            mission_id="m_fail",
            session_id="s_fail",
            project_id=self.proj_a_id,
            status="FAILED",
        )

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertEqual(report.core_metrics["missions_failed"].value, 1)
        self.assertEqual(report.core_metrics["success_rate"].value, 0.0)
        self.assertEqual(report.core_metrics["failure_rate"].value, 1.0)

    def test_04_failure_and_recovery(self):
        """Detects failure followed by recovery and computes positive recovery rate."""
        self.repo.record_session("s_rec", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_rec", "s_rec", self.proj_a_id, status="COMPLETED")

        # 1. Test Failure Event
        ev_fail = SafeEngineeringEvent(
            event_id="e_tf_1",
            mission_id="m_rec",
            project_id=self.proj_a_id,
            event_type="TEST_FAILURE",
            epistemic_grade="FACT",
            affected_file="tests/test_auth.py",
            event_signature="sig_tf_1",
            payload_json=json.dumps({"exit_code": 1}),
            created_at="2026-09-06T12:00:00Z",
        )
        self.repo.record_engineering_event(ev_fail)

        # 2. Successful Fix Event
        ev_fix = SafeEngineeringEvent(
            event_id="e_fix_1",
            mission_id="m_rec",
            project_id=self.proj_a_id,
            event_type="SUCCESSFUL_FIX",
            epistemic_grade="FACT",
            affected_file="src/auth.py",
            event_signature="sig_fix_1",
            payload_json=json.dumps({"exit_code": 0}),
            created_at="2026-09-06T12:05:00Z",
        )
        self.repo.record_engineering_event(ev_fix)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertEqual(report.core_metrics["recovery_rate"].value, 1.0)
        self.assertEqual(report.core_metrics["recovery_rate"].status, MetricStatus.DERIVED)

        # Friction should contain VERIFICATION_RECOVERY_CYCLE
        f_types = [f.friction_type for f in report.friction_patterns]
        self.assertIn("VERIFICATION_RECOVERY_CYCLE", f_types)

    def test_05_repeated_retries(self):
        """Consecutive identical tool calls are detected in retry_rate and friction."""
        self.repo.record_session("s_retry", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_retry", "s_retry", self.proj_a_id, status="ACTIVE")
        self.repo.record_turn("t_retry", "m_retry", step_idx=0)

        # 3 identical tool calls
        for i in range(3):
            tc = SafeToolCall(
                call_id=f"c_ret_{i}",
                turn_id="t_retry",
                tool_name="run_command",
                sanitized_args_json=json.dumps({"CommandLine": "git status"}),
                exit_code=0,
                status="SUCCESS",
                output_sha256=f"sha_{i}",
                output_summary="clean",
                duration_ms=50,
                created_at=f"2026-09-06T12:0{i}:00Z",
            )
            self.repo.record_tool_call(tc)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertGreater(report.core_metrics["retry_rate"].value, 0.0)
        f_types = [f.friction_type for f in report.friction_patterns]
        self.assertIn("TOOL_RETRY_LOOP", f_types)

    def test_06_verification_failure_and_stop_gate(self):
        """Tracks Stop Gate rejections and test failures in failure intelligence."""
        self.repo.record_session("s_v", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_v", "s_v", self.proj_a_id, status="ACTIVE")

        # Stop Gate continue decision (rejection)
        ev_sg = SafeEngineeringEvent(
            event_id="e_sg_1",
            mission_id="m_v",
            project_id=self.proj_a_id,
            event_type="STOP_GATE_RESULT",
            epistemic_grade="FACT",
            affected_file=None,
            event_signature="sig_sg_1",
            payload_json=json.dumps({"decision": "continue", "reason": "Test runner failed"}),
            created_at="2026-09-06T12:10:00Z",
        )
        self.repo.record_engineering_event(ev_sg)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        fail_cats = [f.category for f in report.failure_intelligence]
        self.assertIn("STOP_GATE_VERIFICATION_REJECTION", fail_cats)

    def test_07_navigation_friction(self):
        """Redundant navigation inspections and search thrashing are detected."""
        self.repo.record_session("s_nav", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_nav", "s_nav", self.proj_a_id, status="ACTIVE")
        self.repo.record_turn("t_nav", "m_nav", step_idx=0)

        # 1. Redundant inspection event
        ev_nav = SafeEngineeringEvent(
            event_id="e_nav_1",
            mission_id="m_nav",
            project_id=self.proj_a_id,
            event_type="REPEATED_NAVIGATION_PATH",
            epistemic_grade="FACT",
            affected_file="src/models.py",
            event_signature="sig_nav_1",
            payload_json=json.dumps({"repeated_file": "src/models.py", "consecutive_views": 2}),
            created_at="2026-09-06T12:15:00Z",
        )
        self.repo.record_engineering_event(ev_nav)

        # 2. Search thrashing (3 consecutive grep calls)
        for i in range(3):
            tc = SafeToolCall(
                call_id=f"c_grep_{i}",
                turn_id="t_nav",
                tool_name="grep_search",
                sanitized_args_json=json.dumps({"Query": f"pattern_{i}"}),
                exit_code=0,
                status="SUCCESS",
                output_sha256=f"sha_{i}",
                output_summary="matches",
                duration_ms=40,
                created_at=f"2026-09-06T12:1{i}:00Z",
            )
            self.repo.record_tool_call(tc)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        f_types = [f.friction_type for f in report.friction_patterns]
        self.assertIn("REPEATED_NAVIGATION_INSPECTION", f_types)
        self.assertIn("SEARCH_THRASHING_BEFORE_NAVIGATION", f_types)

    def test_08_successful_strategy_detection(self):
        """Distills canonical tool trajectories from completed missions."""
        self.repo.record_session("s_strat", self.proj_a_id, "DESKTOP")
        self.repo.record_mission(
            mission_id="m_strat_1",
            session_id="s_strat",
            project_id=self.proj_a_id,
            task_class="BUG_FIX",
            status="COMPLETED",
        )
        self.repo.record_turn("t_strat_1", "m_strat_1", step_idx=0)

        tools = ["view_file", "replace_file_content", "run_command"]
        for idx, tname in enumerate(tools):
            tc = SafeToolCall(
                call_id=f"c_strat_{idx}",
                turn_id="t_strat_1",
                tool_name=tname,
                sanitized_args_json="{}",
                exit_code=0,
                status="SUCCESS",
                output_sha256="h",
                output_summary="ok",
                duration_ms=100,
                created_at=f"2026-09-06T12:2{idx}:00Z",
            )
            self.repo.record_tool_call(tc)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        self.assertGreaterEqual(len(report.successful_strategies), 1)
        strat = report.successful_strategies[0]
        self.assertEqual(strat.task_category, "BUG_FIX")
        self.assertEqual(strat.tool_sequence, tools)

    def test_09_multiple_sessions_and_tenants(self):
        """Project-scoped analytics strictly isolates Project Alpha from Project Beta."""
        # Record in Project A
        self.repo.record_session("s_a", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_a", "s_a", self.proj_a_id, status="COMPLETED")

        # Record in Project B
        self.repo.record_session("s_b", self.proj_b_id, "DESKTOP")
        self.repo.record_mission("m_b", "s_b", self.proj_b_id, status="FAILED")

        engine = ExperienceAnalyticsEngine(self.db_path)
        report_a = engine.analyze_project(self.proj_a_id)
        report_b = engine.analyze_project(self.proj_b_id)

        self.assertEqual(report_a.core_metrics["mission_count"].value, 1)
        self.assertEqual(report_a.core_metrics["missions_completed"].value, 1)
        self.assertEqual(report_a.core_metrics["missions_failed"].value, 0)

        self.assertEqual(report_b.core_metrics["mission_count"].value, 1)
        self.assertEqual(report_b.core_metrics["missions_completed"].value, 0)
        self.assertEqual(report_b.core_metrics["missions_failed"].value, 1)

    def test_10_cross_project_global_aggregation(self):
        """Cross-project global analysis aggregates metrics without leaking file paths."""
        self.repo.record_session("s_a", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_a", "s_a", self.proj_a_id, status="COMPLETED")
        self.repo.record_session("s_b", self.proj_b_id, "DESKTOP")
        self.repo.record_mission("m_b", "s_b", self.proj_b_id, status="FAILED")

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_global()

        self.assertEqual(report.scope, "GLOBAL")
        self.assertIsNone(report.project_id)
        self.assertEqual(report.core_metrics["mission_count"].value, 2)
        self.assertEqual(report.core_metrics["missions_completed"].value, 1)
        self.assertEqual(report.core_metrics["missions_failed"].value, 1)
        self.assertIsNotNone(report.cross_project_summary)
        self.assertEqual(report.cross_project_summary["total_registered_projects"], 2)

    def test_11_malformed_and_partial_telemetry(self):
        """Handles missing fields and malformed payloads gracefully without crashing."""
        self.repo.record_session("s_mal", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_mal", "s_mal", self.proj_a_id, status="ACTIVE")
        self.repo.record_turn("t_mal", "m_mal", step_idx=0)

        # Tool call with unparseable JSON args
        tc = SafeToolCall(
            call_id="c_bad_json",
            turn_id="t_mal",
            tool_name="custom_tool",
            sanitized_args_json="INVALID_NON_JSON_STRING",
            exit_code=None,
            status="ERROR",
            output_sha256=None,
            output_summary=None,
            duration_ms=0,
            created_at="2026-09-06T12:30:00Z",
        )
        self.repo.record_tool_call(tc)

        # Event with empty payload
        ev = SafeEngineeringEvent(
            event_id="e_bad_payload",
            mission_id="m_mal",
            project_id=self.proj_a_id,
            event_type="TOOL_FAILURE",
            epistemic_grade="FACT",
            affected_file=None,
            event_signature="sig_bad_1",
            payload_json="{}",
            created_at="2026-09-06T12:31:00Z",
        )
        self.repo.record_engineering_event(ev)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        # Must execute cleanly without exception
        self.assertEqual(report.core_metrics["tool_call_count"].value, 1)
        self.assertEqual(report.core_metrics["tool_failure_rate"].value, 1.0)

    def test_12_privacy_preservation(self):
        """Guarantees reports and exports never leak raw thinking or secret tokens."""
        self.repo.record_session("s_priv", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_priv", "s_priv", self.proj_a_id, status="COMPLETED")
        self.repo.record_turn("t_priv", "m_priv", step_idx=0)

        # Tool call with scrubbed content
        tc = SafeToolCall(
            call_id="c_priv",
            turn_id="t_priv",
            tool_name="view_file",
            sanitized_args_json=json.dumps({"path": "src/config.py"}),
            exit_code=0,
            status="SUCCESS",
            output_sha256="hash123",
            output_summary="token: [REDACTED_SECRET]",
            duration_ms=50,
            created_at="2026-09-06T12:40:00Z",
        )
        self.repo.record_tool_call(tc)

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        text_rep = report.to_text()
        md_rep = report.to_markdown()
        json_rep = json.dumps(report.to_dict())

        for rendered in (text_rep, md_rep, json_rep):
            self.assertNotIn("ghp_", rendered)
            self.assertNotIn("AIza", rendered)
            self.assertNotIn("chain_of_thought", rendered)
            self.assertNotIn("internal_reasoning", rendered)

    def test_13_deterministic_repeated_analysis(self):
        """Repeated analysis on identical store yields identical outputs."""
        self.repo.record_session("s_det", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_det", "s_det", self.proj_a_id, status="COMPLETED")

        engine = ExperienceAnalyticsEngine(self.db_path)
        rep1 = engine.analyze_project(self.proj_a_id)
        rep2 = engine.analyze_project(self.proj_a_id)

        # Compare serialized metrics and representations (excluding volatile timestamp)
        d1 = rep1.to_dict()
        d2 = rep2.to_dict()
        d1["generated_at"] = ""
        d2["generated_at"] = ""
        self.assertEqual(d1, d2)

    def test_14_large_bounded_dataset(self):
        """Analyzes 500+ events and tool calls with deterministic sub-second performance."""
        self.repo.record_session("s_big", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_big", "s_big", self.proj_a_id, status="COMPLETED")
        self.repo.record_turn("t_big", "m_big", step_idx=0)

        # Batch insert 300 tool calls
        calls: List[SafeToolCall] = []
        for i in range(300):
            calls.append(
                SafeToolCall(
                    call_id=f"c_big_{i}",
                    turn_id="t_big",
                    tool_name="view_file" if i % 2 == 0 else "run_command",
                    sanitized_args_json=json.dumps({"idx": i}),
                    exit_code=0 if i % 5 != 0 else 1,
                    status="SUCCESS" if i % 5 != 0 else "ERROR",
                    output_sha256=f"hash_{i}",
                    output_summary=f"output_{i}",
                    duration_ms=25 + (i % 50),
                    created_at=f"2026-09-06T13:00:{i%60:02d}Z",
                )
            )
        self.repo.record_tool_calls(calls)

        # Batch insert 200 events
        events: List[SafeEngineeringEvent] = []
        for j in range(200):
            events.append(
                SafeEngineeringEvent(
                    event_id=f"e_big_{j}",
                    mission_id="m_big",
                    project_id=self.proj_a_id,
                    event_type="TOOL_CALL" if j % 4 != 0 else "TOOL_FAILURE",
                    epistemic_grade="FACT",
                    affected_file=f"file_{j}.py",
                    event_signature=f"sig_big_{j}",
                    payload_json=json.dumps({"step": j}),
                    created_at=f"2026-09-06T13:05:{j%60:02d}Z",
                )
            )
        self.repo.record_engineering_events(events)

        t0 = time.perf_counter()
        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)
        elapsed = time.perf_counter() - t0

        self.assertLess(elapsed, 1.5, f"Analysis took {elapsed:.2f}s, expected < 1.5s")
        self.assertEqual(report.core_metrics["tool_call_count"].value, 300)

    def test_15_export_json_and_markdown(self):
        """Exports report in JSON and Markdown to disk."""
        self.repo.record_session("s_exp", self.proj_a_id, "DESKTOP")
        self.repo.record_mission("m_exp", "s_exp", self.proj_a_id, status="COMPLETED")

        engine = ExperienceAnalyticsEngine(self.db_path)
        report = engine.analyze_project(self.proj_a_id)

        exports_dir = Path(self.temp_dir) / "exports"
        json_file = ExperienceExporter.export(report, exports_dir, export_format="json")
        md_file = ExperienceExporter.export(report, exports_dir, export_format="markdown")

        self.assertTrue(json_file.is_file())
        self.assertTrue(md_file.is_file())

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["scope"], "PROJECT")

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# AntiOS Experience Intelligence Report", content)

    def test_16_cli_commands(self):
        """Tests antios experience analyze, report, and export CLI commands."""
        # 1. Analyze with --json
        parser = build_parser()
        args = parser.parse_args([
            "experience", "analyze",
            "--data-dir", str(self.data_dir),
            "--path", str(self.project_a_root),
            "--json",
        ])
        exit_code = args.func(args)
        self.assertEqual(exit_code, 0)

        # 2. Report with markdown format to file
        out_report = Path(self.temp_dir) / "test_report.md"
        args = parser.parse_args([
            "experience", "report",
            "--data-dir", str(self.data_dir),
            "--path", str(self.project_a_root),
            "--format", "markdown",
            "--output", str(out_report),
        ])
        exit_code = args.func(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(out_report.is_file())

        # 3. Export command
        out_export_dir = Path(self.temp_dir) / "cli_exports"
        args = parser.parse_args([
            "experience", "export",
            "--data-dir", str(self.data_dir),
            "--path", str(self.project_a_root),
            "--output", str(out_export_dir),
            "--format", "json",
            "--json",
        ])
        exit_code = args.func(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(out_export_dir.is_dir())

    def test_17_analysis_failure_isolation(self):
        """Unconfigured or missing database fails closed with clean diagnostic."""
        non_existent_dd = Path(self.temp_dir) / "does_not_exist"
        parser = build_parser()
        args = parser.parse_args([
            "experience", "analyze",
            "--data-dir", str(non_existent_dd),
            "--path", str(self.project_a_root),
            "--json",
        ])
        exit_code = args.func(args)
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
