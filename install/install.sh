#!/usr/bin/env bash
# Install the saas-ai-audit skill into ~/.claude/skills/
# Usage: ./install/install.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$HOME/.claude/skills/saas-ai-audit"

echo "→ Target: $TARGET"

if [ -d "$TARGET" ]; then
  read -p "Skill already installed. Overwrite? [y/N] " confirm
  case "$confirm" in
    [yY]*) rm -rf "$TARGET" ;;
    *) echo "Aborted."; exit 0 ;;
  esac
fi

mkdir -p "$TARGET"
cp "$REPO_ROOT/skill/SKILL.md" "$TARGET/"
cp "$REPO_ROOT/skill/themes.json" "$TARGET/"
cp "$REPO_ROOT/skill/audit_xlsx.py" "$TARGET/"

echo "✓ Skill installed to $TARGET"
echo
echo "Check Python + openpyxl are installed:"
echo "  python3 --version"
echo "  python3 -c 'import openpyxl; print(openpyxl.__version__)'"
echo
echo "If openpyxl is missing: pip install openpyxl"
echo
echo "Then in Claude Code, type: /saas-ai-audit"
