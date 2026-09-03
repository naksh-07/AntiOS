# Experiment 01: StudyLab Architecture Investigation

## Objective
Assess how the agent performs a broad architectural investigation of the StudyLab codebase with and without AntiOS.

## Baseline (Control)
- The agent explores the repository blindly, often reading irrelevant files or saturating the context window with standard Anki core files (e.g., `rslib/`).
- The agent has no concept of what is "out of scope" unless prompted manually.

## Treatment (AntiOS Prototype)
- The agent reads `docs/AGENTS.md` and `docs/ACTIVE_CONTEXT.md` as mandated by the `studylab-task-runner` skill.
- The agent is immediately aware that `rslib/` is upstream Anki core and must not be modified.
- The agent discovers the `ts/`, `qt/`, and `pylib/` subdirectories contextually.

## Observations
- **Context Retention:** The Bounded Memory Bank effectively anchored the agent's understanding.
- **Safety:** The explicit rules prevented time wasted analyzing upstream components.

## Result
PASS. AntiOS provides immediate, structured orientation.
