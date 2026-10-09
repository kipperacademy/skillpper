# Anti-Flakiness Testing Rules 🛡️⏱️

Techniques and contracts to prevent flaky automated tests in asynchronous, concurrent, and end-to-end environments.

---

## 1. The Zero-Sleep Mandate

> **NEVER use arbitrary time pauses (`sleep`, `time.sleep()`, `Thread.sleep()`) to wait for asynchronous operations.**

### Why arbitrary sleeps fail:
- In local development, `sleep(500)` might be enough; in busy CI runners, it randomly times out.
- They drastically slow down the test suite without providing deterministic guarantees.

---

## 2. Deterministic Wait Alternatives

### Pattern A: Polling with Predicate Assertions
Instead of sleeping for 2 seconds waiting for a database write or file update, poll with a timeout and short interval:

```typescript
// BAD:
await sleep(1000);
expect(await getOrderStatus(id)).toBe('COMPLETED');

// GOOD:
await waitFor(async () => {
  const status = await getOrderStatus(id);
  expect(status).toBe('COMPLETED');
}, { timeout: 3000, interval: 50 });
```

### Pattern B: Event-Driven Synchronization
Subscribe to domain events or callback completion rather than guessing timestamps:

```typescript
// GOOD:
await new Promise<void>((resolve, reject) => {
  eventEmitter.once('order:processed', (order) => {
    try {
      expect(order.status).toBe('COMPLETED');
      resolve();
    } catch (err) {
      reject(err);
    }
  });
  triggerOrderProcessing();
});
```

### Pattern C: Web UI & Playwright Assertions
Never wait for arbitrary milliseconds in browser automation. Leverage auto-waiting locator assertions:

```typescript
// BAD:
await page.waitForTimeout(2000);
await page.click('button#submit');

// GOOD:
const submitButton = page.locator('button#submit');
await expect(submitButton).toBeVisible();
await submitButton.click();
await expect(page.locator('.toast-success')).toBeVisible();
```

---

## 3. Hermetic Test Environment

1. **Deterministic Clocks**: Mock time (`jest.useFakeTimers()`, `sinon.useFakeTimers()`) for time-dependent workflows (e.g. JWT expiration, cron scheduling, TTL caches).
2. **Deterministic Randomness**: Seed pseudorandom generators (`Math.random`, `faker.seed()`) when testing algorithms reliant on randomness.
3. **Isolated Test State**: Ensure each test executes in its own database transaction or cleans up all created entities via `beforeEach` / `afterEach` hooks.
