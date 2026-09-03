"""Zero-Dependency Test Runner for AntiOS Core Framework & Skills."""

import os
import sys
import unittest

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import all test modules — baseline (Phase 12-15)
import tests.test_config as test_config
import tests.test_guard as test_guard
import tests.test_gate as test_gate
import tests.test_verdict as test_verdict
import tests.test_skills as test_skills
import tests.test_lifecycle as test_lifecycle
import tests.test_workflows as test_workflows

# Phase 16-18 hardened/new test modules
import tests.test_guard_hardened as test_guard_hardened
import tests.test_gate_hardened as test_gate_hardened
import tests.test_changeset as test_changeset
import tests.test_tool as test_tool
import tests.test_worktree as test_worktree
import tests.test_governance as test_governance

# Phase 19-20 Project Intelligence & Adaptation test modules
import tests.test_profile as test_profile
import tests.test_discovery as test_discovery
import tests.test_adapter as test_adapter
import tests.test_conflict as test_conflict
import tests.test_fixtures as test_fixtures


def build_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    modules = [
        # Phase 12-15 baseline
        test_config,
        test_guard,
        test_gate,
        test_verdict,
        test_skills,
        test_lifecycle,
        test_workflows,
        # Phase 16-18 hardened/new
        test_guard_hardened,
        test_gate_hardened,
        test_changeset,
        test_tool,
        test_worktree,
        test_governance,
        # Phase 19-20
        test_profile,
        test_discovery,
        test_adapter,
        test_conflict,
        test_fixtures,
    ]

    for mod in modules:
        for attr in dir(mod):
            if attr.startswith("test_") and callable(getattr(mod, attr)):
                func = getattr(mod, attr)
                suite.addTest(unittest.FunctionTestCase(func))

    return suite


if __name__ == "__main__":
    print(f"Executing AntiOS Test Suite on Python {sys.version.split()[0]}...")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = build_suite()
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
