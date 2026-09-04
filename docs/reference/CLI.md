# AntiOS Deterministic CLI Reference (`docs/reference/CLI.md`)

AntiOS provides 8 deterministic CLI tools located in `framework/scripts/tools/`. All tools require standard library Python only, accept optional `--json` formatting, and exit 0 on success.

---

## 1. `inspect_repo.py` — Repository Inspector
Inspects a target directory for git state, manifests, available host toolchains, and AntiOS governance configuration.

### Usage
```bash
python framework/scripts/tools/inspect_repo.py [repo_root]
```

### Outputs
Structured JSON containing:
- `is_git_repo`: Boolean git detection.
- `has_antios_config`: Presence of `antios.config.json`.
- `has_agents_dir`, `has_framework_dir`, `has_hooks_json`: Governance integrity checks.
- `available_runners`: Detected test runners and linters available on host PATH.

---

## 2. `adapt_project.py` — Project Adapter Generator
Inspects an unfamiliar repository, constructs its `ProjectProfile`, evaluates adaptation requirements, and generates or applies `antios.config.json`.

### Usage
```bash
python framework/scripts/tools/adapt_project.py <repo_root> [--dry-run] [--apply] [--verify] [--json]
```

### Flags
- `--dry-run`: Evaluate adaptation and print `AdaptationProposal` without modifying disk.
- `--apply`: Write generated `antios.config.json` and `.agents/` scaffolds to the target repository.
- `--verify`: Verify existing adapter configuration against physical repository traits.
- `--json`: Emit machine-readable JSON output.

---

## 3. `navigate_repo.py` — Wayfinding & Subsystem Navigator
Resolves task intent, queries, or file paths to owning subsystems, entrypoints, covering test suites, invariants, and tool selections.

### Usage
```bash
python framework/scripts/tools/navigate_repo.py --query "auth"
python framework/scripts/tools/navigate_repo.py --file "src/core/auth.py"
python framework/scripts/tools/navigate_repo.py --list
python framework/scripts/tools/navigate_repo.py --tools
python framework/scripts/tools/navigate_repo.py --providers
```

### Flags
- `--query <string>`: Search subsystems by natural language query or intent.
- `--file <path>`: Find owning subsystem, test suites, and blast radius for a file.
- `--list`: List all registered subsystems and manifests.
- `--tools`: Display registered tool catalog and tier classifications.
- `--providers`: Display registered tool providers.
- `--tool-selection`: Output recommended tool routing pack for the task.
- `--json`: Emit structured locator card in JSON format.

---

## 4. `audit_docs.py` — Syntactic Documentation Auditor
Audits documentation files and subsystem manifests for broken file references, invalid markdown links, and dead test commands against the physical workspace.

### Usage
```bash
python framework/scripts/tools/audit_docs.py --all
python framework/scripts/tools/audit_docs.py --file README.md
python framework/scripts/tools/audit_docs.py --path docs/
python framework/scripts/tools/audit_docs.py --all --json
```

### Flags
- `--all`: Audit all markdown files across `docs/` and `.agents/`.
- `--file <path>`: Audit a single specific markdown file.
- `--path <dir>`: Audit all markdown files within a directory.
- `--json`: Emit structured validation report in JSON format.
- *Exit Code*: Returns `0` if 100% clean, `1` if any broken reference is detected.

---

## 5. `check_changeset.py` — Same Change Set Integrity Checker
Evaluates whether the current git working tree satisfies the Same Change Set discipline (functional code changes must be accompanied by documentation and test updates).

### Usage
```bash
python framework/scripts/tools/check_changeset.py [repo_root]
```

### Outputs
Structured JSON containing:
- `is_valid`: Boolean indicating whether changeset passes policy.
- `code_changed`, `docs_changed`, `tests_changed`: Category touch flags.
- `violations`: List of specific policy violations (e.g. missing doc update for code edit).

---

## 6. `check_worktree.py` — Working Tree & Conflict Inspector
Captures a snapshot of git working tree state and audits for merge conflicts, conflict markers, and unexpected dirty state.

### Usage
```bash
python framework/scripts/tools/check_worktree.py [repo_root]
```

### Outputs
Structured JSON containing:
- `snapshot`: Git commit SHA, branch, staged files, unstaged files, untracked files.
- `conflicts`: List of detected merge conflict markers.
- `is_clean`: Boolean cleanliness indicator.

---

## 7. `distill_memory.py` — Memory & Lesson Distillation Tool
Inspects, audits, and promotes candidate cross-session lessons in `docs/LESSONS.md` based on deterministic recurrence thresholds and verified task evidence.

### Usage
```bash
python framework/scripts/tools/distill_memory.py [repo_root] [--audit] [--sync]
```

### Flags
- `--audit`: Audit existing candidate lessons for evidence thresholds.
- `--sync`: Promote qualified candidates to durable lessons and synchronize state.

---

## 8. `recover_session.py` — Session Recovery & State Reconstructor
Inspects recorded task state against git working tree reality, detects state contradictions, evaluates verification staleness, and applies deterministic recovery.

### Usage
```bash
python framework/scripts/tools/recover_session.py <repo_root> [--apply] [--json]
```

### Flags
- `--apply`: Safely reconcile contradictory task state with physical git state.
- `--json`: Emit state reconstruction report in JSON format.
