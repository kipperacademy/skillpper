# Red-Green-Refactor In-Depth Guide 🔁

A comprehensive reference for executing the test-driven development cycle with automated coding agents.

---

## 1. The Discipline of the RED Phase

When creating a new feature or fixing a reported bug:

1. **Locate or Create the Test File**:
   - Place the test adjacent to the implementation or in the canonical `tests/` directory following repository conventions.
   - Name test functions descriptively using behavioral phrasing:
     - Python: `def test_calculates_compound_interest_with_monthly_accrual():`
     - TypeScript/Jest: `it('rejects expired authorization tokens with 401 Unauthorized', async () => {})`
     - Go: `func TestTokenExpiration_ReturnsUnauthorized(t *testing.T) {}`
2. **Execute and Capture the Failure**:
   - Run the specific test command.
   - Inspect the failure stack trace:
     - Expected: `AssertionError`, `ValueError`, or compilation error pointing directly to the missing symbol or condition.
     - Unexpected: `ModuleNotFoundError` due to broken package setup or missing runner dependencies. Fix environment issues first before proceeding.
3. **Document the Evidence**:
   - Verify that the test fails because the code is not yet implemented, proving that the test is actually measuring the desired behavior.

---

## 2. The Restraint of the GREEN Phase

The single goal of the Green phase is to reach passing state as quickly and cleanly as possible.

1. **Do the Simplest Thing That Could Possibly Work**:
   - Implement the direct logic satisfying the assertion.
   - If a test expects an empty list when input is empty, return an empty list.
2. **Avoid "While I'm Here" Scope Creep**:
   - Do not implement helper methods or edge-case handling that is not covered by a failing test.
   - If you notice an unhandled edge case, write down a new test case for the next Red cycle instead of adding untested defensive code immediately.
3. **Confirm Clean Pass**:
   - Re-run the test command.
   - Verify that exit code is `0` and the test output explicitly reports success (`PASS`, `OK`).

---

## 3. The Care of the REFACTOR Phase

Refactoring is only done when tests are green.

1. **Keep Tests Passing Continuously**:
   - Make small, atomic improvements to the production code.
   - Run tests after each small change. If tests break, undo or fix immediately.
2. **Focus Areas During Refactoring**:
   - **Clarity over Cleverness**: Replace cryptic one-liners with readable functions.
   - **DRY (Don't Repeat Yourself)**: Extract duplicated logic into private helpers.
   - **Boundary Integrity**: Ensure functions remain pure where possible and side effects are isolated.
   - **Test Code Quality**: Refactor test fixtures and helpers as well to keep test files maintainable.
