"""
AntiOS 3.0 Stage 1 — Compiler & Project Intelligence Test Suite

Comprehensive test suite validating:
1. Project discovery across Python, TypeScript, Rust, Go, and mixed repositories
2. Manifest detection & malformed manifest resilience
3. Deterministic and idempotent compilation
4. Python AST extraction with exact 1-indexed line ranges
5. Unsupported language graceful degradation without fake AST data
6. Subsystem route generation and proving test binding
7. Turn-0 AGENTS.md strict line and token budget constraints (<= 40 lines, < 250 tokens)
8. Artifact ownership and user-authored conflict preservation
9. Canonical JSON serialization (stable ordering, LF endings, no volatile timestamps)
10. Path portability (POSIX forward slashes, zero absolute paths)
11. CLI integration (--check, --json, --force)
12. Performance benchmark on AntiOS repository (<100ms baseline)
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

from framework.compiler.ast_extractor import ASTSymbolExtractor, FileSymbolOutline
from framework.compiler.compiler import CompilationResult, ProjectEnvironmentCompiler, compile_project
from framework.compiler.emit import CANONICAL_SIGNATURE, ArtifactEmitter
from framework.compiler.project_model import Confidence, DiscoveredSignal, ProjectInspector, ProjectModel, SignalKind
from framework.compiler.routes import RouteMapGenerator
from framework.cli import cmd_compile, build_parser


class TestProjectDiscovery(unittest.TestCase):
    """Tests for project discovery across ecosystems."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_discovery_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_project_discovery_python(self):
        """Python project layout discovery with pyproject.toml and tests."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text('[project]\nname = "my-python-app"\nversion = "1.0.0"\n', encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "my_app").mkdir()
        (root / "src" / "my_app" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_app.py").write_text("def test_dummy(): pass\n", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        self.assertEqual(model.project_id, "my-python-app")
        self.assertIn("python", model.languages)
        self.assertIn("pyproject.toml", model.manifests)
        self.assertIn("src", model.source_roots)
        self.assertIn("tests", model.test_roots)
        self.assertIn("src/my_app", model.package_roots)

    def test_project_discovery_ts(self):
        """TypeScript project layout discovery with package.json and tsconfig.json."""
        root = Path(self.temp_dir)
        (root / "package.json").write_text('{"name": "@org/web-service", "version": "0.1.0"}', encoding="utf-8")
        (root / "tsconfig.json").write_text('{"compilerOptions": {}}', encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "index.ts").write_text("export const a = 1;", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        self.assertEqual(model.project_id, "web-service")
        self.assertIn("typescript", model.languages)
        self.assertIn("javascript", model.languages)
        self.assertIn("package.json", model.manifests)

    def test_project_discovery_rust(self):
        """Rust single-crate layout discovery."""
        root = Path(self.temp_dir)
        (root / "Cargo.toml").write_text('[package]\nname = "fast-indexer"\nversion = "0.1.0"\n', encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "main.rs").write_text("fn main() {}", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        self.assertEqual(model.project_id, "fast-indexer")
        self.assertIn("rust", model.languages)
        self.assertIn("Cargo.toml", model.manifests)

    def test_project_discovery_go(self):
        """Go project layout discovery with go.mod."""
        root = Path(self.temp_dir)
        (root / "go.mod").write_text("module github.com/example/api-gateway\n\ngo 1.21\n", encoding="utf-8")
        (root / "main.go").write_text("package main\nfunc main() {}\n", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        self.assertEqual(model.project_id, "api-gateway")
        self.assertIn("go", model.languages)
        self.assertIn("go.mod", model.manifests)

    def test_project_discovery_mixed(self):
        """Polyglot repository with Python and TypeScript."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text('[project]\nname = "mixed-repo"\n', encoding="utf-8")
        (root / "package.json").write_text('{"name": "frontend"}\n', encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        self.assertIn("python", model.languages)
        self.assertTrue("typescript" in model.languages or "javascript" in model.languages)
        self.assertIn("pyproject.toml", model.manifests)
        self.assertIn("package.json", model.manifests)


    def test_malformed_manifest_resilience(self):
        """Corrupt manifests must be handled gracefully without crashing."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text("MALFORMED TOML {[[[", encoding="utf-8")
        (root / "package.json").write_text("INVALID JSON", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()

        # Should fall back to directory basename without raising
        self.assertTrue(len(model.project_id) > 0)
        self.assertIn("pyproject.toml", model.manifests)
        self.assertIn("package.json", model.manifests)

    def test_empty_repository(self):
        """An empty directory compiles safely without exceptions."""
        root = Path(self.temp_dir)
        compiler = ProjectEnvironmentCompiler()
        result = compiler.compile(root)

        self.assertTrue(result.success)
        self.assertTrue(len(result.project_id) > 0)
        self.assertIn(".agents/routes.json", result.emitted_files)
        self.assertIn("AGENTS.md", result.emitted_files)


class TestASTSymbolExtraction(unittest.TestCase):
    """Tests for zero-dependency Python AST symbol extraction."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_ast_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_python_ast_extraction_classes_and_methods(self):
        """Accurately extracts classes, methods, signatures, and line ranges."""
        code = '''"""Module docstring."""

class AuthenticationService:
    """Handles user logins and tokens."""

    def __init__(self, secret: str):
        self.secret = secret

    async def authenticate(self, username: str, token: str) -> bool:
        """Authenticate user credentials."""
        return True


def standalone_helper(x: int, y: int = 10) -> int:
    """Helper function."""
    return x + y
'''
        file_path = Path(self.temp_dir) / "service.py"
        file_path.write_text(code, encoding="utf-8")

        outline = ASTSymbolExtractor.extract_file(file_path, "service.py")

        self.assertEqual(outline.language, "python")
        self.assertEqual(outline.extractor, "python_ast")
        self.assertEqual(outline.confidence, 1.0)
        self.assertIsNone(outline.parse_error)

        # Classes
        self.assertEqual(len(outline.classes), 1)
        cls_sym = outline.classes[0]
        self.assertEqual(cls_sym.name, "AuthenticationService")
        self.assertEqual(cls_sym.start_line, 3)
        self.assertEqual(cls_sym.end_line, 11)
        self.assertEqual(cls_sym.docstring, "Handles user logins and tokens.")

        # Methods
        self.assertEqual(len(cls_sym.methods), 2)
        m1 = cls_sym.methods[0]
        self.assertEqual(m1.name, "__init__")
        self.assertIn("secret", m1.signature)

        m2 = cls_sym.methods[1]
        self.assertEqual(m2.name, "authenticate")
        self.assertEqual(m2.qualified_name, "AuthenticationService.authenticate")
        self.assertTrue(m2.is_async)
        self.assertIn("username", m2.signature)
        self.assertIn("-> bool", m2.signature)
        self.assertEqual(m2.start_line, 9)
        self.assertEqual(m2.end_line, 11)

        # Standalone function
        self.assertEqual(len(outline.functions), 1)
        fn_sym = outline.functions[0]
        self.assertEqual(fn_sym.name, "standalone_helper")
        self.assertFalse(fn_sym.is_async)
        self.assertIn("x: int", fn_sym.signature)
        self.assertEqual(fn_sym.start_line, 14)
        self.assertEqual(fn_sym.end_line, 16)

    def test_unsupported_language_fallback(self):
        """Non-Python files must not synthesize fake AST data."""
        ts_file = Path(self.temp_dir) / "app.ts"
        ts_file.write_text("export class Router { route() {} }", encoding="utf-8")

        outline = ASTSymbolExtractor.extract_file(ts_file, "app.ts")
        self.assertEqual(outline.language, "typescript")
        self.assertEqual(outline.extractor, "unsupported")
        self.assertEqual(outline.confidence, 0.0)
        self.assertEqual(len(outline.classes), 0)
        self.assertEqual(len(outline.functions), 0)

    def test_python_syntax_error_resilience(self):
        """Python syntax errors are caught and recorded safely."""
        bad_file = Path(self.temp_dir) / "broken.py"
        bad_file.write_text("def unclosed_fn(", encoding="utf-8")

        outline = ASTSymbolExtractor.extract_file(bad_file, "broken.py")
        self.assertEqual(outline.language, "python")
        self.assertEqual(outline.confidence, 0.0)
        self.assertIsNotNone(outline.parse_error)
        self.assertIn("SyntaxError", outline.parse_error)


class TestRoutesAndBinding(unittest.TestCase):
    """Tests for routes.json generation and test binding."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_routes_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_subsystem_route_generation(self):
        """Discovers subsystems from layout and builds schema-compliant routes.json."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text('[project]\nname = "demo-system"\n', encoding="utf-8")

        # Subsystem 1: auth
        auth_dir = root / "src" / "auth"
        auth_dir.mkdir(parents=True)
        (auth_dir / "service.py").write_text("# INV-04\ndef login(): pass\n", encoding="utf-8")

        # Subsystem 2: storage
        storage_dir = root / "src" / "storage"
        storage_dir.mkdir(parents=True)
        (storage_dir / "db.py").write_text("def connect(): pass\n", encoding="utf-8")

        # Tests
        tests_dir = root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_auth.py").write_text("def test_login(): pass\n", encoding="utf-8")

        inspector = ProjectInspector(root)
        model = inspector.inspect()
        route_gen = RouteMapGenerator(model)
        routes = route_gen.generate()

        self.assertEqual(routes["$schema"], "https://antios.dev/schemas/v3/routes.json")
        self.assertEqual(routes["project_id"], "demo-system")
        self.assertIn("auth", routes["subsystems"])
        self.assertIn("storage", routes["subsystems"])

        # Check auth entrypoint and test binding
        auth_sub = routes["subsystems"]["auth"]
        self.assertEqual(auth_sub["root_dir"], "src/auth")
        self.assertEqual(auth_sub["entrypoint"], "src/auth/service.py")
        self.assertIn("INV-04", auth_sub["invariants"])
        self.assertIn("login", auth_sub["capabilities"])
        self.assertEqual(auth_sub["test_suite"], ["python", "-m", "unittest", "tests.test_auth"])

        # Check storage entrypoint
        storage_sub = routes["subsystems"]["storage"]
        self.assertEqual(storage_sub["root_dir"], "src/storage")
        self.assertEqual(storage_sub["entrypoint"], "src/storage/db.py")


class TestTurn0AgentsMdAndOwnership(unittest.TestCase):
    """Tests for AGENTS.md size bounds, token ceiling, and ownership conflict preservation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_agents_md_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_agents_md_budget_constraints(self):
        """AGENTS.md must strictly adhere to <= 40 lines and < 250 tokens."""
        root = Path(self.temp_dir)
        compiler = ProjectEnvironmentCompiler()
        res = compiler.compile(root)
        self.assertTrue(res.success)

        agents_md = root / "AGENTS.md"
        self.assertTrue(agents_md.is_file())
        content = agents_md.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        # Line count constraint
        self.assertLessEqual(len(lines), 40, f"AGENTS.md has {len(lines)} lines; must be <= 40")

        # Token count constraint (~1.3 tokens per word)
        word_count = len(content.split())
        token_estimate = int(word_count * 1.3)
        self.assertLess(token_estimate, 250, f"AGENTS.md has ~{token_estimate} tokens; must be < 250")

        # Content presence
        self.assertIn(CANONICAL_SIGNATURE, content)
        self.assertIn("Turn-0 Orientation", content)
        self.assertIn(".agents/routes.json", content)
        self.assertIn("Verification Law", content)

    def test_user_authored_conflict_preservation(self):
        """User-authored AGENTS.md must NEVER be silently overwritten unless --force is used."""
        root = Path(self.temp_dir)
        user_content = "# My Custom Hand-Crafted Instructions\nDo not touch this.\n"
        agents_md = root / "AGENTS.md"
        agents_md.write_text(user_content, encoding="utf-8")

        compiler = ProjectEnvironmentCompiler()
        res = compiler.compile(root, force=False)

        # Original user file must be preserved
        self.assertEqual(agents_md.read_text(encoding="utf-8"), user_content)

        # Generated version emitted as AGENTS.generated.md
        gen_md = root / "AGENTS.generated.md"
        self.assertTrue(gen_md.is_file())
        self.assertTrue(any("AGENTS.generated.md" in w for w in res.warnings))

        # With force=True, user file can be overwritten
        res_force = compiler.compile(root, force=True)
        self.assertIn(CANONICAL_SIGNATURE, agents_md.read_text(encoding="utf-8"))


class TestDeterminismAndIdempotency(unittest.TestCase):
    """Tests for byte-for-byte determinism and path portability."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_idempotence_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_idempotent_and_deterministic_compilation(self):
        """Repeated compilation on unchanged repo produces byte-for-byte identical output."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text('[project]\nname = "stable-proj"\n', encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "core.py").write_text("def run(): pass\n", encoding="utf-8")

        compiler = ProjectEnvironmentCompiler()

        # Run 1
        res1 = compiler.compile(root)
        routes_1 = (root / ".agents" / "routes.json").read_bytes()
        agents_1 = (root / "AGENTS.md").read_bytes()
        ast_1 = (root / ".agents" / "cache" / "ast_outlines.json").read_bytes()

        # Run 2
        res2 = compiler.compile(root)
        routes_2 = (root / ".agents" / "routes.json").read_bytes()
        agents_2 = (root / "AGENTS.md").read_bytes()
        ast_2 = (root / ".agents" / "cache" / "ast_outlines.json").read_bytes()

        self.assertEqual(routes_1, routes_2)
        self.assertEqual(agents_1, agents_2)
        self.assertEqual(ast_1, ast_2)

    def test_path_portability(self):
        """All output paths use POSIX slashes and zero machine-local drive letters."""
        root = Path(self.temp_dir)
        (root / "src").mkdir()
        (root / "src" / "worker.py").write_text("def work(): pass\n", encoding="utf-8")

        compiler = ProjectEnvironmentCompiler()
        res = compiler.compile(root)

        routes_text = (root / ".agents" / "routes.json").read_text(encoding="utf-8")
        self.assertNotIn("\\\\", routes_text)
        self.assertNotIn("C:", routes_text)
        self.assertNotIn("/Users/", routes_text)
        self.assertNotIn("/home/", routes_text)

        ast_text = (root / ".agents" / "cache" / "ast_outlines.json").read_text(encoding="utf-8")
        self.assertNotIn("\\\\", ast_text)
        self.assertNotIn("C:", ast_text)


class TestCLIIntegration(unittest.TestCase):
    """Tests for antios compile CLI command."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_cli_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_compile_check_mode(self):
        """antios compile --check runs in preview mode without writing files."""
        root = Path(self.temp_dir)
        parser = build_parser()
        args = parser.parse_args(["compile", "--path", str(root), "--check"])

        code = cmd_compile(args)
        self.assertEqual(code, 0)
        self.assertFalse((root / ".agents" / "routes.json").exists())
        self.assertFalse((root / "AGENTS.md").exists())

    def test_cli_compile_json_output(self):
        """antios compile --json outputs parseable JSON result."""
        root = Path(self.temp_dir)
        parser = build_parser()
        args = parser.parse_args(["compile", "--path", str(root), "--json"])

        captured_stdout = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.stdout = captured_stdout
            code = cmd_compile(args)
        finally:
            sys.stdout = orig_stdout

        self.assertEqual(code, 0)
        output = captured_stdout.getvalue()
        data = json.loads(output)
        self.assertTrue(data["success"])
        self.assertIn("emitted_files", data)
        self.assertIn("elapsed_ms", data)

    def test_cli_compile_force_flag(self):
        """antios compile --force forces overwrite of user-authored AGENTS.md."""
        root = Path(self.temp_dir)
        user_content = "# My Custom Instructions\n"
        (root / "AGENTS.md").write_text(user_content, encoding="utf-8")

        parser = build_parser()
        args = parser.parse_args(["compile", "--path", str(root), "--force"])
        code = cmd_compile(args)

        self.assertEqual(code, 0)
        new_content = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(CANONICAL_SIGNATURE, new_content)


class TestAdversarialAndEdgeCases(unittest.TestCase):
    """Adversarial fixtures and edge cases."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_test_adversarial_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_nested_packages_and_ignored_directories(self):
        """Prunes node_modules, dist, build, .venv, .pytest_cache without exploration explosion."""
        root = Path(self.temp_dir)
        (root / "pyproject.toml").write_text('[project]\nname = "deep-project"\n', encoding="utf-8")

        # Legitimate package
        (root / "src" / "deep_pkg").mkdir(parents=True)
        (root / "src" / "deep_pkg" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "deep_pkg" / "module.py").write_text("def run(): pass\n", encoding="utf-8")

        # Ignored directories with fake files
        for ign in ("node_modules", "dist", "build", ".venv", ".pytest_cache"):
            ign_dir = root / ign
            ign_dir.mkdir()
            (ign_dir / "ignored.py").write_text("def fake(): pass\n", encoding="utf-8")
            (ign_dir / "package.json").write_text("{}", encoding="utf-8")

        compiler = ProjectEnvironmentCompiler()
        res = compiler.compile(root)

        self.assertTrue(res.success)
        routes = json.loads((root / ".agents" / "routes.json").read_text(encoding="utf-8"))
        subsystems = routes.get("subsystems", {})

        # Ignored directories must NOT appear in subsystems
        for ign in ("node_modules", "dist", "build", ".venv", ".pytest_cache"):
            self.assertNotIn(ign, subsystems)
        self.assertIn("deep_pkg", subsystems)

    def test_adversarial_misleading_names(self):
        """Handles directory named 'test.py' and file named 'tests' without crashing."""
        root = Path(self.temp_dir)
        # Directory named like a python file
        (root / "test.py").mkdir()
        (root / "test.py" / "inner.py").write_text("def dummy(): pass\n", encoding="utf-8")

        # File named 'tests' (instead of a directory)
        (root / "tests").write_text("not a directory", encoding="utf-8")

        compiler = ProjectEnvironmentCompiler()
        res = compiler.compile(root)
        self.assertTrue(res.success)

    def test_json_determinism_and_formatting(self):
        """JSON output is canonical with 2-space indentation and LF line endings."""
        root = Path(self.temp_dir)
        compiler = ProjectEnvironmentCompiler()
        compiler.compile(root)

        routes_bytes = (root / ".agents" / "routes.json").read_bytes()
        self.assertNotIn(b"\r\n", routes_bytes)
        self.assertTrue(routes_bytes.endswith(b"\n"))


class TestCompilerPerformance(unittest.TestCase):
    """Measures compilation cost on the current AntiOS repository."""

    def test_self_compilation_benchmark(self):
        """Compile the AntiOS repository and benchmark latency."""
        antios_root = Path(__file__).resolve().parent.parent
        compiler = ProjectEnvironmentCompiler()

        # Warm-up compile in check mode
        compiler.compile(antios_root, check=True)

        # Timed compile in check mode
        start = time.perf_counter()
        result = compiler.compile(antios_root, check=True)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        print(f"\n[BENCHMARK] AntiOS Self-Compilation: {elapsed_ms:.2f}ms (target <100ms)")
        self.assertTrue(result.success)
        self.assertGreater(result.subsystems_count, 0)
        self.assertLessEqual(result.agents_md_lines, 40)
        # Verify sub-100ms benchmark target
        self.assertLess(elapsed_ms, 100.0, f"Compilation took {elapsed_ms:.2f}ms, exceeding 100ms baseline")


if __name__ == "__main__":
    unittest.main()
