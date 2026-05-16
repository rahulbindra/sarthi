#!/usr/bin/env bash
# Sarthi installer — run once in terminal, then open Claude Code and run /sarthi-setup
set -euo pipefail

REPO="https://github.com/rahulbindra/sarthi"
SKILLS="$HOME/.claude/skills"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"

echo "Installing Sarthi..."

if ! command -v git > /dev/null 2>&1; then
  echo "Error: git is required. Install it with: brew install git" >&2
  exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

git clone --depth 1 "$REPO" "$TMP/sarthi" 2>&1 | tail -1

mkdir -p "$SKILLS"
cp -r "$TMP/sarthi/skills/." "$SKILLS/"
echo "✓ Skills installed"

# Register each skill in CLAUDE.md idempotently
mkdir -p "$HOME/.claude"
touch "$CLAUDE_MD"
for skill_dir in "$TMP/sarthi/skills"/*/; do
  skill_name=$(basename "$skill_dir")
  skill_md="$skill_dir/SKILL.md"
  [ -f "$skill_md" ] || continue
  # Skip if already registered
  grep -qF "skills/$skill_name/SKILL.md" "$CLAUDE_MD" 2>/dev/null && continue
  desc=$(grep "^description:" "$skill_md" | head -1 | sed 's/^description:[[:space:]]*//')
  printf -- '- **%s** (`~/.claude/skills/%s/SKILL.md`) - %s. Trigger: `/%s`\n' \
    "$skill_name" "$skill_name" "$desc" "$skill_name" >> "$CLAUDE_MD"
done
echo "✓ Skills registered in CLAUDE.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Sarthi installed."
echo ""
echo "  Open Claude Code and run:  /sarthi-setup"
echo ""
echo "  Then restart Claude Code when setup finishes."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
