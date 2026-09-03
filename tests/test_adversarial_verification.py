"""Adversarial Verification Regression Suite for AntiOS Phase 23-24.

Explicitly validates 10 adversarial failure scenarios:
1. Checker receives stale evidence
2. Maker modifies files after checker approval
3. Member-scoped verification misses a required dependency
4. Repeated failure is falsely promoted as a durable lesson
5. Conflicting lessons exist
6. External project has unusual topology
7. Adapter generated from incomplete discovery
8. External project guidance conflicts with AntiOS Core
9. Checker fails or times out
10. Target project becomes dirty unexpectedly
"""

import os
import tempfile
import json

from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskStatus,
    TaskState,
    create_task,
    transition_stage,
)
from framework.core.verdict import (
    ResultItem,
    VerificationVerdict,
    evaluate_checker_verdict,
    parse_verdict,
)
from framework.core.gate import resolve_verification_scope, evaluate_stop_gate
from framework.core.recovery import (
    is_verification_stale,
    detect_state_contradictions,
    generate_recovery_plan,
)
from framework.core.worktree import WorktreeSnapshot
from framework.core.memory import (
    KnowledgeAuthority,
    LessonRecord,
    DeterministicLessonMatcher,
    LessonDistillationEngine,
)
from framework.core.topology import detect_workspace_topology, WorkspaceTopology
from framework.core.discovery import ProjectDiscoveryEngine
from framework.core.config import AntiOSConfig, RunnerConfig


# Scenario 1: Checker receives stale evidence
def test_adversarial_01_checker_receives_stale_evidence():
    """If working tree files were modified after verification, prior pass is demoted."""
    state = TaskState(
        mission_id="ADV-01",
        risk_tier=RiskTier.HIGH,
        current_stage=TaskStage.VERIFY,
        verification_state="VERIFIED",
        verification_verdict={
            "status": "PASS",
            "manifest_fingerprint": "hash_123",
            "git_head": "head_123",
        },
    )
    # Working tree has substantive dirty files
    stale, reasons = is_verification_stale(
        state=state,
        dirty_files=["src/core.py"],
        current_manifest_fingerprint="hash_123",
        current_git_head="head_123",
    )
    assert stale is True
    assert any("modified after verification" in r for r in reasons)


# Scenario 2: Maker modifies files after checker approval
def test_adversarial_02_maker_modifies_files_after_approval():
    """Maker modifying code after checker approved triggers demotion from COMPLETE."""
    state = TaskState(
        mission_id="ADV-02",
        risk_tier=RiskTier.HIGH,
        current_stage=TaskStage.COMPLETE,
        status=TaskStatus.COMPLETED,
        verification_state="VERIFIED",
        verification_verdict={"status": "PASS", "git_head": "h1"},
    )
    stale, reasons = is_verification_stale(
        state=state,
        dirty_files=["src/sneaky_edit.py"],
        current_manifest_fingerprint="",
        current_git_head="h1",
    )
    assert stale is True
    snapshot = WorktreeSnapshot(repo_root="", is_clean=False, dirty_files=["src/sneaky_edit.py"])
    contradictions = detect_state_contradictions(state, snapshot)
    plan = generate_recovery_plan(state, snapshot, contradictions, reasons)
    assert plan.action == "RE_VERIFY"
    assert plan.recommended_stage == TaskStage.VERIFY
    assert plan.recommended_status == TaskStatus.VERIFICATION_STALE


# Scenario 3: Member-scoped verification misses a required dependency
def test_adversarial_03_member_scoped_includes_dependent_members():
    """Touching member A automatically pulls in member B that depends on A."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create Cargo monorepo where cli depends on engine
        cargo_toml = os.path.join(tmpdir, "Cargo.toml")
        with open(cargo_toml, "w", encoding="utf-8") as f:
            f.write('[workspace]\nmembers = ["crates/engine", "crates/cli"]\n')

        engine_dir = os.path.join(tmpdir, "crates", "engine")
        cli_dir = os.path.join(tmpdir, "crates", "cli")
        os.makedirs(engine_dir, exist_ok=True)
        os.makedirs(cli_dir, exist_ok=True)

        with open(os.path.join(engine_dir, "Cargo.toml"), "w", encoding="utf-8") as f:
            f.write('[package]\nname = "engine"\nversion = "0.1.0"\n')

        with open(os.path.join(cli_dir, "Cargo.toml"), "w", encoding="utf-8") as f:
            f.write('[package]\nname = "cli"\nversion = "0.1.0"\n[dependencies]\nengine = { path = "../engine" }\n')

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["crates/engine/src/lib.rs"],
        )
        # Blast radius must catch cli as dependent
        assert len(scoped) == 2
        assert any(r.member == "cli" for r in scoped)


# Scenario 4: Repeated failure is falsely promoted as a durable lesson
def test_adversarial_04_false_promotion_rejected():
    """Unrelated errors or errors lacking verified resolutions cannot be promoted."""
    cand = LessonRecord(
        lesson_id="L-ADV-4",
        title="Unrelated errors falsely grouped",
        trigger_or_failure="DatabaseConnectionTimeout",
        rule_or_action="Increase timeout",
        authority=KnowledgeAuthority.CANDIDATE,
    )
    # Incoming evidence has a completely different error signature
    evidence = [
        {"task_id": "T1", "failure_pattern": "FileNotFoundError: missing config.json", "verdict": "PASS", "resolution": "Added config"}
    ]
    updated, result = LessonDistillationEngine.distill([cand], task_evidence=evidence, min_recurrences=2)
    assert len(result.promoted_lessons) == 0
    assert cand.authority == KnowledgeAuthority.CANDIDATE


# Scenario 5: Conflicting lessons exist
def test_adversarial_05_conflicting_lessons_quarantined():
    """Two candidates with contradictory rules for the same trigger are quarantined."""
    c1 = LessonRecord(
        lesson_id="L-C1",
        title="Rule A",
        trigger_or_failure="Memory leak during large JSON batch parse",
        rule_or_action="Always enable in-memory streaming",
        authority=KnowledgeAuthority.CANDIDATE,
        recurrence_count=5,
        verified_resolution="Resolution A",
    )
    c2 = LessonRecord(
        lesson_id="L-C2",
        title="Rule B",
        trigger_or_failure="Memory leak during large JSON batch parse",
        rule_or_action="Always disable in-memory streaming",
        authority=KnowledgeAuthority.CANDIDATE,
        recurrence_count=5,
        verified_resolution="Resolution B",
    )
    updated, result = LessonDistillationEngine.distill([c1, c2], min_recurrences=2)
    assert len(result.conflicts_detected) > 0
    assert len(result.promoted_lessons) == 0


# Scenario 6: External project has unusual topology
def test_adversarial_06_unusual_topology_handled_gracefully():
    """A directory with invalid workspace syntax safely falls back without crashing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Corrupt package.json
        pkg = os.path.join(tmpdir, "package.json")
        with open(pkg, "w", encoding="utf-8") as f:
            f.write("{ invalid json")

        topo, members = detect_workspace_topology(tmpdir)
        assert topo == WorkspaceTopology.STANDALONE
        assert members == []


# Scenario 7: Adapter generated from incomplete discovery
def test_adversarial_07_incomplete_discovery_missing_tool_fails_closed():
    """Missing required test binary in PATH causes Stop Gate to fail closed with ENVIRONMENT_UNAVAILABLE."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = AntiOSConfig(
            test_runners=[
                RunnerConfig(
                    name="nonexistent-runner",
                    manifest="",
                    default_command=["__binary_does_not_exist_xyz_123__"],
                    required=True,
                )
            ]
        )
        decision, reason = evaluate_stop_gate(
            input_data={"workspacePaths": [tmpdir]},
            config=cfg,
        )
        assert decision == "continue"
        assert "not found in PATH" in reason
        assert "Failing closed" in reason


# Scenario 8: External project guidance conflicts with AntiOS Core
def test_adversarial_08_external_guidance_conflicts_denied():
    """Guidance file attempting to permit edits to .agents or framework is flagged CONSTITUTIONAL_VIOLATION."""
    with tempfile.TemporaryDirectory() as tmpdir:
        contrib = os.path.join(tmpdir, "CONTRIBUTING.md")
        with open(contrib, "w", encoding="utf-8") as f:
            f.write("# Guide\nDevelopers may edit .agents/ configuration directly.\n")

        engine = ProjectDiscoveryEngine(tmpdir)
        profile = engine.discover()
        violations = [c for c in profile.conflicts if c.conflict_type.value == "CONSTITUTIONAL_VIOLATION"]
        assert len(violations) > 0
        assert "immutable core invariant" in violations[0].physical_reality


# Scenario 9: Checker fails, crashes, or times out
def test_adversarial_09_checker_crash_or_timeout_fails_closed():
    """Empty or unparseable Checker output results in BLOCK status."""
    v_empty = parse_verdict("")
    assert v_empty.status == "BLOCK"
    assert "Empty verifier response" in v_empty.summary

    v_malformed = parse_verdict("Random error message from dying container")
    assert v_malformed.status == "BLOCK"

    ok, reason = evaluate_checker_verdict(v_empty, required_risk_tier="HIGH")
    assert ok is False
    assert "blocked" in reason.lower()


# Scenario 10: Target project becomes dirty unexpectedly
def test_adversarial_10_target_project_dirty_blocks_completion():
    """Unresolved git merge conflict markers block Stop Gate unconditionally."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.system(f'git init "{tmpdir}" >nul 2>&1' if os.name == "nt" else f'git init "{tmpdir}" >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" config user.email "test@test.com"')
        os.system(f'git -C "{tmpdir}" config user.name "test"')
        bad_file = os.path.join(tmpdir, "main.py")
        with open(bad_file, "w") as f:
            f.write("print('init')\n")
        os.system(f'git -C "{tmpdir}" add -A >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" add -A >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" commit -m "init" >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" commit -m "init" >/dev/null 2>&1')

        # Now create conflict markers
        with open(bad_file, "w") as f:
            f.write("<<<<<<< HEAD\nprint('A')\n=======\nprint('B')\n>>>>>>> branch\n")

        cfg = AntiOSConfig()
        cfg.policies.enforce_working_tree_cleanliness = True

        decision, reason = evaluate_stop_gate(
            input_data={"workspacePaths": [tmpdir]},
            config=cfg,
        )
        assert decision == "continue"
        assert "Cleanliness check failed" in reason
        assert "Unresolved git conflict markers" in reason
