"""Tests for framework.core.config."""

import json
import os
import tempfile

from framework.core.config import AntiOSConfig, TestRunnerConfig, load_config


def test_default_config_when_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = load_config(tmpdir)
        assert cfg.version == "1.0"
        assert ".agents" in cfg.protected_zones
        assert "framework" in cfg.protected_zones
        assert "rslib" in cfg.protected_domain_paths
        assert cfg.policies.fail_closed is True


def test_load_custom_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_data = {
            "version": "2.0",
            "name": "CustomTestAdapter",
            "protected_zones": [".agents", "custom_framework"],
            "protected_domain_paths": ["custom_core"],
            "forbidden_patterns": ["custom~*"],
            "test_runners": [
                {
                    "name": "custom_runner",
                    "manifest": "manifest.json",
                    "scripts": ["test:unit"],
                    "default_command": ["run", "test"],
                    "timeout_seconds": 30
                }
            ],
            "policies": {
                "fail_closed": True,
                "enforce_working_tree_cleanliness": False,
                "enforce_same_change_set": True
            }
        }
        config_path = os.path.join(tmpdir, "antios.config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        cfg = load_config(tmpdir)
        assert cfg.version == "2.0"
        assert cfg.name == "CustomTestAdapter"
        assert "custom_framework" in cfg.protected_zones
        assert "custom_core" in cfg.protected_domain_paths
        assert len(cfg.test_runners) == 1
        assert cfg.test_runners[0].name == "custom_runner"
        assert cfg.policies.enforce_working_tree_cleanliness is False


def test_corrupt_config_falls_back_to_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "antios.config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("{corrupt json...")

        cfg = load_config(tmpdir)
        assert cfg.version == "1.0"
        assert ".agents" in cfg.protected_zones
