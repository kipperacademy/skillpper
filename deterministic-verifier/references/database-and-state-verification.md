# Database & Stateful Mutation Verification 🗄️🔄

Protocols for safely verifying database migrations, transactional consistency, concurrency locks, and stateful mutations.

---

## 1. Zero-Downtime Migration Pattern (Expand / Contract)

When modifying database schemas, verify that migrations do not lock tables or break running instances:

### Phase 1: Expand
- Add new columns as **nullable** or with default values.
- Never drop or rename columns in the same release.
- Verify migration scripts execute forward and backwards:
  ```bash
  # Forward migration verification
  npm run prisma:migrate deploy || npm run db:migrate
  
  # Backward rollback verification (dry-run or staging)
  npm run db:rollback
  ```

### Phase 2: Double-Writing & Backfilling
- Application writes to both old and new columns.
- Background jobs backfill existing rows.

### Phase 3: Contract
- Only drop the deprecated column in a subsequent release after all deployed application nodes read exclusively from the new column.

---

## 2. Concurrency & Race Condition Verification

For stateful financial engines, inventory systems, or voting platforms, you MUST write automated concurrency tests:

```typescript
// Example: Verifying double-spend prevention under parallel load
test('concurrent transfers do not create money out of thin air', async () => {
  const account = await createAccount({ balance: 100 });

  // Simulate 10 parallel attempts to withdraw 100 simultaneously
  const attempts = Array.from({ length: 10 }).map(() =>
    withdrawFunds(account.id, 100)
  );

  const results = await Promise.allSettled(attempts);

  const successful = results.filter(r => r.status === 'fulfilled');
  const rejected = results.filter(r => r.status === 'rejected');

  // Exactly 1 must succeed; 9 must fail due to lock contention or insufficient funds
  expect(successful).toHaveLength(1);
  expect(rejected).toHaveLength(9);

  const finalBalance = await getBalance(account.id);
  expect(finalBalance).toBe(0);
});
```

---

## 3. Test Isolation & Hermetic State

1. **Transactional Rollback Per Test**:
   - Wrap each integration test in a database transaction (`BEGIN`) and execute `ROLLBACK` at test teardown. This ensures instant cleanup and zero state contamination across tests.
2. **Deterministic Seeders**:
   - Never rely on residual test data from previous runs. Always seed the minimal required fixture within the test itself.
3. **No Global Singletons**:
   - Avoid global mutable state in services. Pass dependencies and transaction handles explicitly.
