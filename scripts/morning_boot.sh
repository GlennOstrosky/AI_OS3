#!/usr/bin/env bash
# Morning Boot Check (OS3)
# Purpose: Restore confidence without execution risk

echo "🌅 OS3 Morning Boot"
echo "===================="
echo ""

# 1. Covenant check
if [ -f "COVENANT.md" ]; then
  echo "✅ COVENANT.md present"
else
  echo "⚠️  COVENANT.md missing"
fi

# 2. Canon check
if [ -d "canon" ]; then
  canon_count=$(ls canon/*.md 2>/dev/null | wc -l)
  echo "✅ canon/ exists ($canon_count entries)"
else
  echo "⚠️  canon/ missing"
fi

# 3. Scripts check
if [ -d "scripts" ]; then
  script_count=$(ls scripts/*.sh 2>/dev/null | wc -l)
  echo "✅ scripts/ exists ($script_count scripts)"
else
  echo "⚠️  scripts/ missing"
fi

# 4. Git status
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo "✅ Git repository active"
  branch=$(git branch --show-current)
  echo "   Branch: $branch"
else
  echo "⚠️  Not a git repository"
fi

echo ""
echo "🔥 Boot check complete. Ready for covenant work."
echo "   Next: doctor, share, or canon update"
