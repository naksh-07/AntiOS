# Experiment 02: Locate and Explain an Existing Subsystem

## Objective
Task the agent to locate the StudyLab card templates or UI logic and explain it.

## Baseline (Control)
- Agent searches all `.html` and `.ts` files randomly. May attempt to modify standard Anki templates.

## Treatment (AntiOS Prototype)
- Agent uses `studylab-task-runner` to map out the subsystem without making changes.
- Guided by the global constitution, it knows `StudySourceCore` is out of scope and ignores it if mentioned in documentation.

## Observations
- Agent cleanly mapped the UI components in `ts/` without touching the backend `rslib/`.

## Result
PASS. Progressive disclosure works.
