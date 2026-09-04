"""Adversarial stress and edge-case test campaign for AntiOS Wayfinding Engine."""

import tempfile

from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


def _build_adversarial_engine(tmpdir: str):
    engine = WayfindingEngine(workspace_root=tmpdir)

    auth = SubsystemDeclaration(
        subsystem_id="auth",
        name="Auth Core",
        description="Core authentication module",
        area="security",
        root_paths=["src/auth"],
        entrypoints=["src/auth/index.ts"],
        authoritative_files=["src/auth/index.ts"],
        covering_tests=["tests/auth.test.ts"],
        test_commands=["npm test -- tests/auth.test.ts"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=["Immutable crypto"],
        protected_invariants=["src/auth/keys.ts"],
        dependencies=["oauth"],
        consumers=["api"],
        documentation_paths=["docs/auth.md"],
        keywords=["auth", "jwt", "login"],
    )

    oauth = SubsystemDeclaration(
        subsystem_id="oauth",
        name="OAuth Provider",
        description="OAuth2 and OIDC integration",
        area="security",
        root_paths=["src/auth/oauth"],
        entrypoints=["src/auth/oauth/client.ts"],
        authoritative_files=["src/auth/oauth/client.ts"],
        covering_tests=["tests/oauth.test.ts"],
        test_commands=["npm test -- tests/oauth.test.ts"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=[],
        protected_invariants=[],
        dependencies=["auth"],  # Circular dependency with auth
        consumers=["auth"],
        documentation_paths=["docs/oauth.md"],
        keywords=["oauth", "google", "github", "oidc"],
    )

    engine.register_subsystem(auth)
    engine.register_subsystem(oauth)
    return engine


def test_adversarial_wayfinding_01_path_traversal_escape():
    """Attacker attempts to locate paths outside the workspace via path traversal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        traversal_query_1 = "../../../../etc/passwd"
        traversal_query_2 = "..\\..\\Windows\\System32\\cmd.exe"
        traversal_query_3 = f"{tmpdir}/../../../../sensitive/config.env"

        assert engine.resolve_file(traversal_query_1) is None
        assert engine.resolve_file(traversal_query_2) is None
        assert engine.locate(traversal_query_3) is None


def test_adversarial_wayfinding_02_longest_prefix_matching():
    """Conflicting overlapping prefixes must resolve to the most specific child subsystem."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        # src/auth/oauth/callback.ts is under both src/auth AND src/auth/oauth
        res = engine.resolve_file("src/auth/oauth/callback.ts")
        assert res is not None
        assert res.matched_subsystem_id == "oauth"
        assert res.confidence == 1.0

        # File directly in parent auth
        res_parent = engine.resolve_file("src/auth/token.ts")
        assert res_parent is not None
        assert res_parent.matched_subsystem_id == "auth"


def test_adversarial_wayfinding_03_circular_dependency_graph():
    """Subsystems with circular dependencies (auth <-> oauth) must index and resolve without recursion limits."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        res_auth = engine.locate("auth")
        assert res_auth is not None
        assert res_auth.dependencies == ["oauth"]
        assert res_auth.consumers == ["api"]

        res_oauth = engine.locate("oauth")
        assert res_oauth is not None
        assert res_oauth.dependencies == ["auth"]


def test_adversarial_wayfinding_04_token_flood_extreme_length():
    """Attacker submits massive query payload (10,000 characters) to exhaust regex or memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        flood_query = "word " * 2000
        res = engine.locate(flood_query)
        assert res is None


def test_adversarial_wayfinding_05_pure_punctuation_and_injection():
    """Attacker passes SQL injection, XSS, or command injection strings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        injections = [
            "'; DROP TABLE users; --",
            "<script>alert(1)</script>",
            "$(cat /etc/shadow)",
            "| rm -rf /",
            "`calc.exe`",
            "!@#$%^&*()_+~`|}{[]:;?><,.",
        ]
        for inj in injections:
            assert engine.locate(inj) is None


def test_adversarial_wayfinding_06_malformed_declaration_fails_closed():
    """Attempting to construct declarations with invalid or missing types fails closed."""
    try:
        SubsystemDeclaration.from_dict({"subsystem_id": ""})
        assert False, "Should fail on empty id"
    except ValueError:
        pass

    try:
        SubsystemDeclaration.from_dict({"subsystem_id": None})
        assert False, "Should fail on None id"
    except ValueError:
        pass


def test_adversarial_wayfinding_07_unmapped_random_queries():
    """Completely random or nonsense words must fail safely and return None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = _build_adversarial_engine(tmpdir)
        nonsense = [
            "supercalifragilisticexpialidocious",
            "quantum_flux_antigravity_propulsion",
            "zzzzzz_nonexistent_xyz",
        ]
        for n in nonsense:
            assert engine.locate(n) is None
            assert engine.resolve_file(f"random/{n}.py") is None
