# Cross-Session & Agent Handoff Protocol 🤝

The handoff protocol ensures seamless context transition across sessions and between diverse agent environments (Claude Code, Antigravity, Cursor) without losing context or wasting tokens re-explaining history.

---

## 1. Core Handoff Structure

When ending an active session, the agent constructs a 4-part summary block:

1. **Completed State**: Features built, commits merged, and tests passed.
2. **Pending Items**: Concrete tasks required immediately in the next turn.
3. **Critical Files**: List of the 2–5 primary files relevant to the upcoming work.
4. **Resume Command**: A clean 1-line prompt ready for the user to paste.

---

## 2. Storage Destinations

- **Option A (Obsidian Vault)**:
  - Append to the session document in `sessions/Session-YYYY-MM-DD.md`.
  - Or log directly into the developer daily note in `dailies/Daily-YYYY-MM-DD.md`.
  - Redact credentials, personal absolute paths, environment dumps, and confidential content before writing.
- **Option B (`ai-memory` Daemon)**:
  - The daemon records the handoff snapshot in SQLite and automatically serves it during SessionStart hook events in new terminals.
  - Confirm its capture and redaction policy before enabling automatic observations; persist only the minimum context needed to resume.

---

## 3. One-Click Resume

When opening a new agent session or terminal window:
- The incoming agent inspects the previous handoff.
- Rather than scanning the entire repository from scratch, it focuses strictly on the specified critical files and initiates the immediate next step.
