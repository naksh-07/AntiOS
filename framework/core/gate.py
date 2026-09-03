"""AntiOS Stop Gate Verification Engine.

Enforces physical process test execution ratchets, working tree cleanliness,
and dynamic zero-config test runner discovery.
"""

from __future__ import annotations
import json
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from framework.core.config import AntiOSConfig, RunnerConfig, load_config


def run_command_safe(
    cmd: List[str],
    cwd: str,
    timeout: int = 60
) -> Tuple[int, str, str, bool]:
    """Runs a process safely.

    Returns:
        (returncode, stdout, stderr, is_missing_binary)
    """
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            shell=True if os.name == "nt" else False
        )
        return proc.returncode, proc.stdout, proc.stderr, False
    except FileNotFoundError:
        return -1, "", "Binary not found in PATH", True
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds", False
    except Exception as e:
        return -1, "", str(e), False


def check_working_tree_conflicts(repo_root: str) -> Optional[str]:
    """Checks if working tree contains unresolved git merge conflict markers."""
    git_dir = os.path.join(repo_root, ".git")
    if not os.path.exists(git_dir):
        return None

    ret, out, err, missing = run_command_safe(["git", "rev-parse", "--is-inside-work-tree"], repo_root, timeout=5)
    if missing or ret != 0:
        return None

    ret, out, err, missing = run_command_safe(["git", "diff", "--check"], repo_root, timeout=10)
    if ret != 0:
        for line in (out + "\n" + err).splitlines():
            if "leftover conflict marker" in line.lower():
                return f"Unresolved git conflict markers detected in working tree: {line.strip()}"
    return None


def discover_test_runners(repo_root: str) -> List[RunnerConfig]:
    """Dynamically detects project test runners from root manifests if unconfigured."""
    runners: List[RunnerConfig] = []

    # 1. Node.js / TypeScript (package.json)
    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
            scripts = pkg_data.get("scripts", {})
            if "vitest:once" in scripts:
                runners.append(
                    RunnerConfig(
                        name="vitest",
                        manifest="package.json",
                        scripts=["vitest:once"],
                        default_command=["npm", "run", "vitest:once"],
                        timeout_seconds=90,
                    )
                )
            elif "test" in scripts:
                runners.append(
                    RunnerConfig(
                        name="npm-test",
                        manifest="package.json",
                        scripts=["test"],
                        default_command=["npm", "test"],
                        timeout_seconds=90,
                    )
                )
        except Exception:
            runners.append(
                RunnerConfig(
                    name="npm-test",
                    manifest="package.json",
                    default_command=["npm", "test"],
                    timeout_seconds=90,
                )
            )

    # 2. Python (pyproject.toml, pytest.ini, setup.py)
    pyproject = os.path.join(repo_root, "pyproject.toml")
    pytest_ini = os.path.join(repo_root, "pytest.ini")
    if os.path.isfile(pyproject) or os.path.isfile(pytest_ini):
        manifest_file = "pyproject.toml" if os.path.isfile(pyproject) else "pytest.ini"
        runners.append(
            RunnerConfig(
                name="pytest",
                manifest=manifest_file,
                default_command=["pytest"],
                timeout_seconds=60,
            )
        )

    # 3. Rust (Cargo.toml)
    cargo_toml = os.path.join(repo_root, "Cargo.toml")
    if os.path.isfile(cargo_toml):
        runners.append(
            RunnerConfig(
                name="cargo-test",
                manifest="Cargo.toml",
                default_command=["cargo", "test"],
                timeout_seconds=120,
            )
        )

    # 4. Go (go.mod)
    go_mod = os.path.join(repo_root, "go.mod")
    if os.path.isfile(go_mod):
        runners.append(
            RunnerConfig(
                name="go-test",
                manifest="go.mod",
                default_command=["go", "test", "./..."],
                timeout_seconds=60,
            )
        )

    return runners


def evaluate_stop_gate(
    input_data: Any,
    config: Optional[AntiOSConfig] = None
) -> Tuple[str, Optional[str]]:
    """Evaluates a Stop hook event.

    Returns:
        (decision, reason) where decision is "allow" or "continue".
    """
    try:
        if not isinstance(input_data, dict):
            return "continue", "AntiOS Stop Gate: Malformed hook input. Failing closed."

        workspace_paths = input_data.get("workspacePaths", [])
        if not workspace_paths or not isinstance(workspace_paths, list):
            repo_root = os.getcwd()
        else:
            repo_root = os.path.normcase(os.path.abspath(os.path.realpath(workspace_paths[0])))

        if config is None:
            config = load_config(repo_root)

        # 1. Cleanliness / Conflict Check
        if config.policies.enforce_working_tree_cleanliness:
            conflict_err = check_working_tree_conflicts(repo_root)
            if conflict_err:
                return "continue", f"AntiOS Stop Gate: Cleanliness check failed: {conflict_err}"

        # 2. Dynamic Test Execution (Configured or Auto-discovered)
        test_runners = config.test_runners if config.test_runners else discover_test_runners(repo_root)

        for runner in test_runners:
            if runner.manifest:
                manifest_path = os.path.join(repo_root, runner.manifest)
                if not os.path.isfile(manifest_path):
                    continue

            # Determine command to run
            cmd: List[str] = list(runner.default_command)
            cwd = os.path.join(repo_root, runner.cwd) if runner.cwd else repo_root

            # For npm / node packages, check package.json scripts
            if runner.manifest == "package.json":
                try:
                    with open(os.path.join(repo_root, "package.json"), "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                    scripts = pkg.get("scripts", {})
                    chosen_script = None
                    for candidate in runner.scripts:
                        if candidate in scripts:
                            chosen_script = candidate
                            break

                    if chosen_script:
                        cmd = ["npm", "run", chosen_script]
                except Exception:
                    pass

            ret, stdout, stderr, is_missing = run_command_safe(
                cmd, cwd, timeout=runner.timeout_seconds
            )

            if is_missing:
                # Environment binary unavailable
                continue

            if ret != 0:
                stdout_snip = stdout.strip()[-1000:] if stdout else ""
                stderr_snip = stderr.strip()[-1000:] if stderr else ""
                return (
                    "continue",
                    f"AntiOS Stop Gate: Verification failed! Test runner '{runner.name}' did not pass.\n"
                    f"Command: {' '.join(cmd)}\nExit Code: {ret}\n"
                    f"Stdout: {stdout_snip}\nStderr: {stderr_snip}"
                )

        # If no tests failed, allow task conclusion
        return "allow", None

    except Exception as e:
        return "continue", f"AntiOS Stop Gate Internal Error: {str(e)}. Failing closed."
