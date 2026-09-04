# STUDYLAB REPOSITORY: READ-ONLY FORENSIC AUDIT REPORT
**Target Repository:** `c:\Users\Suraj\Documents\Antigravity\Anki-maths`  
**Audit Type:** Codebase Forensic Audit & Architectural Mapping (Read-Only)  
**Report Artifact:** `STUDYLAB_CURRENT_STATE_AUDIT.md`  
**Evidence Standard:** 100% Grounded in Executable Source Code, Test Suites, and Git Archaeology  
**Classification Labels:** `[OBSERVED]`, `[DOCUMENTED]`, `[INFERRED]`, `[UNVERIFIED]`

---

## 1. EXECUTIVE SUMMARY

StudyLab is an **adaptive procedural problem-solving engine hosted inside the Anki desktop runtime** (`[DOCUMENTED]` `CLAUDE.md:21`, `PROJECT.md:21-25`). It is **not** a traditional flashcard application. It is a modification and extension of upstream Anki (`ankitects/anki` baseline commit `5f3a102f` `[OBSERVED]` `.git/logs/HEAD:1`), specifically re-architected to support quantitative mathematics, deductive reasoning, physical 5D dimensional analysis, and computer algebra system (CAS) step validation.

The system coexists with upstream Anki under a strict **Two-System Architecture**:
- **System 1 (Declarative Spaced Repetition):** Inherited upstream Anki features (FSRS scheduling, `collection.anki21`, declarative `Basic`/`Cloze` cards, deck browser, media server, sync) operate without interference or runtime overhead (`[OBSERVED]` `rslib/src/notetype/render.rs:122-132`).
- **System 2 (Procedural Problem Solving):** An in-tree Rust crate (`rslib/procedural/`), a dedicated SQLite store (`<collection>.procedural`, 16 tables, 22 indexes, WAL mode), and an Open Canvas TypeScript/Svelte reviewer frontend (`ts/reviewer/procedural.ts`).

### Key Forensic Findings
1. **Dual Content Ingestion Architecture (`[OBSERVED]` `PROJECT.md:26-64`, `docs/APKG_CONTENT_CONTRACT.md:23-40`):**
   - **Path A (Canonical Source-First / PYQ):** Curated static questions (`StudyLab Source*`) adhere to the frozen 20-field specification. They bypass dynamic generators, deterministically reconcile into SQLite `practice_items`, mount static `ProblemInstance` models with seed 0, and maintain an immutable learner-state firewall.
   - **Path B (Procedural Blueprints):** Declarative problem blueprints (`StudyLab Procedural Anchor*`) contain `inline_contract` JSON payloads generating dynamic mathematical variants across 175 curriculum topics.
2. **Telemetry Stripping Firewall (`[OBSERVED]` `rslib/src/scheduler/answering/mod.rs:501-512`):** Rich multi-step and error telemetry is routed via `custom_data["studylab"]`, recorded atomically into `collection.procedural`, and stripped to $\le 100$ bytes before committing to Anki's `cards` table, satisfying AnkiWeb sync constraints.
3. **Recently Introduced Interface Disconnect (`[OBSERVED]` `qt/aqt/reviewer.py:1056` vs `qt/aqt/reviewer.py:784-799`):** In commit `0036520b1`, mistake classification buttons were relocated to the native Qt bottom bar with `onclick='pycmd("procedural_mistake_select:{val}");'`. However, `_handle_procedural_command` contains no branch for `procedural_mistake_select`, hitting `else: pass`. Python silently ignores native button clicks, forcing reliance on webview or keyboard shortcuts.
4. **Verification Density (`[OBSERVED]` `rslib/procedural/tests/`, `ts/reviewer/`):** 134 Rust unit tests, 71 Rust integration test suites, 18 TypeScript Vitest suites (150 tests), and 93 Python pytest tests provide strong automated regression detection.

---

## 2. REPOSITORY MAP

```text
Anki-maths (Root)
│
├── rslib/                                # Anki Core Rust Library & StudyLab In-Tree Crate
│   ├── Cargo.toml                        # Workspace member linking procedural crate
│   ├── src/
│   │   ├── collection/mod.rs             # [HOOK] Lazy ProceduralService open & source reconciliation
│   │   ├── notetype/render.rs            # [HOOK] StudyLab card rendering interception
│   │   ├── scheduler/answering/mod.rs    # [HOOK] Telemetry extraction & 100-byte stripping
│   │   └── import_export/.../import/     # [HOOK] Auto-reconciliation upon APKG import
│   └── procedural/                       # [STUDYLAB ENGINE CRATE]
│       ├── Cargo.toml
│       ├── src/
│       │   ├── anchor/                   # ProceduralCardAnchor & SourceQuestion parsers
│       │   ├── chemistry/                # Stoichiometry, equilibrium, reaction balance
│       │   ├── content/                  # PracticeItem, catalog, item definitions
│       │   ├── core/                     # Domain enums, Strong IDs (SkillId, SchemaId)
│       │   ├── diagnostics/              # Error classification taxonomy & mock engine
│       │   ├── exam/                     # Exam profiles & PYQ mapping
│       │   ├── physics/                  # Kinematics 1D, work/energy, physical sanity
│       │   ├── practice/                 # PracticeAttempt, PracticeRequest, sessions
│       │   ├── problems/                 # 15 native generators, 59 declarative math contracts
│       │   │   ├── generators/           # Handcrafted AST math generators
│       │   │   └── steps/                # CAS step validator & solution graph
│       │   ├── reasoning/                # CSP constraint solvers, syllogisms, seating
│       │   ├── remediation/              # 9-tier remediation priority queue & policy
│       │   ├── reviewer/                 # HTML templates & script tag XSS escaping
│       │   ├── scheduling/               # Unified practice engine, rating policy, speed quadrants
│       │   ├── service/                  # ProceduralService façade API
│       │   ├── skills/                   # Bayesian mastery (EMA α=0.20), prerequisite DAG
│       │   ├── storage/                  # SQLite schema DDL (16 tables, 22 indexes, v1-v5)
│       │   └── units/                    # 5D dimensional analysis & 40+ unit registry
│       └── tests/                        # 71 Rust integration test suites
│
├── qt/                                   # PyQt6 Desktop GUI Shell
│   ├── aqt/
│   │   ├── __init__.py                   # App entrypoint & "Anki StudyLab" window branding
│   │   ├── main.py                       # Main window layout & titlebar updater
│   │   ├── profiles.py                   # Isolated profile dir ("AnkiStudyLab" on Windows)
│   │   ├── reviewer.py                   # [HOOK] Ease suppression, bridge routing, mistake strip
│   │   └── webview.py                    # QWebChannel script injection & bridge registration
│   ├── installer/                        # Briefcase desktop installer templates
│   └── tests/                            # Headless PyQt integration tests
│
├── ts/                                   # TypeScript / Svelte Web Reviewer Frontend
│   ├── package.json                      # Svelte 5, Vite 6, Vitest 3, TypeScript 5
│   └── reviewer/
│       ├── index.ts                      # Mounts globalThis.anki.procedural = proceduralAPI
│       ├── procedural.ts                 # 1,483-line 11-state ProceduralReviewer FSM
│       ├── reviewer.scss                 # Open Canvas 720px layout tokens & design rules
│       ├── answering.ts                  # mutateNextCardStates customData pack/unpack bridge
│       └── components/
│           ├── mcq_container.ts          # Radio option container (zero textboxes)
│           ├── numerical_container.ts    # Float input with live 5D unit preview pill
│           ├── stepwise_container.ts     # Multi-step CAS reasoning workspace
│           └── mistake_footer.ts         # Metacognitive reflection button strip
│
├── pylib/                                # Upstream Anki Python library (100% UNTOUCHED)
├── proto/                                # Protobuf RPC definitions (100% UNTOUCHED)
├── tools/                                # Build, content generation, and QA tools
│   ├── studylab_content_factory.py       # Universal 175-topic content factory
│   └── ninja                             # Multi-language build runner
│
├── artifacts_qa/                         # Automated QA runners, validators & test APKGs
│   ├── canonical_source_test_fixture.apkg# Golden APKG fixture
│   ├── live_visual_audit_runner.py       # CDP + Win32 GDI visual audit runner
│   ├── validate_canonical_apkg.py        # 175-topic universe APKG validator
│   └── validate_canonical_source_apkg.py # Canonical source contract validator
│
├── dist/apkgs/                           # Built APKG packages (studylab-demo-v1.0.apkg)
├── docs/                                 # 66 canonical specification documents
│   ├── APKG_CONTENT_CONTRACT.md          # Frozen Source APKG contract specification
│   ├── ARCHITECTURE_INVARIANTS.md        # System invariants and safety rules
│   ├── DOCUMENTATION_MAP.md              # Master sitemap & reading paths
│   ├── DOCUMENTATION_TRUTH_MATRIX.md     # Source-of-truth reconciliation matrix
│   ├── LEARNING_MODEL.md                 # Mastery tracking & cognitive architecture
│   └── SYSTEM_ARCHITECTURE.md            # Multi-layer architectural specifications
│
├── justfile                              # Command recipes (just build, check, test, run)
├── CLAUDE.md                             # Developer guidelines & quick iteration recipes
├── PROJECT.md                            # High-level architecture & feature inventory
└── AGENTS.md                             # Agent entrypoint pointer to CLAUDE.md
```

### Area Categorization Summary

```text
CORE APPLICATION:        qt/aqt/main.py, qt/aqt/__init__.py, pylib/anki/, proto/anki/
MATHS FEATURES:          rslib/procedural/src/problems/, units/, physics/, chemistry/, reasoning/
ANKI INTEGRATION:        rslib/src/notetype/render.rs, rslib/src/scheduler/answering/mod.rs,
                         rslib/src/collection/mod.rs, rslib/src/import_export/.../import/mod.rs,
                         qt/aqt/reviewer.py
UI / REVIEWER:           ts/reviewer/procedural.ts, ts/reviewer/components/, ts/reviewer/reviewer.scss
APKG / DATA:             rslib/procedural/src/storage/, rslib/procedural/src/anchor/,
                         generate_canonical_source_apkg.py, generate_procedural_apkg.py
TESTING:                 rslib/procedural/tests/, ts/reviewer/*.test.ts, qt/tests/, artifacts_qa/
BUILD / PACKAGING:       justfile, tools/ninja, Cargo.toml, pyproject.toml, package.json
DOCUMENTATION:           docs/ (66 specs), CLAUDE.md, PROJECT.md, README.md
DEVELOPMENT TOOLING:     run.bat, run_debug.bat, .ruff.toml, .mypy.ini, .eslintrc.cjs
```

---

## 3. ACTUAL ARCHITECTURE

### 3.1 Component Graph & Structural Dependencies

```text
                                [ Content Authoring / Packaging ]
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        [ Canonical Source APKG ]                         [ Procedural Blueprint APKG ]
         (StudyLab Source Question)                        (StudyLab Procedural Anchor)
                       │                                                 │
                       └────────────────────────┬────────────────────────┘
                                                ▼
                                    [ Anki Import Subsystem ]
                     (rslib/src/import_export/package/apkg/import/mod.rs:69)
                                                │
                                                ▼
                              [ col.reconcile_source_questions() ]
                                 (rslib/src/collection/mod.rs:190)
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        [ collection.anki21 SQLite ]                      [ <col>.procedural SQLite ]
          (Standard Notes / Cards)                        (16 Tables: practice_items,
                                                           attempts, skills, error_events)
                                                │
                                                ▼
                                    [ Card Render Interceptor ]
                                  (rslib/src/notetype/render.rs)
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       │                                                 │
        (nt.name == "StudyLab Source*")              (nt.name == "StudyLab Procedural Anchor*")
                       │                                                 │
                       ▼                                                 ▼
            render_source_anchor()                           render_procedural_anchor()
          (Mounts static ProblemInstance                   (Samples dynamic variant from
           seed 0, zero generation)                         AST or Declarative Blueprint)
                       │                                                 │
                       └────────────────────────┬────────────────────────┘
                                                ▼
                                  [ Reviewer HTML Generation ]
                           (rslib/procedural/src/reviewer/template.rs)
                                                │
                                                ▼
                                [ QtWebEngine Webview Container ]
                                (qt/aqt/reviewer.py & webview.py)
                                                │
                                                ▼
                               [ TypeScript Procedural Reviewer ]
                                  (ts/reviewer/procedural.ts)
                                  11-State Finite State Machine
                                                │
                       ┌────────────────────────┼────────────────────────┐
                       ▼                        ▼                        ▼
               [ MCQContainer ]       [ NumericalContainer ]    [ StepwiseContainer ]
               (Zero Textboxes)       (5D Physical Units AST)   (Multi-Step CAS Graph)
                                                │
                                                ▼
                                  [ Local Answer Evaluation ]
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       │                                                 │
                  [ Correct ]                                      [ Incorrect ]
                       │                                                 │
                       ▼                                                 ▼
             State: "feedback"                             State: "mistake_classification"
             - Speed quadrant pill                         - Space / Enter trapped
             - Shows comparison                            - Forces 4-category reflection:
             - Prepares rating (3..4)                        [1 Silly] [2 Pattern]
                       │                                     [3 Concept] [4 Prereq]
                       │                                                 │
                       │                                                 ▼
                       │                                     Reveals step-by-step solution
                       │                                     Prepares rating (1..2)
                       │                                                 │
                       └────────────────────────┬────────────────────────┘
                                                ▼
                               [ State Mutation & Telemetry Pack ]
                                  (ts/reviewer/answering.ts)
                          customData[state].studylab = full_telemetry
                                                │
                                                ▼
                                    [ Host Bridge Execution ]
                              bridgeCommand("procedural_answer:1..4")
                                                │
                                                ▼
                                  [ Python Reviewer Command ]
                                  (qt/aqt/reviewer.py:761-769)
                            _procedural_answer_authorized = True
                            self._answerCard(val)
                                                │
                                                ▼
                                   [ Rust Answering Hook ]
                           (rslib/src/scheduler/answering/mod.rs:350)
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
         [ Persist to collection.procedural ]             [ Strip Telemetry & Update Anki ]
         - Inserts PracticeAttempt                        - parsed.remove("studylab")
         - Inserts ErrorEvent                             - custom_data becomes "" or <= 100B
         - Updates Bayesian SkillState                    - card.validate_custom_data() PASS
         - Enqueues RemediationAction                     - Committed to collection.anki21
```

### 3.2 Architectural Seams & Coupling

1. **Notetype Name String Coupling (`[OBSERVED]` `rslib/src/notetype/render.rs:123, 128`):** Upstream Anki detects StudyLab cards via string prefix matching:
   - `nt.name.as_str().starts_with("StudyLab Procedural Anchor")`
   - `nt.name.as_str().starts_with("StudyLab Source")`
   If notetypes are renamed in APKG packages without updating `render.rs`, interception fails silently and cards fall back to standard Anki Mustache evaluation.
2. **Ephemeral Custom Data Carrier (`[OBSERVED]` `rslib/src/scheduler/answering/mod.rs:350-512`):** Anki's protobuf RPC provides no custom telemetry channel for card review. StudyLab uses `card.custom_data` as a transient in-memory transport from TypeScript to Rust, stripping it before SQLite writes.
3. **Double SQLite Storage Boundary (`[OBSERVED]` `rslib/src/collection/mod.rs:176`):**
   - Core Anki: `<col_path>.anki2` or `collection.anki21`.
   - StudyLab: `<col_path>.procedural`.
   Physical file separation ensures that corruptions, schema migrations, or heavy analytical writes in StudyLab cannot corrupt Anki's flashcard store.

---

## 4. ANKI ↔ STUDYLAB BOUNDARY

### 4.1 Boundary Classification Matrix

| Boundary Layer | Upstream Anki Responsibility | StudyLab Specific Responsibility | Tightness & Health of Seam |
|---|---|---|---|
| **Notetype Rendering** | `rslib/src/notetype/render.rs` parses Mustache templates, cloze deletions, and field substitutions. | Intercepts procedural notetypes before template parsing, resolving session targets and emitting Open Canvas HTML. | **Clean Seam**. Standard cards (`Basic`, `Cloze`) bypass with zero overhead (`line 132`). |
| **Card Answering** | `rslib/src/scheduler/answering/mod.rs` applies FSRS/V3 state transitions, interval calculations, and leech counters. | Extracts `custom_data["studylab"]`, writes attempt records to `collection.procedural`, enqueues remediation, and strips telemetry. | **Clean Seam**. Telemetry stripped before `validate_custom_data()` (`line 511`). |
| **Database Storage** | SQLite `collection.anki21` (tables: `notes`, `cards`, `revlog`, `col`). | SQLite `collection.procedural` (16 tables: `practice_items`, `practice_attempts`, `skills`, `skill_states`, etc.). | **Clean Seam**. Distinct database handles managed via `ProceduralService`. |
| **Desktop Reviewer GUI** | `qt/aqt/reviewer.py` renders bottom bar (`#ansbut`), tracks shortcuts (Space, Enter, 1..4), and switches question/answer. | Suppresses `#ansbut`, traps Space/Enter in mistake reflection, injects mistake buttons, and handles `procedural_*` commands. | **Tightly Coupled Seam**. Logic is spliced directly into `reviewer.py` (see critical disconnect below). |
| **Webview Frontend** | Svelte/TypeScript review chrome (`ts/reviewer/index.ts`, `reviewer_extras.ts`). | `ts/reviewer/procedural.ts` 11-state state machine, input modality containers, MathJax typesetting. | **Clean Seam**. Injected as `globalThis.anki.procedural`. Teardown handled by `destroyActive()`. |

### 4.2 Forensic Vulnerability Analysis: Native Bottom Bar Disconnect

> [!WARNING]
> **[OBSERVED in `qt/aqt/reviewer.py:1056` vs `qt/aqt/reviewer.py:784-799`]:**
> Commit `0036520b1` moved mistake classification buttons to the native Qt bottom bar:
> ```python
> # qt/aqt/reviewer.py:1056
> buf += f'<button class="proc-mistake-btn {btn_class}" onclick=\'pycmd("procedural_mistake_select:{val}");\'>...</button>'
> ```
> However, `_handle_procedural_command` (`qt/aqt/reviewer.py:758-801`) parses:
> ```python
> if cmd == "procedural_hint": ...
> elif cmd == "procedural_attempt": ...
> elif cmd == "procedural_validate_steps": ...
> elif cmd == "procedural_mistake": ...
> elif cmd == "procedural_try_similar": ...
> elif cmd == "procedural_practice_prerequisite": ...
> elif cmd == "procedural_declarative_recall": ...
> else: pass
> ```
> It checks `cmd == "procedural_mistake"`, but **not** `"procedural_mistake_select"`. Clicking the native bottom button triggers `pycmd("procedural_mistake_select:1")`, which falls through to `else: pass` and is silently ignored. The user cannot advance via mouse click on the native button; advancement requires keyboard hotkeys (1..4) or in-webview controls.

---

## 5. MATHS / PROCEDURAL SYSTEM

### 5.1 Generator & Mathematics Coverage

1. **15 Handcrafted AST Problem Generators (`rslib/procedural/src/problems/generators/` `[OBSERVED]`):**
   - `percentage_successive.rs`: Forward 2-step, reverse initial, net equivalent change ($a + b + \frac{ab}{100}$).
   - `linear_equations.rs`: Single-variable equations $Ax + B = C$, fractions, transpositions.
   - `profit_loss.rs`: CP, SP, profit/loss %, successive discounts, marked price.
   - `ratio.rs`: Direct/inverse proportion, compound ratios, partitioning.
   - `average.rs`: Arithmetic mean, weighted averages, replacement problems.
   - `divisibility.rs`: Divisibility rules ($2$ through $13$), prime factors.
   - `remainders_modular.rs`: Modular congruences, cyclicity of unit digits.
   - `time_work.rs`: Unitary work rates, pipes & cisterns, efficiency ratios.
   - `time_speed_distance.rs`: Relative speed (meeting/chasing), circular tracks, average speed.
   - `mixtures_alligation.rs`: Alligation cross-rule, replacement dilution.
   - `linear_inequalities.rs`: $Ax + B \le C$, sign flip on negative multiplication.
   - `algebraic_identities.rs`: $(a \pm b)^2, a^2 - b^2, (a \pm b)^3, a^3 \pm b^3$.
   - `geometry_triangles.rs`: Pythagoras, Heron's formula, inradius/circumradius.
   - `combined_multi_concept.rs`: Chained concepts (Ratio + Profit/Loss).
2. **59 Declarative Math Topic Contracts (`rslib/procedural/tests/phase36c_all_175_topics_factory_tests.rs:96-199` `[OBSERVED]`):**
   Spans 6 modules: Number System, Commercial Arithmetic, Rates/Time, Algebra, Geometry/Mensuration, Trigonometry/Statistics.
3. **Computer Algebra & Step Validation (`rslib/procedural/src/problems/steps/step_validator.rs:478-650` `[OBSERVED]`):**
   - Strips TeX formatting, currency symbols, and spaces (`normalize_expr`).
   - Algebraic linear solver (`parse_linear_one_var`): recognizes $2x + 6 = 12 \iff 2x = 6 \iff x = 3$.
   - Commutative addition verification: $2x + 6 \equiv 6 + 2x$.
   - Multiplier / percentage equivalence: $1.20 \equiv 120\% \equiv +20\%$.
   - Downstream error consistency (`StepValidationStatus::PartiallyValid`): if a student errs in Step 1, but executes Step 2 correctly based on their erroneous intermediate value, Step 2 is credited.
4. **5D Physical Vector & Unit Engine (`rslib/procedural/src/units/` `[OBSERVED]`):**
   $[M]^m [L]^l [T]^t [N]^n [K]^k$ dimensional vector with 40+ unit definitions and cross-unit scaling.

---

### 5.2 End-to-End Maths Interaction Trace

```text
[1. USER ACTION]
User reviews Quantitative card "Successive Percentage Changes" ($200 increased 25% then decreased 20%).
User enters "210" in #proc-answer-input (committing additive fallacy 25 - 20 = +5% -> $210) and presses Enter.
  ↳ ts/reviewer/procedural.ts:400-406: Keydown listener captures Enter, invokes this.handleQuickSubmit().

[2. UI & LOCAL EVALUATION]
  ↳ ts/reviewer/procedural.ts:924-931: State set to "submitting"; calls evaluateLocally("210").
  ↳ ts/reviewer/procedural.ts:859-868: Compares |210 - 200| = 10 > 0.01 tolerance -> isCorrect = false.
  ↳ ts/reviewer/procedural.ts:968-1001: Computes elapsed time (14.2s), classifies speed quadrant ("concept_setup").
  ↳ ts/reviewer/procedural.ts:993: Calls bridgeCommand("procedural_attempt:{...}").

[3. WEBVIEW ↔ PYTHON BRIDGE]
  ↳ qt/aqt/webview.py:96-108: QWebChannel transports payload over WebSocket IPC to Python.
  ↳ qt/aqt/reviewer.py:723, 750-751: Reviewer._linkHandler receives command, routes to _on_procedural_attempt().
  ↳ qt/aqt/reviewer.py:811-817: Stores _last_procedural_attempt; transitions self.state = "answer"; calls _showEaseButtons().
  ↳ qt/aqt/reviewer.py:1032-1059: Since is_correct == False, renders _mistakeButtons in bottom toolbar.

[4. METACOGNITIVE REFLECTION & KEY TRAP]
  ↳ ts/reviewer/procedural.ts:1008-1050: UI transitions to state = "mistake_classification".
  ↳ ts/reviewer/procedural.ts:516-521: Space and Enter keys trapped to prevent skipping reflection.
  ↳ User presses key "3" (Concept Gap) in webview.
  ↳ ts/reviewer/procedural.ts:1052-1067: Calls selectMistakeCategory("formula_or_concept_misapplied").
  ↳ Dispatches bridgeCommand("procedural_mistake:...").
  ↳ ts/reviewer/procedural.ts:1075-1250: Transitions to state = "feedback"; reveals step-by-step solution (#proc-solution-container).
  ↳ ts/reviewer/procedural.ts:1257-1268: Calls globalThis.anki.mutateNextCardStates to inject studylab telemetry into card states.
  ↳ ts/reviewer/procedural.ts:1350-1373: deriveCalibratedEase() derives ease = 1 (Again) due to misconception.
  ↳ ts/reviewer/procedural.ts:1375-1380: handleNext() transitions to state = "next", dispatches bridgeCommand("procedural_answer:1").

[5. ANKI SCHEDULER & DATABASE COMMIT]
  ↳ qt/aqt/reviewer.py:761-769: Receives "procedural_answer:1", sets _procedural_answer_authorized = True, calls _answerCard(1).
  ↳ qt/aqt/reviewer.py:565-590: _answerCard() invokes Rust answering pipeline with rating = Again.
  ↳ rslib/src/scheduler/answering/mod.rs:349-442: answer_card() detects "studylab" in custom_data.
  ↳ rslib/procedural/src/storage/store.rs:873-1067: record_practice_attempt_atomic() executes single SQLite transaction in collection.procedural:
      - Reads previous SkillState for "percentage.successive".
      - Updates Bayesian mastery (EMA α=0.20 drops mastery from 0.65 to 0.42).
      - Inserts record into practice_attempts table.
      - Inserts record into error_events table (category: "concept").
      - Upserts updated SkillState.
  ↳ rslib/src/scheduler/answering/mod.rs:445-498: Evaluates RemediationPolicy; enqueues ConceptCheckObject into remediation_queue_items.
  ↳ rslib/src/scheduler/answering/mod.rs:501-512: Strips "studylab" from custom_data (reducing it to 0 bytes); card.validate_custom_data() passes <= 100 bytes check; standard card updated in collection.anki21.

[6. TEARDOWN & NEXT CARD]
  ↳ qt/aqt/reviewer.py:416: Reviewer evaluates globalThis.anki.procedural.destroyActive().
  ↳ ts/reviewer/procedural.ts:1390-1428: Observers disconnected, timers cleared, DOM listener removed.
  ↳ Next card rendered with zero residual state leakage.
```

---

## 6. SOURCE → APKG CONTRACT AUDIT

### 6.1 Requirements Enforcement Classification

| Contract Requirement | Classification | Concrete Evidence File & Line References | Implementation & Enforcement Behavior |
|---|---|---|---|
| **Notetype Name Interception** | **ENFORCED** | [OBSERVED] `rslib/src/notetype/render.rs:128-131`<br>[OBSERVED] `qt/aqt/reviewer.py:696-702`<br>[OBSERVED] `rslib/src/collection/mod.rs:191` | Notes starting with `"StudyLab Source"` route to `render_source_anchor()`, suppress ease buttons, and trigger reconciliation. |
| **Mandatory Prompt Field** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:182-187`<br>[OBSERVED] `artifacts_qa/validate_canonical_source_apkg.py:54-55` | Emits `SourceContractError::MissingRequiredField("Prompt")` if missing or whitespace-only. |
| **Mandatory QuestionType** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:30-40, 189-196` | Must parse explicitly to `"mcq"` or `"numerical"`. Unrecognized strings emit `SourceContractError::InvalidQuestionType`. Never inferred. |
| **Mandatory CorrectAnswer** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:197-202` | Missing field emits `SourceContractError::MissingRequiredField("CorrectAnswer")`. |
| **MCQ Options ($\ge 2$ choices)** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:206-256`<br>[OBSERVED] `rslib/procedural/tests/canonical_source_contract_tests.rs:48-66` | Rejects missing options or $<2$ non-empty entries with `SourceContractError::MissingMcqOptions`. Supports JSON array and newline formatting. |
| **MCQ CorrectAnswer Match** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:366-399` | Validates answer matches options by exact text, 1-based index (`"1"`), letter index (`"A"`), or prefix (`"A) text"`). Mismatches emit `SourceContractError::InvalidCorrectAnswer`. |
| **Numerical Finite Float** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:258-271` | Numerical answer must parse to a finite float (`f64::is_finite()`). `NaN`, `inf`, and text strings emit `SourceContractError::InvalidCorrectAnswer`. |
| **Difficulty Range [1.0, 5.0]** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:273-294` | Rejects values $<1.0$, $>5.0$, non-finite floats, or unparseable strings with `SourceContractError::InvalidDifficulty`. |
| **Provenance Year Parsing** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:321-335` | Validates `Year` parses as integer. Renders formatted badge (`PYQ: RRB ALP 2024 · Shift 1`). |
| **Identity Separation Invariant** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/anchor/source.rs:401-403, 461-465, 489-501` | Anki Note GUID (`guid`), StudyLab Runtime Item ID (`pi_src_<guid>`), and Authored `SourceQuestionID` remain strictly separated. |
| **Automatic Ingestion Reconciliation** | **ENFORCED** | [OBSERVED] `rslib/src/import_export/package/apkg/import/mod.rs:69`<br>[OBSERVED] `rslib/procedural/src/service/mod.rs:165-209` | Importing an `.apkg` computes 64-bit content hashes and reconciles items in `collection.procedural.practice_items` (`New`, `Updated`, `Unchanged`, `Archived`). |
| **JIT Review Reconciliation Fallback** | **ENFORCED** | [OBSERVED] `rslib/src/notetype/render.rs:285-300` | If a source note is reviewed before import reconciliation has executed, it is parsed and reconciled into SQLite on-the-fly. |
| **Learner-State Firewall** | **ENFORCED** | [OBSERVED] `rslib/tests/canonical_source_apkg_runtime_e2e_tests.rs:243-313` | Authored question fields in `practice_items` are immutable. Learner attempts write exclusively to `practice_attempts` and `skill_states`. |
| **Modality Purity (Zero Textboxes)** | **ENFORCED** | [OBSERVED] `rslib/procedural/src/reviewer/template.rs:153-184, 425-432`<br>[OBSERVED] `ts/reviewer/components/mcq_container.ts:60` | MCQ renders radio cards with zero `#proc-answer-input`. Numerical renders single input box with zero `.proc-option-group`. |
| **Media Asset Extraction** | **ENFORCED** | [OBSERVED] `generate_canonical_source_apkg.py:389-396`<br>[OBSERVED] `rslib/tests/canonical_source_apkg_runtime_e2e_tests.rs:171-199` | Media references (`<img src="...">`) extract to the profile media folder and resolve in reviewer HTML. |
| **Graceful Reviewer Error Display** | **ENFORCED** | [OBSERVED] `rslib/src/notetype/render.rs:259-274` | Malformed source notes render `<div class='proc-error'>Source Engine Error</div>` rather than crashing the desktop process. |
| **Procedural Blueprint Schemas** | **ENFORCED** | [OBSERVED] `tools/studylab_content_factory.py`<br>[OBSERVED] `artifacts_qa/validate_canonical_apkg.py:56-88` | Validates `inline_contract` across 175 topics with parameters, archetypes, and solution graphs. |
| **Physical File `StudyLab-Source-APKG-Contract(1).txt`** | **DOCUMENTED ONLY** | [DOCUMENTED] `PROJECT.md:7`<br>[DOCUMENTED] `docs/APKG_CONTENT_CONTRACT.md:5` | Cited as Level 1 Frozen Source of Truth, but exists as codified documentation (`docs/APKG_CONTENT_CONTRACT.md`) rather than a standalone `.txt` file. |

---

## 7. TESTING & VERIFICATION

### 7.1 Test Inventory Matrix

| Test Suite / Harness | Framework / Engine | Files & Locations | Volume / Execution Time | Determinism & Fixtures |
|---|---|---|---|---|
| **Rust Procedural Unit Tests** | `cargo test --lib` | `rslib/procedural/src/` | 134 unit tests (~0.09s) | **Deterministic**. Tests unit algebra, CAS, XSS escaping, mastery formulas. |
| **Rust Procedural Integration Tests** | `cargo test --tests` | `rslib/procedural/tests/` | 71 test files, 74+ test targets (~15s) | **Deterministic**. Uses fixed seeds. Includes 175-topic factory test (`phase36c_...tests.rs`). |
| **Rust APKG E2E Runtime Tests** | `cargo test` | `rslib/tests/canonical_source_apkg_runtime_e2e_tests.rs` | 8 multi-stage scenarios (~2.5s) | **Deterministic**. Uses `artifacts_qa/canonical_source_test_fixture.apkg`. |
| **TypeScript Vitest Suites** | `vitest` | `ts/reviewer/`, `ts/lib/`, `ts/routes/` | 18 test files, 150 tests (~8.0s) | **Deterministic**. Vitest fake timers and JSDOM DOM mocking. |
| **Python Pytest Suites** | `pytest` | `qt/tests/`, `pylib/tests/` | 93 tests (57 qt, 36 pylib) (~12.0s) | **Deterministic**. Uses temporary headless SQLite collections. |
| **Playwright Browser E2E Tests** | `playwright` | `ts/tests/e2e/` | 10 spec files (`procedural-runtime.spec.ts`) | **Deterministic**. Drives headless Chromium against Anki mediasrv. |
| **Live Desktop Webview QA** | CDP + Win32 GDI | `artifacts_qa/live_visual_audit_runner.py` | 8–14 live UI states | **Deterministic** against live running Windows GUI. Captures dual screenshots with SHA-256 digests. |
| **APKG Contract QA Validators** | Python CLI | `artifacts_qa/validate_canonical_source_apkg.py`<br>`artifacts_qa/validate_canonical_apkg.py` | 2 validator scripts | **Deterministic**. Direct SQLite inspections of `.apkg` packages. |
| **Adversarial Challenger Suites** | Python CLI | `artifacts_qa/challenger_test_dim1..4.py`<br>`artifacts_qa/challenger_2_master_runner.py` | 4 challenger dimensions | **Deterministic**. Tests CAS edge cases, DB crashes, and cold imports. |

### 7.2 Coverage & Verification Gap Analysis

#### Verified Behaviors
- Source note schema extraction, contract error taxonomy (`SourceContractError`), and SQLite reconciliation.
- Procedural math generation across 15 native families and 59 declarative math topic contracts.
- 5D dimensional vector arithmetic ($[M][L][T][N][K]$) and unit conversions across 40+ units.
- CAS equation step evaluation, commutative addition, and downstream error credit.
- SQLite single-transaction atomicity and migrations (v1-v5) in `<collection>.procedural`.
- Reviewer 11-state state machine, Space/Enter keyboard trap during mistake reflection.
- 100-byte `custom_data` stripping prior to `collection.anki21` commit.
- Isolation of standard cards (`Basic`, `Cloze`) from procedural CSS and events.

#### Unverified Behaviors / Testing Gaps
1. **Mobile Runtime Support:** AnkiDroid (Java) and AnkiMobile (Swift/iOS) are **untested**. StudyLab is currently verified exclusively on desktop (Rust + PyQt6 + QtWebEngine).
2. **Multi-Device Cloud Sync for `collection.procedural`:** AnkiWeb synchronizes `collection.anki21`. Rich attempt histories in `collection.procedural` remain local to the desktop client. Cloud synchronization for the procedural SQLite store is unverified.
3. **Non-Chromium Webview Engines:** UI testing is executed against QtWebEngine (Chromium) and Playwright Chromium. Safari/WebKit rendering is unverified.
4. **Native Mistake Button Command Execution:** The recent change in commit `0036520b1` introducing `pycmd("procedural_mistake_select:{val}")` is **not covered by automated tests**, allowing the unhandled command disconnect to escape detection.

---

## 8. DOCUMENTATION AUDIT

### 8.1 Documentation SOT Hierarchy & Classification

`docs/DOCUMENTATION_MAP.md:108-128` establishes an explicit **8-Tier Source-of-Truth Hierarchy**:
- **Tier 1:** Current Executable Source Code (Supreme Ground Truth)
- **Tier 2:** Current Passing Test Suites (Behavioral Ground Truth)
- **Tier 3:** Current Schemas / Migrations (Structural Ground Truth)
- **Tier 4:** Current Verified Artifacts (Empirical Ground Truth)
- **Tier 5:** Explicit Product Requirements (Intent Ground Truth)
- **Tier 6:** Canonical Suite Documentation (`docs/`)
- **Tier 7:** Historical Phase Reports (`01_` through `08_`)
- **Tier 8:** General / Unverified Assumptions (Subordinate)

### 8.2 Inventory of Master Specifications (The 10 Frozen Contracts)

1. `STUDYLAB_PRODUCT_CONTRACT.md`: Product North Star, Two-System Architecture, ACT-R model.
2. `FRONTEND_PRODUCT_SPEC.md`: 9 learning object modalities, Cognitive Tutor inner loop.
3. `FRONTEND_UI_STATE_SPEC.md`: 14 frontend states, transitions, keyboard isolation.
4. `FRONTEND_BUTTON_CONTRACT.md`: Canonical master button matrix across 23 controls.
5. `FRONTEND_VISUAL_DESIGN_SPEC.md`: "Problem is Visual Hero", design tokens (`--proc-*`).
6. `APKG_CONTENT_CONTRACT.md`: Canonical Source APKG specification & declarative blueprints.
7. `APKG_FRONTEND_CONTRACT.md`: 4-tier cross-layer mapping (APKG -> Rust -> SQLite -> Qt -> TS).
8. `DATABASE_DATA_CONTRACT.md`: Dedicated `collection.procedural` store, 16 tables, 22 indexes.
9. `FRONTEND_ACCEPTANCE_MATRIX.md`: 12-screen testable acceptance criteria, WCAG 2.1 AA.
10. `FRONTEND_CURRENT_STATE_GAP_MAP.md`: Screenshot-grounded forensic gap audit.

### 8.3 Documentation Discrepancies & Stale Information

1. **`StudyLab-Source-APKG-Contract(1).txt` Reference:** Cited in `PROJECT.md:7` and `docs/APKG_CONTENT_CONTRACT.md:5` as the Level 1 Frozen Source of Truth, but no physical `.txt` file exists in the repository. Its contents are fully codified in `docs/APKG_CONTENT_CONTRACT.md`.
2. **Root-Level Historical Artifacts:** `HANDOFF_REPORT.md` in the repository root documents resolved intermediate defects (missing Next button, Spacebar desync) from early investigation phases. Without an explicit historical header, fresh AI agents can misinterpret these as open bugs.
3. **Upstream Anki Documentation Stubs:** Several documents in `docs/` (`api-python.md`, `api-rust.md`, `editing.md`) are 2-line stubs inherited from upstream Anki.
4. **Ad-Hoc Root Scripts:** Scripts such as `qa_advance.py`, `qa_driver.py`, `qa_forensic.py`, and `longitudinal_simulator.py` reside at root without documentation explaining their operational status relative to the formal `artifacts_qa/` harness.

---

## 9. GIT / DEVELOPMENT WORKFLOW

### 9.1 Git Archaeology & Remote Architecture

- **Active Branch:** `main` (`[OBSERVED]` `.git/HEAD`).
- **Tracking Branch:** `upstream-user/main` (`[OBSERVED]` `.git/config`).
- **Remotes:**
  - `origin`: `https://github.com/ankitects/anki.git` (Upstream Anki)
  - `upstream-user`: `https://github.com/naksh-07/anki-maths.git` (StudyLab Fork)
- **Commit History:** 47 commits ahead of upstream base `5f3a102f` (`[OBSERVED]` `.git/logs/HEAD`).
- **Working Tree Cleanliness:** Clean working tree. Untracked ephemeral artifacts are ignored via `.gitignore` (`*.log`, `*.pid`, `desktop_ownership.json`, `desktop_app.log`).

### 9.2 Development Tooling & Workflow Conventions

- **Orchestration Tool:** `just` (`justfile` `[OBSERVED]`). Invoking `./ninja`, `./run`, or `tools/` directly is prohibited (`CLAUDE.md:3-6`).
- **Language Standards:**
  - **Rust:** Edition 2021, MSRV 1.80 (`Cargo.toml:4-6`). Formatting via `.rustfmt.toml`.
  - **Python:** Managed via `uv` (`pyproject.toml`), Python $\ge 3.12$, typed via `mypy` (`.mypy.ini`), linted via `ruff` (`.ruff.toml`).
  - **Web:** Managed via `yarn` (`package.json`), Svelte 5, TypeScript 5, Vite 6, Vitest 3. Formatting via `.dprint.json` and Prettier.
- **Master Verification Gate:** `just check` executes Ninja to compile pylib, qt, and run static checks across all languages.

---

## 10. AI-AGENT READINESS

### 10.1 Readiness Assessment Across 7 Dimensions

| Dimension | Rating (1-10) | Forensic Assessment |
|---|---|---|
| **Discoverability** | **8.5** | High. `AGENTS.md` points to `CLAUDE.md`. `CLAUDE.md` documents invariants and iteration commands. `docs/DOCUMENTATION_MAP.md` provides explicit reader paths. *Minor flaw:* Root is cluttered with ~20 ad-hoc `qa_*.py` and `01_..08_*.md` files. |
| **Context & Mental Model** | **9.5** | Exceptional. The Two-System Architecture (Anki System 1 vs StudyLab System 2) and the two content paths (Source vs Procedural) are clearly articulated. |
| **Boundaries & Invariants** | **9.5** | Strict boundaries. Physical SQLite database separation, 100-byte custom_data stripping, modality purity (zero textboxes on discrete problems), and teardown hooks are explicit in code. |
| **Contracts** | **9.0** | Strongly typed Rust structs with rich serde annotations (`SourceQuestion`, `ProceduralCardAnchor`, `DeclarativeFamilyContract`). Comprehensive error enums (`SourceContractError`). |
| **Verification Loops** | **9.5** | Fast, deterministic feedback loops. Sub-second unit tests (`cargo test -p procedural --lib` in 0.09s), Vitest in 8.0s, and golden fixtures for APKG validation. |
| **Recovery & Failure Handling**| **9.0** | Robust error handling. Invalid source notes render clean HTML error boxes instead of crashing. Malformed procedural anchors fall back gracefully. SQLite uses single-transaction ACID rollbacks. |
| **Cognitive Complexity** | **7.5** | High polyglot complexity (Rust, Python, TypeScript, SQLite, Qt). An agent modifying a feature must understand cross-layer data flows across 4 languages. |

---

## 11. RISK MAP

### HIGH RISK (Could break major behavior across subsystems)
1. **`rslib/src/scheduler/answering/mod.rs:501-512` (Custom Data Telemetry Stripping):**
   *Why:* If the logic stripping `custom_data["studylab"]` fails or is bypassed, `card.validate_custom_data()` will fail or cards will write $>100$ bytes to `collection.anki21`. This will corrupt AnkiWeb synchronization and crash standard Anki clients.
2. **`rslib/src/notetype/render.rs:122-132` (Notetype Interception Hook):**
   *Why:* Relies on string prefix matching (`StudyLab Procedural Anchor*`, `StudyLab Source*`). Any desynchronization between APKG note model names and these prefixes causes cards to render as blank or raw Mustache templates.
3. **`qt/aqt/reviewer.py:696-850` (Reviewer Bridge & Ease Suppression):**
   *Why:* Directly splices into Anki's desktop review loop. Modifying key event handlers or link handlers can re-introduce Spacebar bypasses, break standard Anki ease rating, or leak UI event listeners into non-procedural cards.

### MEDIUM RISK (Requires targeted verification)
1. **`rslib/procedural/src/storage/migration.rs` (SQLite Database Migrations):**
   *Why:* Manages 5 schema versions across 16 tables. Changes to table definitions require migration testing to prevent breaking existing user practice histories.
2. **`ts/reviewer/procedural.ts` (11-State Finite State Machine):**
   *Why:* 1,483 lines of client-side state transitions. Modifying state transitions without running Vitest can cause modal lockups or input container desynchronization.
3. **`rslib/procedural/src/problems/steps/step_validator.rs` (CAS & Semantic Equivalence):**
   *Why:* Balances mathematical normalization against false positives. Modifying tolerances or linear equation parsers can misgrade valid student derivations.

### LOW RISK (Relatively isolated changes)
1. **`rslib/procedural/src/problems/generators/` (Individual Problem Generators):**
   *Why:* Each generator implements `ProblemGenerator` in an isolated file. A bug in one generator only affects its specific schema.
2. **`tools/studylab_content_factory.py` (Curriculum Blueprints):**
   *Why:* Declarative content generation external to the runtime engine. Changes are validated by `phase36c_all_175_topics_factory_tests.rs`.
3. **`docs/` (Specifications and Documentation):**
   *Why:* Pure documentation changes with zero runtime side effects.

---

## 12. UNKNOWN / UNVERIFIED AREAS

1. **Native Mistake Classification Button Runtime State `[UNVERIFIED]`:**
   Because `qt/aqt/reviewer.py:1056` dispatches `pycmd("procedural_mistake_select:{val}")` and `_handle_procedural_command` does not handle this command, the exact runtime failure mode during mouse-driven desktop review requires live verification via `desktop-webview-reviewer`.
2. **High-DPI Desktop Scaling & Multi-Monitor Layout `[UNVERIFIED]`:**
   While the 720px Open Canvas layout is verified on standard 1080p laptop viewports, layout integrity on $4\text{K}$ high-DPI displays or fractional scaling ($125\%, 150\%$) remains unverified.
3. **Large Database Scaling ($\ge 100,000$ attempts) `[UNVERIFIED]`:**
   `collection.procedural` performance has been tested up to 1,000 continuous transitions. Query latency on `practice_attempts` and `remediation_queue_items` with months of continuous learner data is unbenchmarked.
4. **Anki Schema Migration Compatibility (Anki 24.x+) `[UNVERIFIED]`:**
   The current codebase is branched from Anki 24.04 (`5f3a102f`). Upstream changes to `rslib` render pipelines or protobuf schemas in newer Anki releases have not been evaluated for merge conflicts.

---

## 13. IMPORTANT EXISTING STRENGTHS

1. **True Two-System Isolation:** StudyLab leaves standard Anki declarative flashcards, FSRS scheduling, and sync infrastructure 100% functional with zero DOM or event leakage.
2. **Industrial-Grade Mathematics & Science Engine:** 15 handcrafted AST generators, 59 declarative math topic contracts, 5D dimensional unit vectors, and CAS step validation provide deep subject capabilities far beyond basic flashcard apps.
3. **Deterministic Verification Harness:** Fast, multi-layered automated testing spanning Rust, TypeScript, Python, and Playwright allows rapid verification of changes.
4. **Dual Content Pathway Flexibility:** Seamlessly supports both immutable curated PYQs (Source-First path) and dynamic generative practice (Procedural path).
5. **Metacognitive Pedagogy Grounding:** Implements evidence-based learning principles (ACT-R production rules, Sweller Cognitive Load Theory, VanLehn Cognitive Tutor inner loop, Metcalfe hypercorrection).

---

## 14. IMPORTANT WEAKNESSES

1. **Polyglot Complexity:** Spliced across Rust, Python/PyQt, TypeScript/Svelte, and SQLite. A developer must navigate cross-language IPC boundaries to modify end-to-end features.
2. **Reviewer Bridge Tight Coupling:** Host bridge logic is embedded directly in `qt/aqt/reviewer.py` rather than encapsulated in an isolated plugin or extension module.
3. **Recent Disconnect in Bottom Toolbar:** The unhandled `procedural_mistake_select` command in `reviewer.py` demonstrates the fragility of cross-language IPC when UI buttons and Python command handlers are refactored independently.
4. **Cluttered Repository Root:** ~20 ad-hoc test scripts and historical markdown reports at the root directory create cognitive noise for incoming developers and AI agents.
5. **Desktop-Only Constraint:** The architecture currently cannot run on mobile clients (AnkiDroid / AnkiMobile) due to reliance on native Rust compiled libraries and desktop PyQt6/QtWebEngine.

---

## 15. QUESTIONS FOR THE ANTIGRAVITY CAPABILITY AUDIT

1. **Live Desktop Webview Inspection:** Can Antigravity's `desktop-webview-reviewer` skill connect to a live running instance of `AnkiStudyLab` via QtWebEngine remote debugging (port 9222) to capture dual-surface screenshots and verify the native bottom toolbar disconnect?
2. **Subagent Specialization:** Can specialized subagents be assigned disjoint language boundaries (e.g., Rust Core Specialist vs. TypeScript Reviewer Specialist) with isolated branch workspaces to modify features without merge conflicts?
3. **Automated Verification Gate Execution:** Can Antigravity reliably execute the full multi-tier verification pipeline (`cargo test -p procedural`, `npm run vitest:once`, `python artifacts_qa/validate_canonical_source_apkg.py`) as mandatory completion gates?
4. **APKG Fixture Ingestion:** Can headless integration test runners reliably import canonical APKG fixtures and verify SQLite reconciliation in a temporary profile environment without user interaction?

---

## WHAT WE NOW KNOW
- StudyLab is an adaptive procedural learning engine hosted inside Anki, maintaining strict Two-System isolation.
- It provides two distinct content architectures: Canonical Source APKGs (immutable PYQs) and Procedural Blueprints (175 curriculum topics).
- Telemetry is passed via `custom_data["studylab"]` and stripped to $\le 100$ bytes before SQLite commit.
- All StudyLab learner state resides in a separate SQLite database (`<collection>.procedural`, 16 tables).
- A disconnect exists in `qt/aqt/reviewer.py`: `procedural_mistake_select` is rendered in the bottom toolbar but not handled in `_handle_procedural_command`.
- Standard Anki cards (`Basic`, `Cloze`) bypass procedural hooks with zero performance or visual overhead.
- Automated test coverage is extensive (134 Rust unit, 71 Rust integration, 150 TypeScript, 93 Python tests).

## WHAT WE STILL NEED TO TEST
- Live user interaction behavior when clicking the native bottom toolbar mistake buttons in a real PyQt6 desktop session.
- High-DPI and multi-monitor layout stability for the 720px Open Canvas container.
- Scaling characteristics of `collection.procedural` under $\ge 100,000$ practice attempts.
- Clean-room build verification of the Briefcase Windows desktop installer from a fresh terminal environment.

## WHAT WE MUST NOT DESIGN YET
- **Do NOT redesign the Anki ↔ StudyLab IPC bridge** until live desktop interaction testing confirms the exact failure mode of the current command dispatch.
- **Do NOT design cloud synchronization for `collection.procedural`** until local desktop performance and schema stability are verified.
- **Do NOT attempt to port StudyLab to mobile (AnkiDroid/AnkiMobile)** before establishing the desktop agent-native framework.
- **Do NOT alter the frozen Level 1 Canonical Source APKG contract** (`docs/APKG_CONTENT_CONTRACT.md`), which remains the foundation of content ingestion.
- **Do NOT design the final Agent-Native Framework** until completing the planned Antigravity Capability Audit and prior-art experiments.
