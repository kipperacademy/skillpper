# Testing Anti-Patterns & Pitfalls to Avoid ⚠️

Common mistakes made by AI coding agents when writing and executing automated tests, along with corrective actions.

---

## 1. The Vacuous Pass (Testing Tautologies)

### The Anti-Pattern
Writing assertions that will always pass regardless of the underlying business logic.
```python
# BAD: Asserts nothing meaningful
def test_user_creation():
    user = create_user("alice")
    assert user is not None
    assert True
```

### The Fix
Assert the specific state, side effects, and contracts.
```python
# GOOD: Verifies exact state and persistence contracts
def test_user_creation():
    user = create_user("alice")
    assert user.id is not None
    assert user.username == "alice"
    assert user.is_active is True
```

---

## 2. Mocking the System Under Test (SUT)

### The Anti-Pattern
Mocking the very function, class, or database query you are trying to verify, testing only the mock configuration rather than real behavior.
```typescript
// BAD: Mocking the calculator logic itself
jest.spyOn(calculator, 'add').mockReturnValue(5);
expect(calculator.add(2, 3)).toBe(5); // Tests only the mock!
```

### The Fix
Execute real business logic. Only mock non-deterministic or external boundaries:
- Network HTTP requests (use MSW, Nock, or responses library).
- System clocks and timers (freeze time using timecop or Jest fake timers).
- Third-party message brokers or cloud buckets.

---

## 3. The "Assertion-Free" Smoke Test

### The Anti-Pattern
Running a function without asserting its output or state changes, assuming that absence of a crash means success.
```python
# BAD: Merely checking that no exception was thrown
def test_process_invoice():
    process_invoice(invoice_id=123)
```

### The Fix
Assert state transitions, emitted events, or calculated balances.
```python
# GOOD: Asserts the resultant state
def test_process_invoice():
    invoice = process_invoice(invoice_id=123)
    assert invoice.status == InvoiceStatus.PAID
    assert invoice.paid_at is not None
```

---

## 4. Test Pollution & Shared State

### The Anti-Pattern
Tests that leave rows in a shared database or files in the filesystem, causing subsequent tests to fail intermittently or depend on execution order.

### The Fix
- Use database transactions that roll back automatically after each test.
- Use isolated temporary directories (e.g., Python `tempfile.TemporaryDirectory` with `addCleanup` or pytest `tmp_path` fixture).
- Reset all mocks and global state in teardown hooks (`afterEach`, `tearDown`).

---

## 5. False Confidence: "Tests Pass" Without Terminal Evidence

### The Anti-Pattern
The agent assumes that because code looks correct syntactically, tests must be passing, and answers the user without invoking the test suite.

### The Fix
Always execute the test suite in the terminal, capture the command exit code, and provide direct verification evidence before claiming completion.
