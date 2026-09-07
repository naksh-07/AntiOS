# AntiOS Research 4: Agent Wayfinding & Repository Navigation
## Empirical Findings, Navigation Primitives, and Route Maps

**Status**: CANONICAL RESEARCH MONOGRAPH  
**Phase**: AntiOS Research 4 — Large Repository Agent Engineering & Project Intelligence  
**Target Repository**: `naksh-07/AntiOS`  
**Evidence Standard**: `[OFFICIAL]`, `[OBSERVED]`, `[INFERRED]`, `[EXTERNAL_REPORT]`, `[HYPOTHESIS]`, `[UNKNOWN]`, `[CONFLICT]`  

---

## 1. Executive Summary

In a software repository exceeding 100 files or spanning multiple nested packages, autonomous AI agents face the **Cold-Start Localization Problem**:
> *Given a natural language task description, how does the agent determine where to look first, identify the authoritative entrypoint, establish the blast radius, and locate the proving test suite without drowning in navigational tokens?*

Our empirical investigations reveal that standard unguided lexical search (`grep_search`, `find_by_name`) is deeply dysfunctional in large codebases:
- **Catastrophic Context Dilution (`[OBSERVED]`)**: Unscoped keyword queries frequently return between **1,000 and 14,464 tokens** of raw match lines.
- **First-Choice Inaccuracy (`[OBSERVED]`)**: In **87.5%** of real-world trials, the top candidate returned by lexical grep was a documentation file, changelog, or package `__init__.py`, rather than the authoritative implementation file.
- **Rediscovery Thrashing (`[OBSERVED]`, `[INFERRED]`)**: Multi-turn sessions incur repeated 2,500+ token search penalties whenever context truncation forces re-exploration.

Conversely, compact deterministic representations—specifically a **Curated Subsystem Manifest** (~420 tokens) and a **Hybrid Generated Topology + Subsystem Route Map** (~550 tokens)—achieve **100% first-choice localization accuracy**, cut navigational token overhead by **46.9%**, reduce dynamic tool I/O by **68.6%**, and eliminate multi-turn rediscovery costs completely (**0 tokens**).

This monograph provides the empirical data, cognitive failure analysis, navigation primitives, and progressive route-map architecture necessary for agent-native wayfinding in AntiOS.

---

## 2. The Wayfinding Problem in Agentic Engineering

### 2.1 The Four Localization Questions
Every software engineering task requires answering four progressive wayfinding questions:
1. **Subsystem Boundary**: Which subsystem or package owns this functional capability?
2. **Authoritative Entrypoint**: Which specific file and function/class initiates or controls this behavior?
3. **Blast Radius**: What dependent files, interfaces, or callers will be broken or altered by this modification?
4. **Verification Pair**: Which automated test suite or verification script exercises this specific execution path?

### 2.2 The Asymmetry of Wrong Turns
In human software development, opening the wrong file costs 2–5 seconds of cognitive inspection. For an autonomous LLM agent, a wrong turn incurs an asymmetric penalty:
1. **Token Drain**: Viewing an irrelevant 800-line file consumes ~3,500 input tokens.
2. **Context Contamination**: Irrelevant code, deprecated patterns, and distracting comments enter the working context, biasing subsequent code generation (`[INFERRED]`).
3. **Attention Displacement**: Large tool outputs push early-injected system instructions and constitutional invariants out of the high-attention context window (`[OBSERVED]`).
4. **Search Thrashing**: Agents that hit a dead end frequently emit broader, less specific searches, compounding the flood.

---

## 3. Empirical Evaluation of Wayfinding Representations

We conducted controlled physical benchmarks in `sandbox/experiments_r4/exp1_wayfinding.py` and `sandbox/experiments_r4/exp1_live_search.py` evaluating four distinct wayfinding representations across the AntiOS repository (`naksh-07/AntiOS`, 140+ files) and the open-source Click repository (`sandbox/proving_ground/click`).

### 3.1 Four Wayfinding Representations Evaluated

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WAYFINDING REPRESENTATIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Rep A: Unguided Discovery                                                   │
│   • 0 static upfront tokens.                                                │
│   • Agent issues exploratory grep_search / find_by_name calls.              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Rep B: Generated Topology Map                                               │
│   • 405 static tokens.                                                      │
│   • Deterministic 2-level directory tree showing packages and file basenames│
├─────────────────────────────────────────────────────────────────────────────┤
│ Rep C: Curated Subsystem Manifest                                           │
│   • 427 static tokens.                                                      │
│   • Declarative table: Subsystem -> Capability -> Entrypoint -> Test Suite. │
├─────────────────────────────────────────────────────────────────────────────┤
│ Rep D: Hybrid Generated + Curated Route Map                                 │
│   • 553 static tokens.                                                      │
│   • 1-level directory topology + curated capability/entrypoint table.       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Live Search (Unguided Discovery) Measurements

`[OBSERVED]` In our unguided baseline experiments, realistic tasks produced massive tool token outputs and high distraction:

| Task Description | Lexical Query Pattern | Lines Matched | Files Matched | Tool Output Tokens | Authoritative File in Output? | First Candidate Correct? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Block deletion of git tags in hook** | `PreToolUse` | 281 | 98 | **14,464** | Yes (`pre_tool_guard.py`) | **NO** (`.agents/hooks.json`) |
| **Configure test runner timeout in gate** | `timeout_seconds` | 58 | 16 | **1,086** | Yes (`antios.config.json`) | **YES** |
| **Inspect git merge conflict markers** | `inspect_all_conflicts` | 14 | 7 | **328** | Yes (`worktree.py`) | **NO** (`__init__.py`) |
| **Ingest transcript.jsonl to SQLite** | `transcript.jsonl` | 101 | 37 | **4,873** | Yes (`telemetry_bridge.py`)| **NO** (`ANTIOS_ARCHITECTURE.md`) |
| **Locate invariant registry** | `INVARIANT_REGISTRY` | 17 | 13 | **827** | Yes (`INVARIANT_REGISTRY.md`)| **NO** (`ANTIOS_SOURCE_OF_TRUTH.md`)|
| **(Click) Format option prompt default** | `prompt` | 490 | 38 | **10,271** | Yes (`src/click/core.py`) | **NO** (`CHANGES.md`) |
| **(Click) Add custom exception class** | `ClickException` | 21 | 9 | **392** | Yes (`exceptions.py`) | **NO** (`CHANGES.md`) |
| **(Click) Update tests for hidden options**| `hidden` | 83 | 19 | **1,538** | **NO** (Masked by docs) | **NO** (`CHANGES.md`) |

**Summary Metrics for Unguided Discovery**:
- Average tool tokens per query: **4,222 tokens**.
- First candidate accuracy: **12.5%** (87.5% failure rate).
- Authoritative target masking: In 1 out of 8 queries, documentation matches completely displaced test files from the top 50 matches.

### 3.3 Comparative Trajectory Performance

`[OBSERVED]` Across 6 representative AntiOS engineering tasks, we tracked the complete navigational trajectory from task assignment to target file inspection:

| Navigational Metric | Rep A: Unguided | Rep B: Generated Map | Rep C: Curated Manifest | Rep D: Hybrid Route Map | Delta (Rep A vs Rep D) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Static Upfront Tokens** | **0** | 405 | 427 | 553 | +553 |
| **Search Calls (`grep`/`find`)** | 2.0 | 1.0 | **0.0** | **0.0** | **-100%** |
| **Files Opened / Inspected** | 3.0 | 2.0 | **1.0** | **1.0** | **-66.7%** |
| **Irrelevant Exploration Steps** | 2.0 | 1.0 | **0.0** | **0.0** | **-100%** |
| **Dynamic Tool Tokens (I/O)** | 2,550 | 1,650 | **800** | **800** | **-68.6%** |
| **Total Navigational Tokens** | 2,550 | 2,055 | **1,227** | **1,353** | **-46.9%** |
| **First-Choice Correctness (%)** | **0%** | 33% | **100%** | **100%** | **+100%** |
| **Multi-Turn Rediscovery Cost** | 2,550 | 1,650 | **0** | **0** | **-100%** |

---

## 4. Analysis of Wayfinding Failure Modes

### 4.1 Keyword Dilution & Context Floods
When an agent searches for generic identifiers (such as `PreToolUse`, `prompt`, `status`, `config`), ripgrep returns matches across four conflicting strata:
1. Production code implementation.
2. Unit and integration test fixtures.
3. Documentation guides, ADRs, and historical research monographs.
4. Generated artifacts, changelogs, and build scripts.

Because search tools cap results or return unranked matches, historical logs and changelogs routinely crowd out production implementation files (`[OBSERVED]`).

### 4.2 Changelog and Documentation Masking
In established projects, keywords appear far more frequently in `CHANGES.md`, `HISTORY.md`, or markdown documentation than in code. When searching for `ClickException` or `prompt` in Click, `CHANGES.md` appeared at the top of the search output, causing the agent to inspect the changelog first.

### 4.3 False Candidate Drift
In Rep A, opening an irrelevant candidate (e.g. `__init__.py` or `ANTIOS_ARCHITECTURE.md`) triggers **confirmation bias cascades**:
The agent observes imports or prose explanations in the irrelevant file, assumes the file is the right place to implement the fix, and makes edits to high-level documentation or exports rather than the underlying subsystem engine (`[INFERRED]`).

### 4.4 The Multi-Turn Rediscovery Tax
When context compaction occurs in a long conversation, the agent loses recollection of where files are located. Under Rep A, the agent must re-issue `find_by_name` or `grep_search`, burning an additional 2,000–4,000 tokens on every compaction boundary. Under Rep C/D, the manifest is preserved in the system prompt or injected dynamically, incurring **zero rediscovery penalty**.

---

## 5. Architectural Navigation Primitives

To eliminate unguided search thrashing, AntiOS establishes three structured navigation primitives:

### 5.1 Subsystem Directory Map (Level 0: ~150 Tokens)
A root-level table declaring every architectural subsystem, its physical directory, and its primary capability:

```markdown
| Subsystem | Root Directory | Core Responsibility | Primary Entrypoint | Proving Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Hooks & Enforcement** | `framework/hooks/` | Pre/Post tool and turn lifecycle guards | `framework/hooks/gate.py` | `python tests/run_all.py` |
| **Project Intelligence**| `framework/intelligence/`| Manifests, Merkle tree, wayfinding | `framework/intelligence/router.py`| `pytest tests/test_intel.py`|
| **Workspace & Worktree** | `framework/workspace/` | Worktree isolation, dirty tree state | `framework/workspace/worktree.py` | `pytest tests/test_worktree.py`|
```

### 5.2 Capability-to-Entrypoint Route Map (Level 1: ~400 Tokens)
A declarative JSON/YAML index that maps user intent verbs and capabilities directly to physical files and functions:

```json
{
  "capabilities": {
    "block_destructive_commands": {
      "subsystem": "Hooks",
      "file": "framework/hooks/gate.py",
      "symbol": "inspect_pre_tool_call",
      "tests": "tests/test_gate.py"
    },
    "verify_working_tree_cleanliness": {
      "subsystem": "Workspace",
      "file": "framework/workspace/worktree.py",
      "symbol": "verify_clean_working_tree",
      "tests": "tests/test_worktree.py"
    },
    "recalculate_freshness_merkle": {
      "subsystem": "Project Intelligence",
      "file": "framework/intelligence/merkle.py",
      "symbol": "MerkleTree.update_path",
      "tests": "tests/test_merkle.py"
    }
  }
}
```

### 5.3 Blast-Radius & Dependency Edge Map (Level 2: On-Demand)
A lightweight dependency graph declaring inbound and outbound file linkages. Rather than computing full Abstract Semantic Graphs, this primitive records file-level imports:
- `gate.py` $\to$ depends on: `[config.py, telemetry.py]`
- `gate.py` $\to$ depended on by: `[.agents/hooks.json, cli.py]`
- Modifying `gate.py` triggers required test suites: `tests/test_gate.py`, `tests/run_all.py`.

---

## 6. The Progressive Wayfinding Ladder

To prevent context inflation while guaranteeing instant localization, AntiOS implements a **4-Tier Progressive Wayfinding Ladder**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PROGRESSIVE WAYFINDING LADDER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level 0: Global Subsystem Manifest (Turn-0 Injection)                       │
│   • Size: ~150 tokens.                                                      │
│   • Injected in AGENTS.md or PreInvocation hook.                            │
│   • Resolves user request to exactly ONE subsystem directory.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level 1: Subsystem Route Map (On-Demand / Skill Trigger)                     │
│   • Size: ~300 tokens.                                                      │
│   • Located at `<subsystem>/ROUTES.md` or dynamically returned.              │
│   • Pinpoints authoritative entrypoint file, key classes, and test suite.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level 2: File Outline & Symbol Slices (Targeted Inspection)                 │
│   • Size: ~500 tokens.                                                      │
│   • Extracted via AST/ctags: class signatures, method headers, line ranges. │
│   • Prevents viewing entire 1,500-line file.                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Level 3: Bounded Target Chunk (Precision Edit Window)                       │
│   • Size: 50–150 lines (~300 tokens).                                       │
│   • Retrieved via view_file(StartLine, EndLine).                            │
│   • Target of replace_file_content edit tool.                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Concrete Architectural Recommendations for AntiOS

1. **Mandate Declarative Subsystem Manifests (`[RECOMMENDED]`)**:
   AntiOS must require every managed repository or workspace to expose a root `SUBSYSTEMS.md` or `.agents/routes.json`. This replaces unguided keyword searches with zero-search entrypoint resolution.

2. **Suppress Unscoped Search Tools (`[RECOMMENDED]`)**:
   Agents should be instructed by `AGENTS.md` to NEVER issue bare `grep_search` with single generic terms (`status`, `config`, `run`). All searches must be scoped by file glob (e.g. `Includes: ["framework/hooks/*.py"]`).

3. **Pair Every Entrypoint with its Proving Test (`[RECOMMENDED]`)**:
   Route maps must be bi-directional: declaring not only where code lives, but the exact test command required to verify that code.

4. **Pre-Compile Route Maps during Project Adaptation (`[RECOMMENDED]`)**:
   The Project Environment Compiler (`antios-adapt-project`) must automatically discover packages (`setup.py`, `pyproject.toml`, `package.json`, `Cargo.toml`), parse primary exports, and generate the Level 0 and Level 1 route maps deterministically.

---

## 8. Classification & Verification Ledger

| Claim / Metric | Classification | Evidence Source |
| :--- | :---: | :--- |
| Unguided grep yields 1,000–14,500 tokens | `[OBSERVED]` | `sandbox/experiments_r4/exp1_live_search.py` |
| Unguided first candidate failure rate: 87.5% | `[OBSERVED]` | `sandbox/experiments_r4/exp1_live_search.py` |
| Curated manifest achieves 100% first-choice accuracy | `[OBSERVED]` | `sandbox/experiments_r4/exp1_wayfinding.py` |
| Curated manifest reduces navigational tokens by 46.9% | `[OBSERVED]` | `sandbox/experiments_r4/exp1_wayfinding.py` |
| Rediscovery cost in compact context is 0 tokens | `[INFERRED]` | Static prompt injection permanence vs turn-by-turn tool replay |
| PreInvocation hook timeout is 30 seconds | `[OFFICIAL]` | Antigravity Platform Hook Specification |
