"""Standard Library Test Runner for AntiOS.

Runs all tests using pure Python standard library (no external dependencies).
"""

import os
import sys
import unittest

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def main():
    print(f"Executing AntiOS Test Suite on Python {sys.version.split()[0]}...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Import test modules
    import tests.test_config as tc
    import tests.test_guard as tg
    import tests.test_gate as tga
    import tests.test_verdict as tv
    import tests.test_skills as ts

    # Add pytest-style test functions by wrapping them in FunctionTestCase
    for mod in (tc, tg, tga, tv, ts):
        for attr in dir(mod):
            if attr.startswith("test_") and callable(getattr(mod, attr)):
                func = getattr(mod, attr)
                suite.addTest(unittest.FunctionTestCase(func))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()