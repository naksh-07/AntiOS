"""Tests for AntiOS 2.0 Git, GitHub, and Release Engineering Capabilities."""

import os
from pathlib import Path
import tempfile
import unittest

from framework.core.git_capability import GitCapabilityEngine, GitMutationPolicy
from framework.core.github_capability import (
    FeatureTriageVerdict,
    GitHubCapabilityEngine,
    IssueClass,
    IssueEvidence,
)
from framework.core.release_engine import ReleaseEngine
from framework.core.version import ANTIOS_VERSION


class TestGitGitHubReleaseCapabilities(unittest.TestCase):
    """Test suite validating Git CLI abstraction, GitHub workflows, and release gates."""

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_git_capability_read_only_inspection(self):
        """Git capability engine inspects current repository without mutations."""
        git_eng = GitCapabilityEngine(self.repo_root)
        self.assertTrue(git_eng.is_git_available())
        status = git_eng.inspect_status()
        self.assertTrue(status.is_git_repo)
        self.assertIsNotNone(status.current_commit)
        self.assertIsInstance(status.tags, list)

    def test_git_mutation_guard_on_dirty_tree(self):
        """Guarded mutating operation (create_release_tag) rejects dirty tree."""
        git_eng = GitCapabilityEngine(self.repo_root)
        # In current test run, there are uncommitted working tree changes
        res = git_eng.create_release_tag(
            tag_name="v9.9.9-test",
            message="Test release tag",
            policy=GitMutationPolicy.GUARDED,
        )
        # Should be rejected because tree is dirty or policy guarded
        if not git_eng.inspect_status().is_clean:
            self.assertFalse(res["success"])
            self.assertIn("dirty working tree", res["error"])

    def test_github_capability_discovery(self):
        """GitHub capability profile discovers local gh CLI and tools."""
        gh_eng = GitHubCapabilityEngine(self.repo_root)
        caps = gh_eng.discover_capabilities()
        self.assertTrue(caps.gh_cli_available)
        self.assertTrue(caps.gh_authenticated)
        self.assertIn("repo", caps.gh_scopes)
        self.assertTrue(caps.can_manage_issues)
        self.assertTrue(caps.can_manage_prs)

    def test_feature_request_freeze_triage(self):
        """Architecture Freeze gatekeeper triages feature requests deterministically."""
        gh_eng = GitHubCapabilityEngine(self.repo_root)

        # Banned: Vector DB
        res_vdb = gh_eng.triage_feature_request("Add a vector database and embedding index for search")
        self.assertEqual(res_vdb["verdict"], FeatureTriageVerdict.REJECTED_OUT_OF_SCOPE.value)
        self.assertFalse(res_vdb["is_permitted_in_2_x"])

        # Banned: Swarm
        res_sw = gh_eng.triage_feature_request("Create a swarm of autonomous communicating workers")
        self.assertEqual(res_sw["verdict"], FeatureTriageVerdict.REJECTED_OUT_OF_SCOPE.value)

        # Banned: Daemon
        res_dae = gh_eng.triage_feature_request("Run a persistent background daemon poller")
        self.assertEqual(res_dae["verdict"], FeatureTriageVerdict.REJECTED_OUT_OF_SCOPE.value)

        # AntiOS 3.0 Candidate: Multi-repo
        res_mr = gh_eng.triage_feature_request("Enable multi-repo distributed workspace orchestration")
        self.assertEqual(res_mr["verdict"], FeatureTriageVerdict.ANTI_OS_3_CANDIDATE.value)
        self.assertFalse(res_mr["is_permitted_in_2_x"])

        # Permitted: Bug fix
        res_bug = gh_eng.triage_feature_request("Fix crash when parsing nested cargo workspaces")
        self.assertEqual(res_bug["verdict"], FeatureTriageVerdict.BUG.value)
        self.assertTrue(res_bug["is_permitted_in_2_x"])

        # Permitted: Adapter
        res_adp = gh_eng.triage_feature_request("Add project adapter for Go/Golang tooling")
        self.assertEqual(res_adp["verdict"], FeatureTriageVerdict.COMPATIBILITY.value)
        self.assertTrue(res_adp["is_permitted_in_2_x"])

    def test_issue_evidence_formatting(self):
        """Issue evidence model formats structured markdown report."""
        evidence = IssueEvidence(
            title="Adapter fail-closed on missing Cargo.toml",
            issue_class=IssueClass.BUG,
            observed_behavior="Uncaught FileNotFoundError",
            expected_behavior="Fail-closed diagnostic card",
            reproduction_steps=["antios adapt --path /empty"],
            evidence_traces=["Exit code 1: FileNotFoundError"],
            affected_files=["framework/core/adapter.py"],
            anti_os_version=ANTIOS_VERSION,
        )
        md = evidence.to_markdown()
        self.assertIn("[BUG] Adapter fail-closed", md)
        self.assertIn("FileNotFoundError", md)
        self.assertIn(ANTIOS_VERSION, md)

    def test_release_engine_release_notes_generation(self):
        """Release engine assembles structured release notes with highlights and limitations."""
        rel_eng = ReleaseEngine(self.repo_root)
        notes = rel_eng.generate_release_notes()
        self.assertIn(f"# AntiOS {ANTIOS_VERSION} Release Notes", notes)
        self.assertIn("## Highlights", notes)
        self.assertIn("## Verified Capabilities", notes)
        self.assertIn("## Known Limitations", notes)


if __name__ == "__main__":
    unittest.main()
