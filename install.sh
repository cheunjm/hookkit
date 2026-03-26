#!/usr/bin/env bash
#
# hookkit installer
# Usage: ./install.sh [hook-name ...]
# Example: ./install.sh guard-branch notify-stop
#

set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)/hooks"
INSTALL_DIR="${HOME}/.claude/hooks"

# Hook registry: name -> hook type -> matcher
declare -A HOOK_TYPES=(
    ["guard-branch"]="PreToolUse"
    ["dangerous-command-guard"]="PreToolUse"
    ["notify-stop"]="Stop"
    ["lint-on-edit"]="PostToolUse"
)

declare -A HOOK_MATCHERS=(
    ["guard-branch"]="Edit|Write|NotebookEdit|Bash"
    ["dangerous-command-guard"]="Bash"
    ["notify-stop"]=""
    ["lint-on-edit"]="Edit|Write"
)

list_hooks() {
    echo "Available hooks:"
    echo ""
    printf "  %-28s %-14s %s\n" "NAME" "TYPE" "FILE"
    printf "  %-28s %-14s %s\n" "----" "----" "----"
    for hook in "${!HOOK_TYPES[@]}"; do
        if [[ -f "${HOOKS_DIR}/${hook}.py" ]]; then
            printf "  %-28s %-14s %s\n" "$hook" "${HOOK_TYPES[$hook]}" "hooks/${hook}.py"
        fi
    done
    echo ""
    echo "Usage: ./install.sh <hook-name> [hook-name ...]"
    echo "Example: ./install.sh guard-branch notify-stop"
}

install_hook() {
    local hook_name="$1"
    local source="${HOOKS_DIR}/${hook_name}.py"
    local dest="${INSTALL_DIR}/${hook_name}.py"

    if [[ ! -f "$source" ]]; then
        echo "Error: Hook '${hook_name}' not found at ${source}"
        return 1
    fi

    mkdir -p "$INSTALL_DIR"
    cp "$source" "$dest"
    chmod +x "$dest"
    echo "Installed: ${dest}"
}

print_registration() {
    local hook_name="$1"
    local hook_type="${HOOK_TYPES[$hook_name]}"
    local matcher="${HOOK_MATCHERS[$hook_name]}"

    echo ""
    echo "Add this to your ~/.claude/settings.json under \"hooks\":"
    echo ""
    echo "  \"${hook_type}\": ["
    echo "    {"
    if [[ -n "$matcher" ]]; then
        echo "      \"matcher\": \"${matcher}\","
    else
        echo "      \"matcher\": \"\","
    fi
    echo "      \"hooks\": ["
    echo "        {"
    echo "          \"type\": \"command\","
    echo "          \"command\": \"python3 ~/.claude/hooks/${hook_name}.py\""
    echo "        }"
    echo "      ]"
    echo "    }"
    echo "  ]"
}

# Main
if [[ $# -eq 0 ]]; then
    list_hooks
    exit 0
fi

echo "hookkit installer"
echo "================="
echo ""

for hook_name in "$@"; do
    if [[ ! -v "HOOK_TYPES[$hook_name]" ]]; then
        echo "Error: Unknown hook '${hook_name}'"
        echo "Run ./install.sh with no arguments to see available hooks."
        exit 1
    fi

    install_hook "$hook_name"
    print_registration "$hook_name"
    echo ""
done

echo "Done. Remember to add the registration snippets to ~/.claude/settings.json"
