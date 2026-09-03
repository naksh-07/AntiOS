"""Tests for framework.core.workflow."""

import os
from framework.core.lifecycle import TaskClass, TaskStage
from framework.core.workflow import (
    WORKFLOW_REGISTRY,
    get_workflow,
    list_workflows,
    validate_workflow_step,
)

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".agents", "workflows")


def test_all_canonical_workflows_registered():
    workflows = list_workflows()
    assert len(workflows) == 6

    expected_classes = [
        TaskClass.FEATURE,
        TaskClass.BUG,
        TaskClass.REFACTOR,
        TaskClass.INVESTIGATION,
        TaskClass.DOCUMENTATION,
        TaskClass.RELEASE,
    ]
    for tc in expected_classes:
        spec = get_workflow(tc)
        assert spec is not None
        assert spec.task_class == tc
        assert len(spec.steps) == 10
        assert len(spec.entry_conditions) > 0
        assert len(spec.completion_criteria) > 0
        assert len(spec.recovery_path) > 0
        assert len(spec.composed_skills) > 0


def test_workflow_skill_composition():
    bug_wf = get_workflow(TaskClass.BUG)
    assert "antios-debug" in bug_wf.composed_skills
    assert "antios-engineer" in bug_wf.composed_skills

    feature_wf = get_workflow(TaskClass.FEATURE)
    assert "antios-engineer" in feature_wf.composed_skills
    assert "antios-verifier" in feature_wf.composed_skills

    refactor_wf = get_workflow(TaskClass.REFACTOR)
    assert "antios-verifier" in refactor_wf.composed_skills


def test_workflow_step_validation():
    assert validate_workflow_step(TaskClass.FEATURE, TaskStage.IMPLEMENT) is True
    assert validate_workflow_step(TaskClass.BUG, TaskStage.TEST) is True


def test_workflow_markdown_files_exist():
    assert os.path.isdir(WORKFLOWS_DIR)
    expected_files = [
        "README.md",
        "FEATURE.md",
        "BUG.md",
        "REFACTOR.md",
        "INVESTIGATION.md",
        "DOCUMENTATION.md",
        "RELEASE_MAINTENANCE.md",
    ]
    for filename in expected_files:
        filepath = os.path.join(WORKFLOWS_DIR, filename)
        assert os.path.isfile(filepath), f"Workflow file missing: {filepath}"
