---
name: skillpper-saver
description: >-
  Aggressive token, context, and cost optimization mode for AI coding agents (Claude Code, Antigravity, Cursor, etc.). Prevents marathon sessions, eliminates redundant file re-reading, prioritizes text extraction over screenshots in browser automation, and manages context windows with surgical cutoff triggers. Use when the user requests token savings, context optimization, quota conservation, or when starting extensive refactoring, browsing, or debugging tasks.
---

# Skillpper Saver 🐿️⚡

A governance and aggressive optimization skill designed to reduce token consumption, operating costs, and context window bloating for AI coding agents.

This skill supports macOS, Linux, and Windows. See the [Cross-Platform Guide](references/cross-platform.md) for shell and path handling.

Based on empirical development metrics: the primary drivers of runaway token consumption are not high-end models themselves, but rather **marathon sessions** (threads running for tens of hours), **repetitive re-reading of identical files**, **unnecessary screenshots during web automation**, and **dumping massive terminal logs** directly into the context window.

---

## ⚡ Quick Install

```bash
npx skills add https://github.com/kipperacademy/skillpper --skill skillpper-saver
```

---

## 🎯 When to Use

Activate this skill when:
- The user asks to "save tokens", "reduce cost", "run in saver mode", "skillpper saver", "muri saver", or `/saver`.
- The developer operates under strict API budgets or session window rate limits (e.g., 5-hour rolling quotas or weekly caps).
- The task requires deep exploration of large codebases, complex debugging, or multi-step browser QA.

---

## ⚙️ Universal Execution Rules

### 1. Direct Responses Without Slop
- **Zero Preamble**: Never repeat the user's prompt or provide conversational filler ("Sure thing!", "I would be happy to help with that...").
- **Concise Summaries**: Limit completion responses to 1–2 actionable sentences highlighting what was changed or the immediate next step.
- **No Code Mirroring**: Never restate large blocks of unchanged code. Only display concise git diffs or edited segments.

### 2. Surgical File Reading
- **Grep/Glob First**: Never read entire files to find a single declaration or symbol. Locate the exact line range first using targeted search.
- **Partial Reads**: For files exceeding 100 lines, use line slicing (`StartLine`/`EndLine` or `offset`/`limit`) instead of loading the entire content.
- **Never Re-read**: Never re-read a file already loaded in the current session unless it was modified externally or by an edit tool. Trust what is already present in context.

### 3. Context Auto-Monitoring & Cutoff Triggers
- **150k Accumulated Context Threshold**: When a session reaches 2+ of the following signals, proactively suggest `/compact` or `/clear` with a 1-line handoff:
  - 15+ tool calls executed in the current thread.
  - Large build, compilation, or test suites logged in history.
  - Multiple large source files loaded into context.
  - Session wall-time exceeds 30 minutes with heavy tool usage.
- **Idle Inactivity**: If a session remains inactive for over 1 hour, the prompt cache has expired. Summarize and start a fresh session to avoid re-paying full un-cached prompt tokens.

### 4. Subagent Governance
- **Avoid Spurious Subagents**: Never spawn subagents for small, sequential tasks. A new subagent incurs a fixed cost by re-deriving the entire project context from scratch.
- **Lightweight Delegation**: When delegating purely mechanical or broad scanning tasks, explicitly configure subagents to use lightweight models (`haiku`, `flash`, or `flash_lite`).

### 5. Tool Loop Brake
- **Anti-Loop Safety**: If a tool call or terminal command fails twice with the identical error, do not retry a third time blindly. Stop immediately, diagnose the root cause, or ask for developer guidance.

### 6. Browser Automation (Rule: Text > Screenshots)
- **Text Extraction First**: To verify navigation, clicks, or loaded content, always extract DOM text (rendered HTML, page headings, or accessibility tree).
- **Strict Visual Criteria**: Only take screenshots when the task is inherently visual (e.g., layout reviews, CSS styling checks, responsive viewports). Screenshots persist indefinitely in conversational history and are never evicted by prompt caching, inflating every subsequent turn.

### 7. Surgical Log & Error Handling
- **Immediate Truncation**: If a terminal command, build tool, or test runner produces more than 50 lines of output, extract only the first 5 lines, the core error message, and the immediate stack trace.
- **Massive Logs**: Never paste multi-hundred-line outputs into the chat. Pipe them to a local file (e.g., `scratch/error.log`) and inspect using grep.

---

## 💰 Model Tier & Cost Efficiency Reference

| Tier | Example Models | Relative Cost | Recommended Tasks |
| :--- | :--- | :--- | :--- |
| **Fast / Lightweight** | Claude 3.5 Haiku, Gemini 2.0 Flash / Flash-Lite, GPT-4o-mini | **1x (Baseline)** | Mechanical tasks, boilerplate, file scanning, formatting, simple PR descriptions. |
| **Standard Workhorse** | Claude 3.5 Sonnet, Gemini 2.0 Pro, GPT-4o | **~5x** | Core application coding, refactoring, feature implementation, regular debugging. |
| **Heavy Reasoning** | Claude 3.7 Sonnet (High Effort), Claude 3 Opus, o1 / o3-mini | **~15x–30x** | Complex distributed systems architecture, subtle concurrency bugs, security reviews. |

---

## 🧭 Workflow by Task Type

| Task Type | Recommended Economy Practice | Reference |
| :--- | :--- | :--- |
| **Backend & APIs** | Targeted Grep by route/controller signature; run only the specific test for the touched endpoint. | [Tools Guide](references/automation-and-tools.md) |
| **Frontend & UI** | Reuse existing styling tokens; capture screenshots only after finishing an entire component block. | [Tools Guide](references/automation-and-tools.md) |
| **Browser & QA** | Extract text via DOM/Accessibility Tree; prohibit screenshots for step verification. | [Tools Guide](references/automation-and-tools.md) |
| **Architecture & Refactoring** | Record decisions in atomic local notes and terminate sessions before accumulating stale context. | [Session Guide](references/session-management.md) |

---

## 📚 Supporting References

- [Universal Optimization Rules](references/universal-rules.md)
- [Session Management & Handoff Protocol](references/session-management.md)
- [Automation, Browser & Tool Best Practices](references/automation-and-tools.md)
