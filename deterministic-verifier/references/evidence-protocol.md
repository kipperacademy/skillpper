# Evidence-First Verification Protocol 📜🔬

This protocol defines the non-negotiable verification gates required before any non-trivial code modification is deemed complete.

---

## 1. The Core Axiom

> **"Code that has not been executed in the terminal with an exit status of 0 does not work. Declarative claims of correctness without command logs are hallucinations."**

An AI coding agent operating under this protocol cannot state *"The changes are tested and working"* without providing verifiable output from a command line tool.

---

## 2. The Verification Stages

### Stage 1: Static Type & Linter Verification
Every modern strongly-typed or linted project has a static analysis toolchain. Run it before testing:
- **Zero Errors**: Compilation must yield exit code `0`.
- **Zero Suppression**: Do not introduce `@ts-ignore`, `eslint-disable`, `# type: ignore`, or `@SuppressWarnings` without explicit human instruction.

### Stage 2: Bug Fix Protocol (Red-Green TDD)
When addressing an issue or regression:
1. **Red Phase (Reproduction)**:
   - Write a test targeting the defect in `test/` or `__tests__/`.
   - Run the test in isolation.
   - Capture the failure output (e.g., `AssertionError: expected 400 to equal 200`).
   - Confirm the failure reason directly matches the bug report.
2. **Green Phase (Surgical Implementation)**:
   - Edit only the code required to satisfy the invariant.
   - Run the reproduction test again until it passes with code `0`.
3. **Refactor & Regression**:
   - Run the full suite to verify no ancillary breakage.

### Stage 3: Anti-Shotgun Debugging Rules
When an unexpected failure occurs:
- 🛑 **Do NOT**: Randomly edit 4 different files hoping the error disappears.
- 🛑 **Do NOT**: Chain multiple untested changes together.
- ✅ **DO**: Read the stack trace to the exact line number.
- ✅ **DO**: Formulate a single falsifiable hypothesis (e.g., *"Function X receives null when header Y is omitted"*).
- ✅ **DO**: Add a temporary assertion or debug statement, run once, observe output, fix root cause, remove debug statement.

---

## 3. Terminal Evidence Template

When concluding your work, include a structured verification block:

```markdown
### 🔬 Empirical Verification Sign-Off

- **Target Component**: `src/services/billing.ts`
- **Reproduction Test**: `tests/billing.spec.ts:18`
- **Red Baseline**: `exit code 1` (Failed with `BillingCycleMismatchError`)
- **Green Verification**: `exit code 0` (4 passing assertions in 120ms)
- **Static Checks**:
  - `npm run typecheck` -> exit 0 (0 errors)
  - `npm run lint` -> exit 0 (clean)
- **Full Suite**: 142/142 tests passing across 12 suites
```
