---
name: grill-me
description: >-
  Interview the user to clarify requirements, architecture, design, and business rules before implementation. Use the host's available interactive question interface and ask in rounds sized to its limits. Works across macOS, Linux, and Windows. Use when the user asks to grill an idea, plan a major feature, or invokes /grill-me.
---

# /grill-me — Native Interactive Interview Protocol 🎤

A technical alignment skill designed to drill down into requirements, architecture, and business rules before code implementation begins.

---

## ⚡ Quick Install

```bash
npx skills add https://github.com/kipperdev/skillpper --skill grill-me
```

---

## 🎯 Why Does the /grill-me Protocol Exist?

When starting a major feature, refactoring, or new system architecture, unspoken assumptions frequently cause rework. AI coding assistants typically fall into one of two traps:
1. **Blind Assumptions**: The agent guesses architecture or library choices on its own, building solutions misaligned with the developer's tech stack.
2. **Text Slop in Chat**: The agent prints long lists of questions in conversational prose (`❓ Question 1`, `➡️ Options:`), forcing the user to type out tedious paragraphs to answer.

The `/grill-me` protocol uses the question interface available in the current agent. Ask focused multiple-choice questions when supported, then refine the decision tree with the user's answers.

---

## 🌐 Cross-Platform Support

This skill works on macOS, Linux, and Windows. It has no operating-system-specific scripts or paths. Use the active agent's question interface and respect its capabilities, question limits, and available response formats. See the [interview guide](references/interactive-interview.md).

---

## ⚙️ Mandatory Execution Guidelines

### 1. Zero Raw Text in Chat
- **Prefer Native Input**: Use the current agent's interactive question interface when one is available.
- **Use a Clear Fallback**: If the host has no interactive question interface, ask concise questions in the conversation. Do not claim to have opened a modal that is unavailable.

### 2. Interview in Bounded Rounds
- Build a decision tree and ask only questions whose prerequisites are settled.
- Respect the host's per-call question limit. A round may contain fewer questions; cover additional branches in later rounds only when the user's answers make them relevant.
- Prioritize the choices that materially change the implementation:
  - **Scope & Boundaries**: What is included in the MVP and what is explicitly excluded.
  - **Architecture & Libraries**: Target frameworks, persistence engines, and design patterns.
  - **Interface & UX**: Visual layout behavior, loading states, and responsive viewports.
  - **Error Handling & Edge Cases**: Failure modes, permissions, and security constraints.
  - **Testing & Delivery Strategy**: Target test suites and verification criteria.

### 3. Option Formatting
- **First-Person Voice**: Formulate every option as the user's direct response (e.g., *"Use SQLite in WAL mode"* rather than *"The agent should configure..."*).
- **Recommended Option First**: The technically optimal choice recommended by the agent must always appear first, prefixed with `(Recommended)`.
- **Deliberate Multi-Select**: Use multi-select only when combining answers makes sense; use a single choice for mutually exclusive decisions.
- **Respect Host Controls**: Include a write-in option only when the interface does not provide one automatically.

### 4. Transition to Execution
- Wait for the user to answer decisions that materially affect implementation before committing to those choices. Continue independent inspection that does not depend on the answers.

---

## 📚 Supporting References

- [Interactive Interview Guidelines & Alignment Axes](references/interactive-interview.md)
