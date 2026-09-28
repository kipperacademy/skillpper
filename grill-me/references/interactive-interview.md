# Interactive Interview Guidelines & Alignment Axes 📋

A guide for AI coding agents to structure focused, iterative interviews when executing the `/grill-me` protocol.

The guide is platform-neutral and requires no scripts or fixed paths. Use the interactive input supported by the current agent on macOS, Linux, or Windows. If a host limits questions per call, ask a small first round and continue only along branches made relevant by the answers.

---

## 1. Five Fundamental Axes of Any Technical Task

When asking questions, use the following axes to choose the decisions that matter for the task. Do not force every axis into one round:

1. **Scope & Delivery Boundaries**:
   - What is the minimum viable deliverable for this task?
   - Which files, endpoints, or modules must NOT be modified?
2. **Architecture & Data Contracts**:
   - What architectural pattern should be followed (Clean Architecture, MVC, Event-driven)?
   - How should data payloads flow (REST, GraphQL, gRPC, WebSockets)?
3. **State Management & Dependencies**:
   - Which existing libraries or utilities in the codebase should be reused?
   - What persistence or caching mechanism should be employed?
4. **Interface & User Experience (if applicable)**:
   - What design system tokens or CSS conventions apply?
   - How should loading spinners, empty states, and network errors be rendered?
5. **Testing & Validation Strategy**:
   - Which test levels are mandatory (unit, integration, e2e)?
   - Are there specific coverage thresholds or CI pipelines that must pass?

---

## 2. Best Practices for Formulating Options

- **Be Concrete**: Avoid ambiguous questions like *"What database do you want?"*. Prefer: *"Which database engine should be used for the telemetry audit store?"*.
- **Ground the Recommendation**: In the first `(Recommended)` option, summarize the technical rationale (e.g., `(Recommended) Local SQLite in WAL mode — zero external infrastructure, sub-millisecond query latency`).
- **Respect User Selection**: When the user picks a non-recommended option, accept the architectural decision without arguing and execute accordingly.
