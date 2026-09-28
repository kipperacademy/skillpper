# Cross-Platform Setup

The skill supports macOS, Linux, and Windows. It uses portable Markdown and MCP concepts, while vault and data paths must match the operating system running the agent and MCP server.

## Obsidian vault paths

Do not assume a vault is in a standard Documents folder or use the skill author's home directory. Ask the user for the vault location or use the path already configured by their Obsidian/MCP client.

| Platform | Example native path |
| --- | --- |
| macOS | `/Users/<username>/Documents/<vault>` |
| Linux | `/home/<username>/Documents/<vault>` |
| Windows | `C:/Users/<username>/Documents/<vault>` |

For `@bitbonsai/mcpvault`, put the actual absolute vault path in the MCP server's argument list. In JSON on Windows, escape each backslash. MCP client configuration locations and command-line registration differ by agent, so use that agent's current setup interface instead of hard-coding one client's config path into this skill.

MCPVault uses Node.js and a local filesystem path. It can access Markdown files without launching Obsidian. Obsidian's official CLI is a separate option: it requires the Obsidian 1.12.7+ installer, CLI registration, and the desktop app running. Check the [official CLI guide](https://obsidian.md/help/cli) for current setup instructions.

## ai-memory data directories

Use the `ai-memory` CLI's platform defaults, or set `AI_MEMORY_DATA_DIR` when the user intentionally chooses a custom location. Current defaults are:

| Platform | Default data directory |
| --- | --- |
| macOS | `~/Library/Application Support/ai-memory` |
| Linux | `~/.local/share/ai-memory` |
| Windows | `%LOCALAPPDATA%/ai-memory` |

Do not construct these paths with string concatenation or copy one platform's path into another platform's hook configuration. Let the CLI resolve its default, or use the platform's path APIs and environment variables. See the [official installation guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) for native service and platform-specific setup.

## Portable agent instructions

- Keep references relative to this skill directory.
- Do not require `.claude/`, `.codex/`, or `.gemini/` directories. Agent configuration paths belong in agent-specific setup instructions.
- When a shell command is needed, detect the available shell and use its syntax. Label Bash, PowerShell, or other shell-specific examples.
- Quote paths in commands and configuration values when they can contain spaces.
