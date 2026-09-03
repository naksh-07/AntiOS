"""Zero-Dependency Test Runner for AntiOS Core Framework & Skills."""

import os
import sys
import unittest

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import all test modules
import tests.test_config as test_config
import tests.test_guard as test_guard
import tests.test_gate as test_gate
import tests.test_verdict as test_verdict
import tests.test_skills as test_skills
import tests.test_lifecycle as test_lifecycle
import tests.test_workflows as test_workflows


def build_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    modules = [
        test_config,
        test_guard,
        test_gate,
        test_verdict,
        test_skills,
        test_lifecycle,
        test_workflows,
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
