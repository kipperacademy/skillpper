# Boundary Value Analysis Matrix 📐🧱

A systematic checklist for identifying edge cases and boundary conditions that AI coding agents commonly overlook.

---

## 1. Primitive & Structural Boundaries

| Category | Boundary Scenarios to Test | Failure Modes Prevented |
|---|---|---|
| **Numeric Values** | `0`, `-1`, `1`, `MAX_SAFE_INTEGER`, `MIN_SAFE_INTEGER`, `Infinity`, `NaN`, floating point inaccuracies (`0.1 + 0.2`) | Division by zero, integer overflow, rounding mismatch in financial calculations |
| **Strings & Text** | `""` (empty), whitespace-only (`"   "`), single character, strings with emojis (`🐿️`), unicode astral planes, multibyte UTF-8, strings > 64KB | Off-by-one substring errors, unhandled whitespace trim, buffer truncation, encoding crash |
| **Collections** | `[]` (empty), single element `[x]`, large arrays (10,000+ items), duplicated items, sparse arrays | IndexOutOfBounds, memory exhaustion, accidental N+1 queries, unhandled head/tail logic |
| **Object / Nullability** | `null`, `undefined`, missing keys, circular references, prototype pollution keys (`__proto__`, `constructor`) | NullPointerExceptions, `Cannot read property of undefined`, injection vulnerabilities |

---

## 2. Temporal & Date Boundaries

| Category | Boundary Scenarios to Test | Failure Modes Prevented |
|---|---|---|
| **Date & Time** | Leap year (`2024-02-29`), end of month rollover, Daylight Saving Time (DST) forward/backwards transitions, midnight `00:00:00`, timezone offset shifts (e.g. UTC-3 to UTC) | Off-by-one day bugs, schedule duplication, timezone desynchronization |
| **Durations & Expiry** | Exactly at expiry time (`t == expires_at`), 1 millisecond before, 1 millisecond after | Premature revocation, expired token acceptance, race on token refresh |

---

## 3. Concurrency & State Invariants

| Category | Boundary Scenarios to Test | Failure Modes Prevented |
|---|---|---|
| **Parallel Mutation** | 2+ simultaneous requests updating the exact same record or balance | Race conditions, double-spend, lost updates (requires optimistic locking or serializable transactions) |
| **Idempotency** | Duplicate webhook delivery, replayed HTTP requests with identical `Idempotency-Key` | Duplicate orders, duplicate payments, ghost record creation |
| **Partial Failure** | Network drop after step 2 of a 3-step operation | Inconsistent state, orphaned foreign keys (requires atomic rollback or saga compensation) |
