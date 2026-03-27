#!/usr/bin/env python3
"""
notify-stop — Send a native OS notification when Claude Code finishes a task.

Type: Stop
Category: notifications

Sends a desktop notification using osascript (macOS) or notify-send (Linux)
when Claude Code completes a task. Useful when running long tasks in the
background so you know when to come back.

Configuration:
    HOOKKIT_NOTIFY_TITLE (env var) — Notification title. Default: "Claude Code"
    HOOKKIT_NOTIFY_SOUND (env var) — macOS sound name. Default: "Glass"
        Set to "" to disable sound.

Registration (add to ~/.claude/settings.json):
    {
      "hooks": {
        "Stop": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "python3 ~/.claude/hooks/notify-stop.py"
              }
            ]
          }
        ]
      }
    }
"""

import json
import os
import platform
import subprocess
import sys


def notify_macos(title, message, sound):
    """Send notification via osascript on macOS."""
    sound_part = ""
    if sound:
        sound_part = f' sound name "{sound}"'
    script = f'display notification "{message}" with title "{title}"{sound_part}'
    subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        timeout=5,
    )


def notify_linux(title, message):
    """Send notification via notify-send on Linux."""
    subprocess.run(
        ["notify-send", title, message],
        capture_output=True,
        timeout=5,
    )


def truncate(text, max_length=100):
    """Truncate text to max_length, adding ellipsis if needed."""
    if not text:
        return "Task completed"
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        title = os.environ.get("HOOKKIT_NOTIFY_TITLE", "Claude Code")
        sound = os.environ.get("HOOKKIT_NOTIFY_SOUND", "Glass")

        # Extract a summary from the stop reason or transcript
        stop_reason = input_data.get("stop_reason", "")
        message = truncate(stop_reason) if stop_reason else "Task completed"

        system = platform.system()
        if system == "Darwin":
            notify_macos(title, message, sound)
        elif system == "Linux":
            notify_linux(title, message)
        # Windows and other platforms: silently skip

    except Exception:
        # Notifications are best-effort — never fail the agent
        pass


if __name__ == "__main__":
    main()
