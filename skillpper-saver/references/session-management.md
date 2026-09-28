# Session Management & Handoff Protocol 🔄

The single largest cost and quota driver in AI coding agents is **uncontrolled session length**.

---

## 1. The Marathon Session Anti-Pattern

Every new message in an active conversation re-transmits the **entire accumulated history** to the LLM:
- In a thread with 50 turns containing terminal outputs and files read, asking a simple question like *"add a comment to line 10"* can re-transmit over 100,000 tokens of context.
- Once context exceeds 100k–150k tokens, response latency spikes and per-turn API costs scale dramatically.

---

## 2. Cutoff Triggers

Terminate the current session and start fresh when **2 or more** of these conditions are met:

1. **More than 15 to 20 tool calls executed** within the same conversation.
2. **Large build, compilation, or test suites** have flooded the transcript.
3. **Multiple large files loaded** into conversational context.
4. **Completion of a logical milestone** (feature implemented, bug verified, database migration run).
5. **Session idle for over 1 hour** (prompt cache expiration).

---

## 3. Active Handoff Protocol (One-Click Resume)

Before suggesting `/clear` or ending a session, generate a structured handoff containing:

1. **Current Status**: What was finished and verified.
2. **Next Steps**: Immediate actionable tasks in bullet points.
3. **Key Files**: Paths to the 2–5 most relevant modified files.
4. **1-Line Resume Command**: A self-contained instruction for the user to paste into the new session.

### Example Handoff Message

```markdown
✅ **Completed**: Created `/api/v1/auth/refresh` endpoint with JWT validation.
📂 **Touched Files**: `src/routes/auth.ts`, `src/services/jwt.ts`.
🎯 **Next Step**: Add integration tests verifying token expiry behavior.

💡 **To continue with clean, cost-effective context**:
Type `/clear` and then run:
> Continue integration tests for the refresh token endpoint as outlined in src/routes/auth.ts.
```
