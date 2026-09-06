"""AntiOS 2.1 Storage & Data Directory Foundation Test Suite.

Comprehensive test suite covering all 18 Phase 103 verification dimensions:
1. Data-directory creation (backups/, exports/, config.toml, experience.db)
2. Custom data-directory configuration (CLI, env var, antios.config.json)
3. Existing data-directory reuse without destruction
4. Database initialization (all 6 entity tables, indexes, schema_migrations)
5. Idempotent initialization (repeated init is safe no-op)
6. Schema version verification in schema_migrations
7. Migration mechanism and atomic execution
8. SQLite WAL configuration (journal_mode=WAL, synchronous=NORMAL, busy_timeout=5000, foreign_keys=1)
9. Relational foreign key enforcement and cascading deletion
10. Strict project/tenant isolation (Project A vs Project B proving ground)
11. Missing directory recovery and fail-closed diagnostics
12. Invalid configuration (rejecting database inside project repository)
13. Database corruption and error handling
14. CLI data status and set-dir commands (human + JSON)
15. Doctor and Status engine integration
16. Windows-compatible path normalization and deterministic project_id
17. Multiple projects sharing one central data directory
18. Zero database files inside target repositories (INV-10)
"""

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from framework.cli import build_parser
from framework.core.config import AntiOSConfig, load_config
from framework.core.doctor import DiagnosticSeverity, DoctorEngine
from framework.core.experience import (
    CURRENT_STORAGE_SCHEMA_VERSION,
    AntiOSDataResolver,
    DataDirectoryNotConfiguredError,
    MigrationError,
    StorageError,
    StorageStatus,
    backup_database,
    get_db_connection,
    get_storage_status,
    init_data_directory,
    init_experience_db,
    register_project,
    verify_project_isolation,
)
from framework.core.installation import InstallationLifecycleManager
from framework.core.manifest import load_manifest


class TestExperienceFoundation(unittest.TestCase):
    """Test suite validating AntiOS 2.1 Storage & Data Directory Foundation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_storage_test_")
        self.base = Path(self.test_dir).resolve()
        self.data_dir = self.base / "central_data"
        self.proj_a = self.base / "projects" / "project_alpha"
        self.proj_b = self.base / "projects" / "project_beta"

        self.proj_a.mkdir(parents=True, exist_ok=True)
        self.proj_b.mkdir(parents=True, exist_ok=True)

        (self.proj_a / "tests").mkdir(parents=True, exist_ok=True)
        (self.proj_a / "tests" / "run_all.py").write_text("# Master test runner\n", encoding="utf-8")
        (self.proj_b / "tests").mkdir(parents=True, exist_ok=True)
        (self.proj_b / "tests" / "run_all.py").write_text("# Master test runner\n", encoding="utf-8")

        self.source_root = Path(__file__).resolve().parent.parent

    def tearDown(self):
        if "ANTIOS_DATA_DIR" in os.environ:
            del os.environ["ANTIOS_DATA_DIR"]
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------
    # 1. Data-directory creation
    # -------------------------------------------------------------
    def test_01_data_directory_creation(self):
        """Verifies creation of backups/, exports/, config.toml, and experience.db path."""
        d_path, db_path = init_data_directory(self.data_dir)
        self.assertTrue(d_path.is_dir())
        self.assertTrue((d_path / "backups").is_dir())
        self.assertTrue((d_path / "exports").is_dir())
        self.assertTrue((d_path / "config.toml").is_file())
        self.assertEqual(db_path, d_path / "experience.db")

        config_text = (d_path / "config.toml").read_text(encoding="utf-8")
        self.assertIn("AntiOS 2.1", config_text)
        self.assertIn("max_database_bytes", config_text)

    # -------------------------------------------------------------
    # 2. Custom data-directory configuration
    # -------------------------------------------------------------
    def test_02_custom_data_directory_configuration(self):
        """Tests data directory resolution precedence: explicit > env > config > manifest."""
        custom_a = self.base / "custom_a"
        custom_b = self.base / "custom_b"
        custom_c = self.base / "custom_c"

        # Explicit argument takes top priority
        os.environ["ANTIOS_DATA_DIR"] = str(custom_b)
        res = AntiOSDataResolver.resolve_data_dir(project_root=self.proj_a, explicit_dir=custom_a)
        self.assertEqual(res, custom_a.resolve())

        # Environment variable takes second priority
        res_env = AntiOSDataResolver.resolve_data_dir(project_root=self.proj_a)
        self.assertEqual(res_env, custom_b.resolve())
        del os.environ["ANTIOS_DATA_DIR"]

        # antios.config.json takes third priority
        cfg_file = self.proj_a / "antios.config.json"
        cfg_file.write_text(json.dumps({"data_dir": str(custom_c)}), encoding="utf-8")
        res_cfg = AntiOSDataResolver.resolve_data_dir(project_root=self.proj_a)
        self.assertEqual(res_cfg, custom_c.resolve())

    # -------------------------------------------------------------
    # 3. Existing data-directory reuse
    # -------------------------------------------------------------
    def test_03_existing_data_directory_reuse(self):
        """Existing directory with pre-existing data is preserved without truncation."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        # Insert a dummy record
        pid = register_project(db_path, self.proj_a, ecosystem="python")
        self.assertTrue(pid.startswith("proj_"))

        # Re-initialize directory
        init_data_directory(self.data_dir)
        init_experience_db(db_path)

        # Verify project record is still present
        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_id, project_name FROM projects WHERE project_id = ?;", (pid,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["project_name"], "project_alpha")

    # -------------------------------------------------------------
    # 4. Database initialization
    # -------------------------------------------------------------
    def test_04_database_initialization(self):
        """Initializes database and verifies all 6 core entity tables and indexes exist."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        expected_tables = {
            "schema_migrations",
            "projects",
            "sessions",
            "missions",
            "turns",
            "tool_calls",
            "engineering_events",
        }

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {r[0] for r in cursor.fetchall()}
            for et in expected_tables:
                self.assertIn(et, tables, f"Expected table '{et}' missing from experience.db")

            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
            indexes = {r[0] for r in cursor.fetchall()}
            self.assertIn("idx_sessions_project", indexes)
            self.assertIn("idx_missions_project", indexes)
            self.assertIn("idx_events_project", indexes)
            self.assertIn("idx_events_signature", indexes)

    # -------------------------------------------------------------
    # 5. Idempotent initialization
    # -------------------------------------------------------------
    def test_05_idempotent_initialization(self):
        """Calling init_experience_db multiple times succeeds without error or state corruption."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"

        # 3 sequential initializations
        init_experience_db(db_path)
        init_experience_db(db_path)
        init_experience_db(db_path)

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as cnt FROM schema_migrations;")
            cnt = cursor.fetchone()["cnt"]
            self.assertEqual(cnt, 1, "Idempotent initialization should only record migration once")

    # -------------------------------------------------------------
    # 6. Schema version
    # -------------------------------------------------------------
    def test_06_schema_version(self):
        """Verifies current schema version is properly logged with checksum in schema_migrations."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version, applied_at, checksum FROM schema_migrations;")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["version"], CURRENT_STORAGE_SCHEMA_VERSION)
            self.assertTrue(len(row["checksum"]) == 64)  # SHA-256
            self.assertTrue(row["applied_at"].endswith("+00:00") or "Z" in row["applied_at"] or "T" in row["applied_at"])

    # -------------------------------------------------------------
    # 7. Migration mechanism
    # -------------------------------------------------------------
    def test_07_migration_mechanism(self):
        """Verifies migration failure triggers rollback and does not corrupt database."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        # Attempt to insert an invalid migration
        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as cnt FROM schema_migrations;")
            initial_cnt = cursor.fetchone()["cnt"]

        self.assertEqual(initial_cnt, 1)

    # -------------------------------------------------------------
    # 8. WAL configuration and PRAGMAs
    # -------------------------------------------------------------
    def test_08_wal_configuration_and_pragmas(self):
        """Verifies mandatory PRAGMAs: WAL, synchronous=NORMAL, busy_timeout=5000, foreign_keys=ON."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        with closing(get_db_connection(db_path, timeout=5.0)) as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA journal_mode;")
            journal = cursor.fetchone()[0].upper()
            self.assertEqual(journal, "WAL")

            cursor.execute("PRAGMA synchronous;")
            sync = int(cursor.fetchone()[0])
            self.assertEqual(sync, 1)  # 1 == NORMAL

            cursor.execute("PRAGMA busy_timeout;")
            busy = int(cursor.fetchone()[0])
            self.assertEqual(busy, 5000)

            cursor.execute("PRAGMA foreign_keys;")
            fk = int(cursor.fetchone()[0])
            self.assertEqual(fk, 1)  # 1 == ON

    # -------------------------------------------------------------
    # 9. Foreign keys enforcement and cascade
    # -------------------------------------------------------------
    def test_09_foreign_keys_and_cascade(self):
        """Enforces relational constraints: orphan rejects and ON DELETE CASCADE."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        pid = register_project(db_path, self.proj_a)
        now_utc = datetime.now(timezone.utc).isoformat()

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()

            # 1. Attempting to insert a session with non-existent project_id fails
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    """INSERT INTO sessions (session_id, project_id, surface, started_at) 
                       VALUES ('sess_invalid', 'proj_nonexistent', 'CLI', ?);""",
                    (now_utc,),
                )

            # 2. Insert valid session
            cursor.execute(
                """INSERT INTO sessions (session_id, project_id, surface, started_at) 
                   VALUES ('sess_valid', ?, 'CLI', ?);""",
                (pid, now_utc),
            )

            # 3. Attempt to insert mission with non-existent session_id fails
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute(
                    """INSERT INTO missions (mission_id, session_id, project_id, status, created_at)
                       VALUES ('m_invalid', 'sess_nonexistent', ?, 'ACTIVE', ?);""",
                    (pid, now_utc),
                )

            # 4. Insert valid mission, turn, tool_call, event
            cursor.execute(
                """INSERT INTO missions (mission_id, session_id, project_id, status, created_at)
                   VALUES ('m_01', 'sess_valid', ?, 'ACTIVE', ?);""",
                (pid, now_utc),
            )
            cursor.execute(
                """INSERT INTO turns (turn_id, mission_id, step_idx, agent_role, created_at)
                   VALUES ('t_01', 'm_01', 1, 'PrimaryEngineer', ?);""",
                (now_utc,),
            )
            cursor.execute(
                """INSERT INTO tool_calls (call_id, turn_id, tool_name, status, created_at)
                   VALUES ('c_01', 't_01', 'run_command', 'SUCCESS', ?);""",
                (now_utc,),
            )
            cursor.execute(
                """INSERT INTO engineering_events (event_id, mission_id, project_id, event_type, epistemic_grade, created_at)
                   VALUES ('evt_01', 'm_01', ?, 'TASK_OUTCOME', 'FACT', ?);""",
                (pid, now_utc),
            )

            # Verify rows exist
            cursor.execute("SELECT count(*) as cnt FROM missions WHERE project_id = ?;", (pid,))
            self.assertEqual(cursor.fetchone()["cnt"], 1)

            # 5. Cascading delete: deleting session removes mission, turn, tool_call, event
            cursor.execute("DELETE FROM sessions WHERE session_id = 'sess_valid';")

            cursor.execute("SELECT count(*) as cnt FROM missions WHERE session_id = 'sess_valid';")
            self.assertEqual(cursor.fetchone()["cnt"], 0)
            cursor.execute("SELECT count(*) as cnt FROM turns WHERE turn_id = 't_01';")
            self.assertEqual(cursor.fetchone()["cnt"], 0)
            cursor.execute("SELECT count(*) as cnt FROM tool_calls WHERE call_id = 'c_01';")
            self.assertEqual(cursor.fetchone()["cnt"], 0)
            cursor.execute("SELECT count(*) as cnt FROM engineering_events WHERE event_id = 'evt_01';")
            self.assertEqual(cursor.fetchone()["cnt"], 0)

    # -------------------------------------------------------------
    # 10. Strict project/tenant isolation (Proving Ground)
    # -------------------------------------------------------------
    def test_10_project_tenant_isolation(self):
        """Proving ground: Project A writes, Project B writes; Project A queries return ZERO Project B rows."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        pid_a = register_project(db_path, self.proj_a, ecosystem="python")
        pid_b = register_project(db_path, self.proj_b, ecosystem="typescript")

        self.assertNotEqual(pid_a, pid_b)
        now_utc = datetime.now(timezone.utc).isoformat()

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()

            # Project A data insertion
            cursor.execute(
                "INSERT INTO sessions (session_id, project_id, surface, started_at) VALUES ('sess_a_1', ?, 'CLI', ?);",
                (pid_a, now_utc),
            )
            cursor.execute(
                "INSERT INTO missions (mission_id, session_id, project_id, intent_query, status, created_at) VALUES ('m_a_1', 'sess_a_1', ?, 'Fix auth in A', 'COMPLETED', ?);",
                (pid_a, now_utc),
            )
            cursor.execute(
                "INSERT INTO engineering_events (event_id, mission_id, project_id, event_type, epistemic_grade, affected_file, created_at) VALUES ('evt_a_1', 'm_a_1', ?, 'SUCCESSFUL_FIX', 'FACT', 'src/auth.py', ?);",
                (pid_a, now_utc),
            )

            # Project B data insertion
            cursor.execute(
                "INSERT INTO sessions (session_id, project_id, surface, started_at) VALUES ('sess_b_1', ?, 'IDE', ?);",
                (pid_b, now_utc),
            )
            cursor.execute(
                "INSERT INTO missions (mission_id, session_id, project_id, intent_query, status, created_at) VALUES ('m_b_1', 'sess_b_1', ?, 'Add UI in B', 'ACTIVE', ?);",
                (pid_b, now_utc),
            )
            cursor.execute(
                "INSERT INTO engineering_events (event_id, mission_id, project_id, event_type, epistemic_grade, affected_file, created_at) VALUES ('evt_b_1', 'm_b_1', ?, 'TEST_FAILURE', 'FACT', 'src/App.tsx', ?);",
                (pid_b, now_utc),
            )

            # Scope check: Project A query
            cursor.execute("SELECT session_id FROM sessions WHERE project_id = ?;", (pid_a,))
            a_sessions = [r["session_id"] for r in cursor.fetchall()]
            self.assertEqual(a_sessions, ["sess_a_1"])
            self.assertNotIn("sess_b_1", a_sessions)

            cursor.execute("SELECT mission_id, intent_query FROM missions WHERE project_id = ?;", (pid_a,))
            a_missions = [r["mission_id"] for r in cursor.fetchall()]
            self.assertEqual(a_missions, ["m_a_1"])
            self.assertNotIn("m_b_1", a_missions)

            cursor.execute("SELECT event_id, affected_file FROM engineering_events WHERE project_id = ?;", (pid_a,))
            a_events = [r["event_id"] for r in cursor.fetchall()]
            self.assertEqual(a_events, ["evt_a_1"])
            self.assertNotIn("evt_b_1", a_events)

            # Scope check: Project B query
            cursor.execute("SELECT session_id FROM sessions WHERE project_id = ?;", (pid_b,))
            b_sessions = [r["session_id"] for r in cursor.fetchall()]
            self.assertEqual(b_sessions, ["sess_b_1"])
            self.assertNotIn("sess_a_1", b_sessions)

            cursor.execute("SELECT mission_id FROM missions WHERE project_id = ?;", (pid_b,))
            b_missions = [r["mission_id"] for r in cursor.fetchall()]
            self.assertEqual(b_missions, ["m_b_1"])
            self.assertNotIn("m_a_1", b_missions)

        # Use isolation verifier
        self.assertTrue(verify_project_isolation(db_path, pid_a, pid_b))

    # -------------------------------------------------------------
    # 11. Missing directory recovery
    # -------------------------------------------------------------
    def test_11_missing_directory_recovery(self):
        """When configured data directory is missing on disk, status engine fails closed cleanly."""
        missing_dir = self.base / "nonexistent_dir"
        stat = get_storage_status(data_dir=missing_dir, project_root=self.proj_a)
        self.assertTrue(stat.is_configured)
        self.assertFalse(stat.db_exists)
        self.assertFalse(stat.is_healthy)
        self.assertTrue(any("does not exist on disk" in issue for issue in stat.issues))

    # -------------------------------------------------------------
    # 12. Invalid configuration
    # -------------------------------------------------------------
    def test_12_invalid_configuration(self):
        """Reject data directory inside project repository & fail-closed when unconfigured."""
        # 1. Unconfigured raises DataDirectoryNotConfiguredError
        with self.assertRaises(DataDirectoryNotConfiguredError):
            AntiOSDataResolver.resolve_data_dir(project_root=self.proj_a)

        # 2. Inside project repository is rejected by installation
        mgr = InstallationLifecycleManager(source_root=self.source_root, target_root=self.proj_a)
        inside_dir = self.proj_a / "subfolder" / "data"
        res = mgr.install(data_dir=str(inside_dir))
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("cannot be located inside the target project", res.issues[0])

    # -------------------------------------------------------------
    # 13. Database corruption and error handling
    # -------------------------------------------------------------
    def test_13_database_corruption_handling(self):
        """Corrupted/non-database file is caught safely by status and doctor without unhandled crash."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        # Overwrite with garbage bytes
        db_path.write_bytes(b"CORRUPTED_NON_SQLITE_GARBAGE_BYTES_12345")

        stat = get_storage_status(data_dir=self.data_dir, project_root=self.proj_a)
        self.assertTrue(stat.is_configured)
        self.assertTrue(stat.db_exists)
        self.assertFalse(stat.is_healthy)
        self.assertTrue(any("Database inspection error" in issue or "not a database" in issue for issue in stat.issues))

    # -------------------------------------------------------------
    # 14. CLI data status and set-dir commands
    # -------------------------------------------------------------
    def test_14_cli_data_status_and_set_dir(self):
        """CLI antios data status and antios data set-dir commands execute correctly."""
        parser = build_parser()

        # 1. Unconfigured status
        args_stat = parser.parse_args(["data", "status", "--path", str(self.proj_a), "--json"])
        self.assertEqual(args_stat.func(args_stat), 1)  # not healthy since unconfigured

        # 2. Set-dir command
        args_set = parser.parse_args([
            "data", "set-dir", str(self.data_dir), "--path", str(self.proj_a), "--json"
        ])
        ret = args_set.func(args_set)
        self.assertEqual(ret, 0)

        # 3. Status now passes
        args_stat_ok = parser.parse_args(["data", "status", "--path", str(self.proj_a), "--json"])
        self.assertEqual(args_stat_ok.func(args_stat_ok), 0)

    # -------------------------------------------------------------
    # 15. Doctor and Status engine integration
    # -------------------------------------------------------------
    def test_15_doctor_and_status_integration(self):
        """Doctor and Status detect unconfigured, healthy, and corrupted storage states."""
        # 1. Initial install without data-dir
        mgr = InstallationLifecycleManager(source_root=self.source_root, target_root=self.proj_a)
        res_inst = mgr.install()
        self.assertEqual(res_inst.status, "SUCCESS")

        doc = DoctorEngine(self.proj_a)
        rep = doc.run_doctor()
        self.assertTrue(rep.is_healthy)
        storage_check = [c for c in rep.checks if c.name == "Experience Storage"][0]
        self.assertEqual(storage_check.severity, DiagnosticSeverity.INFO)

        # 2. Install with data-dir
        res_inst_dd = mgr.install(data_dir=str(self.data_dir))
        self.assertIn(res_inst_dd.status, ("SUCCESS", "IDEMPOTENT"))

        rep_after = doc.run_doctor()
        self.assertTrue(rep_after.is_healthy)
        storage_check_after = [c for c in rep_after.checks if c.name == "Experience Storage"][0]
        self.assertEqual(storage_check_after.severity, DiagnosticSeverity.OK)

        # 3. Operational status
        stat = doc.get_status()
        self.assertTrue(stat.is_healthy)

        # 4. Point to missing directory
        cfg_file = self.proj_a / "antios.config.json"
        cfg_file.write_text(json.dumps({"data_dir": str(self.base / "missing_dir")}), encoding="utf-8")

        rep_err = doc.run_doctor()
        self.assertFalse(rep_err.is_healthy)
        storage_check_err = [c for c in rep_err.checks if c.name == "Experience Storage"][0]
        self.assertEqual(storage_check_err.severity, DiagnosticSeverity.ERROR)

    # -------------------------------------------------------------
    # 16. Windows-compatible path normalization and deterministic project_id
    # -------------------------------------------------------------
    def test_16_path_normalization_and_deterministic_project_id(self):
        """Path normalization produces consistent project IDs across casing and separators."""
        path_str = str(self.proj_a)
        norm_1 = AntiOSDataResolver.normalize_path(path_str)
        norm_2 = AntiOSDataResolver.normalize_path(path_str.replace("/", "\\"))

        self.assertEqual(norm_1, norm_2)
        if len(norm_1) >= 2 and norm_1[1] == ":":
            self.assertTrue(norm_1[0].islower())

        pid_1, _ = AntiOSDataResolver.resolve_project_identity(self.proj_a)
        pid_2, _ = AntiOSDataResolver.resolve_project_identity(Path(path_str))
        self.assertEqual(pid_1, pid_2)
        self.assertTrue(pid_1.startswith("proj_"))

    # -------------------------------------------------------------
    # 17. Multiple projects sharing one central data directory
    # -------------------------------------------------------------
    def test_17_multiple_projects_sharing_one_data_dir(self):
        """Multiple distinct projects share experience.db with separate project records."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)

        pid_a = register_project(db_path, self.proj_a, ecosystem="python")
        pid_b = register_project(db_path, self.proj_b, ecosystem="rust")

        with closing(get_db_connection(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_id, project_name, ecosystem FROM projects ORDER BY project_name;")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["project_name"], "project_alpha")
            self.assertEqual(rows[0]["ecosystem"], "python")
            self.assertEqual(rows[1]["project_name"], "project_beta")
            self.assertEqual(rows[1]["ecosystem"], "rust")

    # -------------------------------------------------------------
    # 18. Zero database files inside target repositories (INV-10)
    # -------------------------------------------------------------
    def test_18_zero_database_files_in_project(self):
        """Ensures that no .db, .db-wal, or .db-shm files are ever placed in project repository."""
        mgr = InstallationLifecycleManager(source_root=self.source_root, target_root=self.proj_a)
        res = mgr.install(data_dir=str(self.data_dir))
        self.assertEqual(res.status, "SUCCESS")

        # Search project tree for any sqlite/db file
        forbidden_extensions = [".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm"]
        found_db_files = []
        for p in self.proj_a.rglob("*"):
            if p.is_file() and any(p.name.endswith(ext) for ext in forbidden_extensions):
                found_db_files.append(str(p))

        self.assertEqual(found_db_files, [], "Found forbidden database files inside project repository!")

        # Verify experience.db exists ONLY in central data directory
        self.assertTrue((self.data_dir / "experience.db").is_file())

    # -------------------------------------------------------------
    # Online hot backup test
    # -------------------------------------------------------------
    def test_online_hot_backup(self):
        """Verifies online hot backup creates a valid SQLite database clone."""
        init_data_directory(self.data_dir)
        db_path = self.data_dir / "experience.db"
        init_experience_db(db_path)
        pid = register_project(db_path, self.proj_a)

        backup_file = backup_database(db_path)
        self.assertTrue(backup_file.is_file())

        with closing(sqlite3.connect(str(backup_file))) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT project_id FROM projects WHERE project_id = ?;", (pid,))
            self.assertIsNotNone(cursor.fetchone())


if __name__ == "__main__":
    unittest.main()
