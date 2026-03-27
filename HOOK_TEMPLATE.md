# Hook Contribution Template

Use this template when creating a new hook for hookkit.

## File Structure

Every hook file must follow this structure:

```python
#!/usr/bin/env python3
"""
hook-name — Short description of what the hook does.

Type: PreToolUse | PostToolUse | Stop
Category: safety | workflow | notifications | quality

Configuration:
    HOOKKIT_YOUR_VAR (env var) — Description. Default: "value"

Registration (add to ~/.claude/settings.json):
    {
      "hooks": {
        "HookType": [
          {
            "matcher": "ToolPattern",
            "hooks": [
              {
                "type": "command",
                "command": "python3 ~/.claude/hooks/hook-name.py"
              }
            ]
          }
        ]
      }
    }
"""

import json
import os
import sys


def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())

    # Your hook logic here
    # ...

    # Output result (PreToolUse example)
    # To block: {"decision": "block", "reason": "Why it was blocked"}
    # To allow: (empty output or no output)


if __name__ == "__main__":
    main()
```

## Requirements

1. **Standalone** — No external dependencies. stdlib only.
2. **Docstring header** — Must include: description, type, category, configuration, registration snippet.
3. **Configurable** — Use environment variables with `HOOKKIT_` prefix for configuration. Always provide sensible defaults.
4. **Safe** — Hooks should fail open (allow) on errors, not fail closed (block). Wrap main logic in try/except.
5. **Fast** — Hooks run synchronously. Keep execution under 100ms.
6. **Cross-platform** — Support macOS and Linux where possible. Use platform detection when needed.

## Categories

| Category | Description |
|----------|-------------|
| `safety` | Prevent destructive actions (branch protection, dangerous commands) |
| `workflow` | Automate workflow steps (auto-commit messages, PR templates) |
| `notifications` | Alert the user (task completion, errors) |
| `quality` | Enforce code quality (linting, formatting, type checking) |

## Testing Your Hook

```bash
# Test with sample input
echo '{"tool_name": "Edit", "tool_input": {"file_path": "/tmp/test.py"}}' | python3 hooks/your-hook.py

# Test on a protected branch
cd /tmp && git init test-repo && cd test-repo && git checkout -b main
echo '{"tool_name": "Edit", "tool_input": {"file_path": "test.py"}}' | python3 /path/to/hooks/your-hook.py
```

## Checklist

Before submitting a PR:

- [ ] Hook file is in `hooks/` directory
- [ ] Docstring header includes all required sections
- [ ] No external dependencies
- [ ] Environment variables use `HOOKKIT_` prefix
- [ ] Fails open on errors (try/except around main logic)
- [ ] Tested manually with sample input
- [ ] README catalog table updated
- [ ] `install.sh` updated if needed
