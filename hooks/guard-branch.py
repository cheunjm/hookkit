#!/usr/bin/env python3
"""
guard-branch — Block edits and dangerous git commands on protected branches.

Type: PreToolUse
Category: safety

Prevents accidental modifications to protected branches (main/master by default).
Blocks Edit, Write, NotebookEdit tools and mutating Bash commands (git add,
git commit, git push, rm -rf) when the current branch is protected.

Configuration:
    HOOKKIT_PROTECTED_BRANCHES (env var) — Comma-separated list of protected
        branch names. Default: "main,master"

Registration (add to ~/.claude/settings.json):
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
"""

import json
import os
import subprocess
import sys

PROTECTED_BRANCHES = os.environ.get(
    "HOOKKIT_PROTECTED_BRANCHES", "main,master"
).split(",")

MUTATING_COMMANDS = [
    "git add",
    "git commit",
    "git push",
    "git merge",
    "git rebase",
    "git reset",
    "git checkout --",
    "git restore",
    "rm -rf",
    "rm -r",
]

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}


def get_current_branch(cwd=None):
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def is_mutating_command(command):
    """Check if a bash command is a mutating git/destructive command."""
    cmd = command.strip().lower()
    return any(cmd.startswith(mc) for mc in MUTATING_COMMANDS)


def extract_cwd_from_command(command):
    """Extract target directory from git -C flag if present."""
    parts = command.split()
    if "git" in parts:
        git_idx = parts.index("git")
        if git_idx + 2 < len(parts) and parts[git_idx + 1] == "-C":
            return parts[git_idx + 2]
    return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Determine if this tool call should be checked
        should_check = False
        cwd = None

        if tool_name in EDIT_TOOLS:
            should_check = True
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_mutating_command(command):
                should_check = True
                cwd = extract_cwd_from_command(command)

        if not should_check:
            return

        branch = get_current_branch(cwd=cwd)
        if branch and branch.strip() in [b.strip() for b in PROTECTED_BRANCHES]:
            result = {
                "decision": "block",
                "reason": (
                    f"Blocked: branch '{branch}' is protected. "
                    f"Create a feature branch first. "
                    f"Protected branches: {', '.join(PROTECTED_BRANCHES)}"
                ),
            }
            print(json.dumps(result))

    except Exception:
        # Fail open — don't block on errors
        pass


if __name__ == "__main__":
    main()
