# Automation, Browser & Tool Best Practices 🛠️

Guidelines for mindful tool usage when agents run shell commands, browser automation, and MCP servers.

---

## 1. Browser Automation Rule: Text > Screenshots

In browser automation (Playwright, Puppeteer, Chrome DevTools Protocol, Computer Use):

- **Screenshots Persist Permanently**: Images consume 1,000 to 3,000+ tokens each. Once added to conversational history, they are re-billed on every single subsequent interaction turn.
- **Text Extraction Solves 95% of Tasks**:
  - To verify page load: check `<title>` or the primary `<h1>`.
  - To verify error alerts or form validation: extract the element text or inspect the accessibility tree.
  - To locate interactive elements: query selectors and anchor text.
- **When are Screenshots Justified?**: Strictly when visual review is requested (CSS breakpoint fidelity, typography alignment, visual polish).

---

## 2. Surgical Error Log Handling

- If a terminal command generates a massive stack trace (50–500+ lines):
  - Never dump the entire log into the conversation context.
  - Isolate the core error message (e.g., `TypeError: Cannot read properties of undefined`) and the 2–3 immediate stack frames.
  - This reduces error-turn token overhead by up to 90%.

---

## 3. Mindful MCP Tool Usage

- **Single Schema Load**: Initialize and search MCP tools once per session. Avoid repeatedly re-querying tool definitions.
- **Dedicated CLI Commands over Generic APIs**: Prefer targeted subcommands (e.g., `gh pr view`, `gh issue list`) over unbounded generic API endpoints, enabling better caching and granular permission controls.
