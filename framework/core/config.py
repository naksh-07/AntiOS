"""AntiOS Adapter Configuration Loader.

Decouples generic AntiOS governance mechanisms from project-specific domains
(e.g., StudyLab rslib paths or custom test commands).
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RunnerConfig:
    name: str
    manifest: str
    scripts: List[str] = field(default_factory=list)
    default_command: List[str] = field(default_factory=list)
    timeout_seconds: int = 60


# Alias for backward compatibility
TestRunnerConfig = RunnerConfig


@dataclass
class PoliciesConfig:
    fail_closed: bool = True
    enforce_working_tree_cleanliness: bool = True
    enforce_same_change_set: bool = True


@dataclass
class AntiOSConfig:
    version: str = "1.0"
    name: str = "AntiOS-Default-Adapter"
    protected_zones: List[str] = field(default_factory=lambda: [".agents", "framework"])
    protected_domain_paths: List[str] = field(default_factory=lambda: ["rslib"])
    forbidden_patterns: List[str] = field(default_factory=lambda: ["rslib~*"])
    test_runners: List[RunnerConfig] = field(default_factory=lambda: [
        RunnerConfig(
            name="typescript",
            manifest="package.json",
            scripts=["vitest:once", "test"],
            default_command=["npm", "run", "vitest:once"],
            timeout_seconds=60
        ),
        RunnerConfig(
            name="python",
            manifest="pyproject.toml",
            scripts=[],
            default_command=["pytest"],
            timeout_seconds=60
        )
    ])
    policies: PoliciesConfig = field(default_factory=PoliciesConfig)


def load_config(repo_root: Optional[str] = None) -> AntiOSConfig:
    """Load antios.config.json from repo_root, falling back to secure defaults."""
    if not repo_root:
        repo_root = os.getcwd()

    config_path = os.path.join(repo_root, "antios.config.json")
    if not os.path.isfile(config_path):
        return AntiOSConfig()

    try:
        with open(config_path, "r", encoding="utf-8-sig") as f:
            data: Dict[str, Any] = json.load(f)

        test_runners = []
        for tr in data.get("test_runners", []):
            test_runners.append(
                RunnerConfig(
                    name=tr.get("name", "unknown"),
                    manifest=tr.get("manifest", ""),
                    scripts=tr.get("scripts", []),
                    default_command=tr.get("default_command", []),
                    timeout_seconds=tr.get("timeout_seconds", 60),
                )
            )

        raw_policies = data.get("policies", {})
        policies = PoliciesConfig(
            fail_closed=raw_policies.get("fail_closed", True),
            enforce_working_tree_cleanliness=raw_policies.get("enforce_working_tree_cleanliness", True),
            enforce_same_change_set=raw_policies.get("enforce_same_change_set", True),
        )

        return AntiOSConfig(
            version=data.get("version", "1.0"),
            name=data.get("name", "AntiOS-Adapter"),
            protected_zones=data.get("protected_zones", [".agents", "framework"]),
            protected_domain_paths=data.get("protected_domain_paths", ["rslib"]),
            forbidden_patterns=data.get("forbidden_patterns", ["rslib~*"]),
            test_runners=test_runners if test_runners else AntiOSConfig().test_runners,
            policies=policies,
        )
    except Exception:
        return AntiOSConfig()