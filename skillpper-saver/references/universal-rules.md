# Universal Token Optimization Rules 💡

This reference outlines foundational practices for keeping AI coding agents operating at peak efficiency and minimal token expenditure.

---

## 1. Eliminating Redundant File Reads

Unnecessary file re-reading is the single most common source of token waste in coding agent workflows:

- **Rely on Session Memory**: Once a file is loaded by the agent, its contents remain in context until the session is cleared (`/clear`). Never issue repeated read calls for unchanged files.
- **Avoid Blind Directory Scans**: Instead of recursive directory listings or loading entire modules to infer relationships, use fast search commands (`grep`, `rg`, `find`, `glob`) to pinpoint exact files and line numbers.
- **Slicing with Offset/Limit**: Files longer than 100 lines rarely need to be read in their entirety for localized edits. Specify line ranges or search for the specific function/class signature.

---

## 2. Reducing Output Verbosity

LLM APIs charge for both input tokens (prompt + history + tool results) and generated output tokens. Overly verbose explanations carry direct cost:

- **No Conversational Filler**: Begin immediately with the technical answer or code action.
- **No Redundant Summaries**: Do not restate in prose what the newly generated code already demonstrates.
- **Surgical Diffs**: Always prefer localized contiguous edits (`replace_file_content` or unified diffs) over rewriting entire files from scratch.

---

## 3. Batching Tool Calls

Whenever a task requires multiple independent actions (such as searching two separate files, checking git status, and running a lightweight script), execute them within a **single interaction turn**:

- Eliminates round-trip latency with the LLM API.
- Prevents intermediate turns with partial outputs from re-transmitting the accumulating conversation history.

---

## 4. Selecting Model Tier & Reasoning Effort

- **Lightweight Models (Haiku / Flash / Mini)**: Ideal for code formatting, boilerplate generation, simple documentation updates, and repetitive mechanical tasks.
- **Standard Workhorse Models (Sonnet / Pro)**: Default choice for everyday software development (component creation, route refactoring, standard debugging).
- **Heavy Reasoning (Opus / Ultra / High Effort)**: Reserve strictly for multi-layer architecture decisions, distributed systems trade-offs, and critical security audits.
