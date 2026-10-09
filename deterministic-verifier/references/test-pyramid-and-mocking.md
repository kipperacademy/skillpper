# Test Pyramid & Mocking Governance 🏗️🎭

Guidelines for structuring test suites and governing the boundary between isolated unit tests, integration contracts, and realistic mocks.

---

## 1. The Proportional Test Pyramid

For any non-trivial codebase or feature implementation, maintain an intentional distribution of automated tests:

```
        / \
       /   \        10% End-to-End (Critical User Journeys, Playwright/Cypress)
      /-----\
     /       \      20% Integration (API Handlers, DB Transactions, Middleware)
    /---------\
   /           \    70% Unit (Pure Business Logic, Domain Entities, Algorithms)
  /-------------\
```

### 70% Unit Tests (Fast & Isolated)
- **Execution Target**: Sub-millisecond execution per test (< 5 seconds for thousands of tests).
- **Scope**: Domain invariants, pure calculation functions, state machines, value objects.
- **Dependencies**: Zero disk I/O, zero network calls, zero process spawning.

### 20% Integration Tests (Contract & Boundary Verification)
- **Scope**: Interaction between application services and infrastructure (ORM queries, SQL migrations, repository implementations, cache decorators, message brokers).
- **Environment**: Testcontainers, local ephemeral databases (SQLite/PostgreSQL in Docker), or in-memory database instances with transactional rollback per test.

### 10% End-to-End Tests (Smoke & Golden Paths)
- **Scope**: Full-stack assembly from HTTP/GraphQL request to database persistence and back, or headless browser automation for core revenue flows (signup, checkout, authentication).
- **Principle**: Keep minimal and high-value; never use E2E to test permutations of edge-case business logic that can be tested in unit tests.

---

## 2. The Over-Mocking Anti-Pattern

> **"If you mock the database, the network, the logger, the repository, and the helper functions, you are no longer testing your code—you are testing your mocks."**

### Inviolable Mocking Rules for AI Coding Agents:

1. **NEVER Mock Internal Domain Logic**:
   - Do not mock your own domain entities, value objects, or algorithmic helpers within the same bounded context.
   - Example (BAD): Mocking `User.canMakePurchase()` when testing the Checkout Service. Use real domain instances.

2. **Mock at Architectural Boundaries Only**:
   - Only mock external 3rd-party SaaS integrations (Stripe, Twilio, SendGrid, AWS S3) where real network calls are cost-prohibitive, rate-limited, or destructive.

3. **Fakes over Mocks**:
   - Prefer in-memory fakes implementing the interface (`InMemoryUserRepository`) over dynamic mocks (`jest.spyOn()` / `unittest.mock.MagicMock`). Fakes verify interface fidelity and can be reused across test suites.

4. **Verify Contract Integrity**:
   - When mocking external APIs, ensure mock payloads adhere to verified OpenAPI/JSON Schema definitions. Never invent mock response structures out of thin air.
