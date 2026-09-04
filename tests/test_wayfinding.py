"""Unit tests for AntiOS Wayfinding & Locality Engine."""

from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine, LocalityResolution


def _build_test_engine():
    engine = WayfindingEngine(workspace_root="/repo")

    auth_decl = SubsystemDeclaration(
        subsystem_id="auth",
        name="Authentication Subsystem",
        description="User identity, login, JWT token handling, and session auth.",
        area="core",
        root_paths=["src/auth"],
        entrypoints=["src/auth/service.py"],
        authoritative_files=["src/auth/service.py", "src/auth/types.py"],
        covering_tests=["tests/test_auth.py"],
        test_commands=["pytest tests/test_auth.py"],
        applicable_skills=["antios-engineer", "antios-debug"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Never log plain passwords or JWT secrets"],
        protected_invariants=["src/auth/crypto.py"],
        dependencies=["db"],
        consumers=["api-gateway", "billing", "users"],
        documentation_paths=["docs/subsystems/auth.md"],
        keywords=["auth", "login", "jwt", "session", "password", "token"],
    )

    billing_decl = SubsystemDeclaration(
        subsystem_id="billing",
        name="Billing & Payments",
        description="Processes customer invoices, Stripe webhooks, and subscriptions.",
        area="finance",
        root_paths=["src/billing"],
        entrypoints=["src/billing/checkout.py"],
        authoritative_files=["src/billing/checkout.py"],
        covering_tests=["tests/test_billing.py"],
        test_commands=["pytest tests/test_billing.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=["Strict idempotency on payment charges"],
        protected_invariants=[],
        dependencies=["auth", "db"],
        consumers=["reports"],
        documentation_paths=["docs/subsystems/billing.md"],
        keywords=["billing", "payment", "stripe", "invoice", "subscription", "checkout"],
    )

    engine.register_subsystem(auth_decl)
    engine.register_subsystem(billing_decl)
    return engine


def test_wayfinding_list_and_get_subsystems():
    engine = _build_test_engine()
    all_subs = engine.list_subsystems()
    assert len(all_subs) == 2

    auth = engine.get_subsystem("auth")
    assert auth is not None
    assert auth.subsystem_id == "auth"

    missing = engine.get_subsystem("nonexistent")
    assert missing is None


def test_wayfinding_resolve_file_exact_match():
    engine = _build_test_engine()
    res = engine.resolve_file("src/auth/service.py")
    assert res is not None
    assert res.matched_subsystem_id == "auth"
    assert res.confidence == 1.0
    assert res.entrypoints == ["src/auth/service.py"]
    assert res.covering_tests == ["tests/test_auth.py"]

    res2 = engine.resolve_file("src/billing/handlers/webhook.py")
    assert res2 is not None
    assert res2.matched_subsystem_id == "billing"
    assert res2.confidence == 1.0


def test_wayfinding_resolve_file_windows_and_posix_separators():
    engine = _build_test_engine()
    res = engine.resolve_file("src\\auth\\submodule\\token.py")
    assert res is not None
    assert res.matched_subsystem_id == "auth"


def test_wayfinding_resolve_file_unmapped_returns_none():
    engine = _build_test_engine()
    res = engine.resolve_file("unrelated/docs/guide.txt")
    assert res is None


def test_wayfinding_locate_by_subsystem_id():
    engine = _build_test_engine()
    res = engine.locate("auth")
    assert res is not None
    assert res.matched_subsystem_id == "auth"
    assert res.confidence == 1.0


def test_wayfinding_locate_by_keyword():
    engine = _build_test_engine()
    res = engine.locate("Stripe payment webhook")
    assert res is not None
    assert res.matched_subsystem_id == "billing"
    assert res.confidence >= 0.4

    res2 = engine.locate("user session JWT token expiration")
    assert res2 is not None
    assert res2.matched_subsystem_id == "auth"


def test_wayfinding_locate_by_file_path():
    engine = _build_test_engine()
    res = engine.locate("src/auth/types.py")
    assert res is not None
    assert res.matched_subsystem_id == "auth"
    assert res.confidence == 1.0


def test_wayfinding_locate_empty_query():
    engine = _build_test_engine()
    assert engine.locate("") is None
    assert engine.locate("   ") is None
    assert engine.locate(None) is None


def test_wayfinding_format_locator_card():
    engine = _build_test_engine()
    res = engine.locate("auth")
    assert res is not None
    card = engine.format_locator_card(res)
    assert "=== ANTIOS WAYFINDING LOCATOR ===" in card
    assert "Subsystem:   auth" in card
    assert "Entrypoints: src/auth/service.py" in card
    assert "Tests:       tests/test_auth.py" in card
    assert "Runners:     pytest tests/test_auth.py" in card
    assert "Invariants:  Immutable: src/auth/crypto.py" in card

    lines = card.strip().splitlines()
    assert len(lines) <= 20


def test_wayfinding_multiple_root_paths_resolution():
    """Subsystem declaring multiple root paths correctly indexes and resolves under all paths."""
    multi_sub = SubsystemDeclaration(
        subsystem_id="multi_root",
        name="Multi Root Subsystem",
        description="Subsystem spanning multiple root paths",
        area="core",
        root_paths=["src/multi_a", "src/multi_b"],
        entrypoints=["src/multi_a/main.py"],
        authoritative_files=[],
        covering_tests=[],
        test_commands=[],
        applicable_skills=[],
        applicable_workflows=[],
        governing_rules=[],
        protected_invariants=[],
        dependencies=[],
        consumers=[],
        documentation_paths=[],
        keywords=["multi"],
    )
    engine = WayfindingEngine()
    engine.register_subsystem(multi_sub)
    res_a = engine.resolve_file("src/multi_a/worker.py")
    res_b = engine.resolve_file("src/multi_b/worker.py")
    assert res_a is not None
    assert res_a.matched_subsystem_id == "multi_root"
    assert res_b is not None
    assert res_b.matched_subsystem_id == "multi_root"
