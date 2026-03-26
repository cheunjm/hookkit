# hookkit

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/cheunjm/hookkit/actions/workflows/ci.yml/badge.svg)](https://github.com/cheunjm/hookkit/actions/workflows/ci.yml)

**Curated hook library for Claude Code.**

Claude Code skills have 7,000+ entries and growing marketplaces. Hooks have near zero reusable packages. hookkit fills that gap — a collection of battle-tested, production-ready hooks you can install in seconds.

Each hook is a standalone Python script. No framework, no dependencies, no build step. Copy a file, register it, done.

## Hook Catalog

| Hook | Type | Category | Description |
|------|------|----------|-------------|
| [`guard-branch`](hooks/guard-branch.py) | PreToolUse | Safety | Blocks edits and dangerous git commands on protected branches (main/master) |
| [`dangerous-command-guard`](hooks/dangerous-command-guard.py) | PreToolUse | Safety | Blocks destructive commands like `rm -rf /`, `DROP TABLE`, `git push --force` |
| [`notify-stop`](hooks/notify-stop.py) | Stop | Notifications | Sends a native OS notification when Claude Code finishes a task |
| [`lint-on-edit`](hooks/lint-on-edit.py) | PostToolUse | Quality | Auto-runs your project's linter after every file edit |

## Quick Start

### Option 1: Install Script

```bash
git clone https://github.com/cheunjm/hookkit.git
cd hookkit
./install.sh guard-branch notify-stop
```

### Option 2: Manual Install

1. Copy the hook file to your hooks directory:

```bash
mkdir -p ~/.claude/hooks
cp hooks/guard-branch.py ~/.claude/hooks/
```

2. Register it in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/guard-branch.py"
          }
        ]
      }
    ]
  }
}
```

## How Hooks Work in Claude Code

Claude Code hooks are Python scripts that run at specific points in the agent lifecycle:

- **PreToolUse** — Runs before a tool executes. Can block the action by returning `{"decision": "block", "reason": "..."}`.
- **PostToolUse** — Runs after a tool executes. Can add context or trigger follow-up actions.
- **Stop** — Runs when the agent finishes a task. Good for notifications and cleanup.

Hooks receive context via stdin as JSON and communicate back via stdout JSON. See [HOOK_TEMPLATE.md](HOOK_TEMPLATE.md) for the full specification.

## Configuration

Most hooks support configuration via environment variables. Set them in your shell profile or inline:

```bash
# Example: customize protected branches
export HOOKKIT_PROTECTED_BRANCHES="main,master,production,staging"
```

See each hook's docstring header for available options.

## Contributing

We welcome new hooks! See [HOOK_TEMPLATE.md](HOOK_TEMPLATE.md) for the contribution template and format requirements.

To add a new hook:

1. Create `hooks/your-hook-name.py` following the template
2. Include a docstring header with: description, hook type, configuration, registration snippet
3. Add an entry to the catalog table in this README
4. Update `install.sh` if needed
5. Open a PR

## License

[MIT](LICENSE) - Jace Cheun
