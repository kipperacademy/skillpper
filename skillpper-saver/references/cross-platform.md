# Cross-Platform Guidance

Skillpper Saver supports macOS, Linux, and Windows. The guidance applies across Claude Code, Codex, Antigravity, and other coding agents; it does not require an agent-specific directory layout.

## Paths and files

- Resolve files from the installed skill directory or the current repository root. Do not assume a fixed home directory, username, drive letter, or agent configuration folder.
- Prefer the agent's file and search tools for repository work. When a shell command is necessary, use the active shell's syntax and quote paths that may contain spaces.
- Use platform-aware path APIs in scripts. On Windows, account for drive letters and both slash styles; on macOS and Linux, account for POSIX paths and case-sensitive filesystems.

## Shells and tools

- Do not assume Bash is available on Windows or PowerShell is available on macOS and Linux. Select commands for the shell the agent actually provides.
- Prefer tools already available through the agent over shell-specific utilities. If a tool is missing, check for a platform-neutral equivalent before changing the user's environment.
- Keep examples focused on their intent. Label any Bash, PowerShell, or platform-specific command explicitly.

## Portable verification

- Keep packaged Markdown references relative to `SKILL.md`.
- Validate the `.skill` archive after changing any packaged file. The archive should extract with its skill directory intact on all supported operating systems.
- Avoid case-only differences in filenames because filesystems handle case differently.
