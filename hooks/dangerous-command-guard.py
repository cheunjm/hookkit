#!/usr/bin/env python3
"""
dangerous-command-guard — Block destructive and dangerous commands.

Type: PreToolUse
Category: safety

Prevents execution of commands that could cause severe damage: recursive
deletion of root, SQL table drops, force pushes, hard resets, permission
escalation, and fork bombs.

Configuration:
    HOOKKIT_EXTRA_BLOCKED (env var) — Comma-separated list of additional
        command patterns to block. Default: "" (empty)

Registration (add to ~/.claude/settings.json):
    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "Bash",
            "hooks": [
              {
                "type": "command",
                "command": "python3 ~/.claude/hooks/dangerous-command-guard.py"
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

# Default blocked patterns — each is (pattern, description)
BLOCKED_PATTERNS = [
    ("rm -rf /", "Recursive deletion of root filesystem"),
    ("rm -rf /*", "Recursive deletion of root filesystem"),
    ("rm -rf ~", "Recursive deletion of home directory"),
    ("drop table", "SQL table drop"),
    ("drop database", "SQL database drop"),
    ("git push --force", "Force push (use --force-with-lease instead)"),
    ("git push -f", "Force push (use --force-with-lease instead)"),
    ("git reset --hard", "Hard reset (destructive, loses uncommitted changes)"),
    ("chmod 777", "Overly permissive file permissions"),
    ("chmod -R 777", "Recursive overly permissive file permissions"),
    (":(){ :|:& };:", "Fork bomb"),
    ("mkfs.", "Filesystem format command"),
    ("dd if=/dev/zero", "Disk overwrite"),
    ("> /dev/sda", "Direct disk write"),
]


def load_extra_blocked():
    """Load additional blocked patterns from environment."""
    extra = os.environ.get("HOOKKIT_EXTRA_BLOCKED", "").strip()
    if not extra:
        return []
    return [(p.strip(), "Custom blocked pattern") for p in extra.split(",") if p.strip()]


def check_command(command):
    """Check if a command matches any blocked pattern. Returns (matched, description) or None."""
    cmd_lower = command.lower().strip()
    all_patterns = BLOCKED_PATTERNS + load_extra_blocked()

    for pattern, description in all_patterns:
        if pattern.lower() in cmd_lower:
            return pattern, description
    return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name != "Bash":
            return

        command = tool_input.get("command", "")
        if not command:
            return

        match = check_command(command)
        if match:
            pattern, description = match
            result = {
                "decision": "block",
                "reason": (
                    f"Blocked dangerous command. Matched pattern: '{pattern}' "
                    f"({description}). If you need to run this command, "
                    f"review it carefully and run it manually."
                ),
            }
            print(json.dumps(result))

    except Exception:
        # Fail open — don't block on errors
        pass


if __name__ == "__main__":
    main()
