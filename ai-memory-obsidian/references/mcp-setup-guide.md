# MCP Setup Guide for Memory & Obsidian 🔌

This guide explains how to connect your AI coding agent (Claude Code, Antigravity, Cursor, etc.) to Obsidian vaults and persistent memory engines.

For platform-specific vault paths, data directories, and CLI behavior, see the [Cross-Platform Setup Guide](cross-platform-setup.md).

---

## 1. Connecting to Obsidian via MCP

Choose the connection method that matches your agent and operating system:

### Option A: Direct Filesystem Bridge via `@bitbonsai/mcpvault` (Recommended — Zero Plugins Required)
[`@bitbonsai/mcpvault`](https://www.npmjs.com/package/@bitbonsai/mcpvault) connects directly to your vault folder on disk. It requires no community plugins, no API keys, and works even when Obsidian is closed:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": [
        "-y",
        "@bitbonsai/mcpvault",
        "/absolute/path/to/your/Obsidian/Vault"
      ]
    }
  }
}
```

### Option B: Official Obsidian CLI (No MCP server required)

If your agent can run shell commands, the official CLI can search and edit the vault through the Obsidian desktop app:

```shell
obsidian search query="architecture decisions"
obsidian daily
```

The CLI requires the Obsidian 1.12.7+ installer, command-line interface enabled in Settings, and the Obsidian app running. Registration differs by operating system; follow the [official CLI setup guide](https://obsidian.md/help/cli).

### Optional: Local REST API bridges

The official Obsidian CLI and `@bitbonsai/mcpvault` do not require an Obsidian API key. A key is required only when a user deliberately chooses the third-party Local REST API community plugin or an MCP server built on it.

Prefer the key-free options above. If a Local REST API bridge is required, follow that bridge's current documentation and inject its credential through the MCP client's secret store or another non-committed runtime mechanism. Never paste the key into a repository file, shared agent configuration, example, note, handoff, prompt, shell history, or captured environment dump. Bind the service to loopback unless remote access is explicitly required, and rotate the key immediately if it is disclosed.

---

## 2. Local Memory Engine with `ai-memory`

[`ai-memory`](https://github.com/akitaonrails/ai-memory) is a high-performance local daemon developed by Fabio Akita for cross-session continuity, SQLite FTS5 full-text indexing, and automated multi-agent handoffs.

### Architecture & Capabilities:
1. Runs locally in the background, listening on default port `49374`.
2. Exposes HTTP endpoints and stdio MCP bridging.
3. Enables sub-10ms full-text search across hundreds of historical sessions without token re-reading overhead.

### Stdio Bridge Configuration:
```json
{
  "mcpServers": {
    "ai-memory": {
      "command": "ai-memory",
      "args": ["mcp-bridge"]
    }
  }
}
```

To install and compile the `ai-memory` daemon, follow the official setup instructions at [github.com/akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory).

---

## 3. Direct Filesystem Access (Zero MCP Mode)

If you prefer not to run MCP servers, an agent may manipulate Markdown files directly when its sandbox is explicitly granted access to the intended vault or subdirectory. Keep the vault outside public repositories and do not mount or symlink the vault root into a repository workspace. Use the narrowest access scope supported by the agent.
