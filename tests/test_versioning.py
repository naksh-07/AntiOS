"""Unit tests for AntiOS 2.0 Authoritative Versioning & Release Channels."""

import unittest
from pathlib import Path

from framework.core.manifest import CURRENT_ANTIOS_VERSION, CURRENT_SCHEMA_VERSION
from framework.core.version import (
    ANTIOS_VERSION,
    ADAPTER_SCHEMA_VERSION,
    ReleaseChannel,
    SemVer,
    compare_versions,
    get_version_info,
)


class TestVersioning(unittest.TestCase):
    """Test suite validating Semantic Versioning contracts and version authority."""

    def test_single_authoritative_source(self):
        """Authoritative version in version.py must align with manifest constants."""
        self.assertEqual(ANTIOS_VERSION, CURRENT_ANTIOS_VERSION)
        self.assertEqual(CURRENT_SCHEMA_VERSION, "2.0.0")
        self.assertEqual(ADAPTER_SCHEMA_VERSION, "1.0")

    def test_semver_parsing_valid(self):
        """Valid SemVer strings parse into structured objects."""
        v1 = SemVer.parse("2.0.0")
        self.assertEqual(v1.major, 2)
        self.assertEqual(v1.minor, 0)
        self.assertEqual(v1.patch, 0)
        self.assertIsNone(v1.prerelease)
        self.assertEqual(v1.channel, ReleaseChannel.STABLE)

        v2 = SemVer.parse("2.0.0-beta.1")
        self.assertEqual(v2.major, 2)
        self.assertEqual(v2.minor, 0)
        self.assertEqual(v2.patch, 0)
        self.assertEqual(v2.prerelease, "beta.1")
        self.assertEqual(v2.channel, ReleaseChannel.BETA)

        v3 = SemVer.parse("v2.1.0-rc.2")
        self.assertEqual(v3.major, 2)
        self.assertEqual(v3.minor, 1)
        self.assertEqual(v3.patch, 0)
        self.assertEqual(v3.prerelease, "rc.2")
        self.assertEqual(v3.channel, ReleaseChannel.RC)

        v4 = SemVer.parse("0.1.0-alpha.1")
        self.assertEqual(v4.channel, ReleaseChannel.DEVELOPMENT)

    def test_semver_parsing_invalid(self):
        """Invalid version formats must raise ValueError."""
        invalid_versions = ["invalid", "2.0", "v2", "2.0.0.0", "", None, "2.a.0"]
        for inv in invalid_versions:
            with self.assertRaises(ValueError):
                SemVer.parse(inv)  # type: ignore

    def test_semver_comparison(self):
        """SemVer comparison follows strict SemVer rules."""
        v_beta1 = SemVer.parse("2.0.0-beta.1")
        v_beta2 = SemVer.parse("2.0.0-beta.2")
        v_rc1 = SemVer.parse("2.0.0-rc.1")
        v_stable = SemVer.parse("2.0.0")
        v_next = SemVer.parse("2.0.1")

        self.assertTrue(v_beta1 < v_beta2)
        self.assertTrue(v_beta2 < v_rc1)
        self.assertTrue(v_rc1 < v_stable)
        self.assertTrue(v_stable < v_next)
        self.assertEqual(v_beta1, SemVer.parse("2.0.0-beta.1"))

    def test_compare_versions_helper(self):
        """compare_versions detects upgrades and downgrades."""
        cmp_up = compare_versions("2.0.0-beta.1", "2.0.0")
        self.assertTrue(cmp_up["is_upgrade"])
        self.assertFalse(cmp_up["is_downgrade"])
        self.assertFalse(cmp_up["is_same"])

        cmp_down = compare_versions("2.0.0", "2.0.0-beta.1")
        self.assertFalse(cmp_down["is_upgrade"])
        self.assertTrue(cmp_down["is_downgrade"])

        cmp_same = compare_versions("2.0.0-beta.1", "2.0.0-beta.1")
        self.assertTrue(cmp_same["is_same"])

    def test_version_info_structure(self):
        """get_version_info returns valid payload with compatibility facts."""
        info = get_version_info()
        self.assertEqual(info.version, ANTIOS_VERSION)
        self.assertEqual(info.channel, "beta")
        self.assertTrue(info.is_prerelease)
        d = info.to_dict()
        self.assertIn("antigravity", d["compatibility"])
        self.assertIn("python", d["compatibility"])


if __name__ == "__main__":
    unittest.main()
