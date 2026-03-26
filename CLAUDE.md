# hookkit

Curated hook library for Claude Code. Each hook is a standalone Python script in `hooks/`.

## Structure

```
hooks/              # Hook scripts (Python, standalone)
install.sh          # Installer script
HOOK_TEMPLATE.md    # Contributing template
.github/workflows/  # CI (ruff lint)
```

## Development

- Hooks must be standalone Python scripts (no external dependencies)
- Each hook must have a docstring header explaining what it does, hook type, config, and registration
- Hooks receive JSON on stdin and output JSON on stdout
- Lint: `ruff check hooks/`
- Format: `ruff format hooks/`

## Hook Types

- **PreToolUse**: Block actions by returning `{"decision": "block", "reason": "..."}`
- **PostToolUse**: React after tool use, return empty or context
- **Stop**: Run on task completion, no return value needed
