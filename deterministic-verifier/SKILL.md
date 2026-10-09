---
name: deterministic-verifier
description: >-
  Enforce empirical, deterministic verification and anti-hallucination gates for AI coding agents. Prevents premature declarations of task completion, bans shotgun debugging, requires red-first reproduction tests for bug fixes, demands real terminal output for test/build gates, and mandates boundary value analysis. Use when completing non-trivial code changes, fixing bugs, refactoring, or when the user demands rigorous QA and proof of correctness before sign-off.
---

# Deterministic Verifier 🔬✅

A rigorous quality assurance and empirical verification skill for AI coding agents.

Based on software reliability engineering: the primary source of bugs introduced by AI coding agents is **premature declaration of completion** ("I have implemented the feature and all tests pass!") without executing actual compiler, linter, and test suites in the terminal, paired with **shotgun debugging** (blind trial-and-error edits when a failure occurs).

This skill enforces a strict **Empirical Evidence First** protocol: no change is complete without deterministic terminal proof.

---

## ⚡ Quick Install

```bash
npx skills add https://github.com/kipperdev/skillpper --skill deterministic-verifier
```

---

## 🎯 When to Use

Activate this skill when:
- The user requests rigorous verification, proof of correctness, reliable QA, or asks "did you test this?".
- Implementing non-trivial features, architectural refactors, or database mutations.
- Investigating and fixing bugs (triggering the **Red-First Reproduction** rule).
- Preparing a pull request or submitting code for human review.
- Invoking `/verify`, `deterministic-verifier`, or running in zero-hallucination mode.

---

## ⚙️ Core Principles & Inviolable Rules

### 1. Zero Declarative Assumptions (Empirical Proof Rule)
- **Never claim a build, typecheck, or test passes without executing it**: You must run the exact terminal command (`npm test`, `pytest`, `cargo test`, `tsc --noEmit`, etc.) and inspect its exit code.
- **Attach raw terminal evidence**: Always show the terminal command and its real exit status (`exit code 0`, test counts, execution time). Detailed reporting conventions are found in the [Evidence Protocol](references/evidence-protocol.md).

### 2. Red-First Bug Reproduction (Inverse TDD)
- When assigned a bug fix, **never modify production code immediately**.
- **Step 1**: Author a minimal automated test that reproduces the defect and fails with exit code != 0.
- **Step 2**: Capture the failing assertion log as baseline evidence.
- **Step 3**: Implement the minimal surgical fix in production code.
- **Step 4**: Re-run the reproduction test and the entire regression suite, proving that the test now passes with exit code 0.

### 3. Anti-Shotgun Debugging Brake
- If a fix or test fails, **stop immediately**. Do not apply random consecutive edits across multiple files.
- Formulate a testable hypothesis: identify the exact variable, type mismatch, or invariant violation.
- Add minimal diagnostic logging or isolate the failing unit before editing further.

### 4. Boundary Value Coverage Matrix
Every stateful or numerical component must be verified against the [Boundary Analysis Matrix](references/boundary-analysis-matrix.md):
- **Empty & Null**: `null`, `undefined`, empty string `""`, empty array `[]`, zero `0`.
- **Extremes**: Maximum integer/float, negative numbers, unicode strings, oversized payloads.
- **Temporal & Spatial**: Leap years, DST transitions, UTC offsets, network latency/timeouts.
- **Concurrency & Races**: Parallel execution, double-spend, idempotency key replay, transactional rollback.

### 5. Anti-Flakiness Contract
- Prohibit arbitrary delays (`sleep(1000)`, `time.sleep()`).
- Use explicit reactive conditions (`waitForSelector`, polling with timeouts, event listeners, condition variables). See [Anti-Flakiness Rules](references/anti-flakiness-rules.md).

### 6. Architectural Test Pyramid & Mocking Boundaries
- Keep a 70% Unit / 20% Integration / 10% E2E distribution.
- Never mock internal domain entities; mock only at 3rd-party architectural boundaries. See [Test Pyramid & Mocking Governance](references/test-pyramid-and-mocking.md).

### 7. Database & State Isolation
- Apply the Expand/Contract migration pattern.
- Wrap integration tests in transactional rollbacks to prevent state leakage. See [Database & Stateful Mutation Verification](references/database-and-state-verification.md).

---

## 🔄 The 4-Stage Verification Workflow

```
[ Stage 1: Static Typecheck & Lint ]
               │
               ▼
[ Stage 2: Unit & Domain Invariants (Red -> Green) ]
               │
               ▼
[ Stage 3: Integration & Boundary Stress ]
               │
               ▼
[ Stage 4: Regression & PR Gate Sign-Off ]
```

### Stage 1: Static Analysis
Execute the project typechecker and linter synchronously:
```bash
# TypeScript / JavaScript
npm run typecheck && npm run lint

# Python
mypy . && ruff check .

# Go / Rust
go vet ./... && golangci-lint run
cargo check && cargo clippy -- -D warnings
```

### Stage 2: Unit & Domain Invariant Suite
Execute the fast, isolated test suite. If fixing a defect, verify that the new test fails first:
```bash
# Example: Running the targeted test file
npm test -- path/to/feature.spec.ts
```

### Stage 3: Integration & Boundary Suite
Verify database transactions, API contracts, middleware, and external service mocks:
```bash
npm test -- --testPathPattern="integration"
```

### Stage 4: Full Regression Gate
Run the complete test suite. Verify that no previously passing tests were broken:
```bash
npm test
```

---

## 📋 Expected Output Format

When concluding a task under `deterministic-verifier`, format your final report as an **Empirical Verification Sign-Off**:

```markdown
### 🔬 Empirical Verification Sign-Off

#### 1. Baseline & Reproduction (Red Phase)
- **Reproduction Test**: `tests/unit/payment-gateway.spec.ts:42`
- **Initial Exit Code**: `1` (Failing as expected with `InsufficientFundsError`)

#### 2. Terminal Execution Log (Green Phase)
- **Command**: `npm test -- tests/unit/payment-gateway.spec.ts`
- **Exit Code**: `0` (Passing: 12 tests passed, 0 failed in 1.42s)

#### 3. Boundary Values Verified
- [x] Zero / negative amount rejected with `InvalidAmountError`
- [x] Concurrent requests handled via optimistic lock
- [x] Idempotency key prevents duplicate transaction

#### 4. Full Regression Status
- **Typecheck**: `tsc --noEmit` -> OK (0 errors)
- **Linter**: `eslint` -> OK (0 warnings)
- **Full Suite**: 86 passing tests across 8 suites
```
