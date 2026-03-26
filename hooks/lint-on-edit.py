#!/usr/bin/env python3
"""
lint-on-edit — Auto-run linter after file edits.

Type: PostToolUse
Category: quality

Automatically runs the project's linter after Edit or Write tool calls.
Detects the appropriate linter based on project files (ruff for Python,
eslint for JavaScript/TypeScript, prettier for formatting) or uses a
custom linter specified via environment variable.

Configuration:
    HOOKKIT_LINTER (env var) — Custom lint command to use instead of
        auto-detection. Example: "ruff check --fix"
    HOOKKIT_LINT_EXTENSIONS (env var) — Comma-separated list of file
        extensions to lint. Default: ".py,.js,.ts,.jsx,.tsx,.css,.json"

Registration (add to ~/.claude/settings.json):
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [
              {
                "type": "command",
                "command": "python3 ~/.claude/hooks/lint-on-edit.py"
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

DEFAULT_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".css", ".json"}

# Linter detection: (config file, command, file extensions)
LINTER_CONFIGS = [
    ("pyproject.toml", "ruff check", {".py"}),
    ("setup.cfg", "ruff check", {".py"}),
    (".flake8", "flake8", {".py"}),
    (".eslintrc.json", "npx eslint", {".js", ".ts", ".jsx", ".tsx"}),
    (".eslintrc.js", "npx eslint", {".js", ".ts", ".jsx", ".tsx"}),
    (".eslintrc.yml", "npx eslint", {".js", ".ts", ".jsx", ".tsx"}),
    ("eslint.config.js", "npx eslint", {".js", ".ts", ".jsx", ".tsx"}),
    ("eslint.config.mjs", "npx eslint", {".js", ".ts", ".jsx", ".tsx"}),
    (".prettierrc", "npx prettier --check", {".js", ".ts", ".jsx", ".tsx", ".css", ".json"}),
]


def get_file_extension(file_path):
    """Get the file extension from a path."""
    _, ext = os.path.splitext(file_path)
    return ext.lower()


def get_allowed_extensions():
    """Get the set of file extensions to lint."""
    env_ext = os.environ.get("HOOKKIT_LINT_EXTENSIONS", "").strip()
    if env_ext:
        return {e.strip() for e in env_ext.split(",") if e.strip()}
    return DEFAULT_EXTENSIONS


def detect_linter(file_path):
    """Auto-detect the appropriate linter based on project files."""
    ext = get_file_extension(file_path)

    # Walk up from the file to find project root
    search_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # Max 10 levels up
        for config_file, command, extensions in LINTER_CONFIGS:
            if ext in extensions and os.path.exists(os.path.join(search_dir, config_file)):
                return command, search_dir
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent

    # Fallback by extension
    if ext == ".py":
        return "ruff check", None
    if ext in {".js", ".ts", ".jsx", ".tsx"}:
        return "npx eslint", None

    return None, None


def run_linter(command, file_path, cwd=None):
    """Run the linter on the given file."""
    full_command = f"{command} {file_path}"
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
        return result.stdout, result.stderr, result.returncode
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "", "", -1


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ("Edit", "Write"):
            return

        file_path = tool_input.get("file_path", "")
        if not file_path:
            return

        # Check if extension is lintable
        ext = get_file_extension(file_path)
        if ext not in get_allowed_extensions():
            return

        # Use custom linter or auto-detect
        custom_linter = os.environ.get("HOOKKIT_LINTER", "").strip()
        if custom_linter:
            command = custom_linter
            cwd = None
        else:
            command, cwd = detect_linter(file_path)

        if not command:
            return

        stdout, stderr, returncode = run_linter(command, file_path, cwd)

        # Report lint results if there were issues
        if returncode != 0 and (stdout or stderr):
            output = (stdout + "\n" + stderr).strip()
            # Truncate long output
            if len(output) > 500:
                output = output[:497] + "..."
            print(json.dumps({"lint_output": output}))

    except Exception:
        # Lint is best-effort — never break the agent workflow
        pass


if __name__ == "__main__":
    main()
