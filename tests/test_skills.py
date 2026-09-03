"""Tests for AntiOS Skills, Platform Discovery Layer, and Universality."""

import os
import re
import json

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
SKILLS_DIR = os.path.join(REPO_ROOT, ".agents", "skills")


def test_skills_exist_and_conform_to_budget():
    assert os.path.isdir(SKILLS_DIR), ".agents/skills directory must exist"

    expected_skills = ["antios-engineer", "antios-verifier", "antios-debug", "antios-adapt-project"]
    for skill_name in expected_skills:
        skill_file = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        assert os.path.isfile(skill_file), f"Skill file for {skill_name} must exist at {skill_file}"

        with open(skill_file, "r", encoding="utf-8-sig") as f:
            content = f.read()

        lines = content.splitlines()
        # Strictly enforce <= 60 lines budget
        assert len(lines) <= 60, f"Skill {skill_name} exceeds token budget: {len(lines)} lines (max 60)"

        # Verify YAML frontmatter
        assert content.startswith("---"), f"Skill {skill_name} must start with YAML frontmatter"
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        assert match is not None, f"Skill {skill_name} missing closing --- for frontmatter"
        fm = match.group(1)
        assert "name:" in fm, f"Skill {skill_name} frontmatter must specify 'name'"
        assert "description:" in fm, f"Skill {skill_name} frontmatter must specify 'description'"


def test_skills_and_core_are_project_agnostic():
    """Universality test: verify skills and core do not hardcode StudyLab or StudySourceCore."""
    forbidden_terms = ["rslib", "studylab", "studysource"]

    check_dirs = [
        os.path.join(REPO_ROOT, ".agents", "skills"),
        os.path.join(REPO_ROOT, "framework", "core"),
    ]

    for check_dir in check_dirs:
        for root, _, files in os.walk(check_dir):
            for file in files:
                if file.endswith((".py", ".md")):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read().lower()
                    for term in forbidden_terms:
                        assert term not in text, f"Forbidden project term '{term}' found in {filepath}"


def test_legacy_studylab_task_runner_pruned():
    legacy_path = os.path.join(REPO_ROOT, "framework", ".agents", "skills", "studylab-task-runner", "SKILL.md")
    assert not os.path.exists(legacy_path), "Legacy studylab-task-runner must be completely pruned"


def test_hooks_json_valid_at_root():
    hooks_file = os.path.join(REPO_ROOT, ".agents", "hooks.json")
    assert os.path.isfile(hooks_file), ".agents/hooks.json must exist at root"

    with open(hooks_file, "r", encoding="utf-8-sig") as f:
        hooks = json.load(f)

    assert "antios-guard" in hooks
    assert "PreToolUse" in hooks["antios-guard"]
    assert "Stop" in hooks["antios-guard"]
