#!/usr/bin/env bash
# Daily snapshot of built-in Muse skills -> git -> GitHub
# Layout: skills at the REPO ROOT (flattened 2026-10-22), dereferenced,
# so SKILL.md files are real, readable and restorable outside a container.
set -euo pipefail
SRC="/opt/hatch/skills"
REPO="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO"

# --- Guardrails: --delete at the repo root is only safe in the right place.
# Refuse to run unless this really is the muse-skills backup checkout.
[ -d .git ] || { echo "ABORT: no .git in $REPO" >&2; exit 1; }
git remote get-url origin 2>/dev/null | grep -q 'allison-profound/muse-skills' \
  || { echo "ABORT: unexpected origin: $(git remote get-url origin 2>&1)" >&2; exit 1; }
[ -f README.md ] && [ -f backup.sh ] \
  || { echo "ABORT: repo tooling files missing in $REPO" >&2; exit 1; }

# Tooling that must survive --delete at root. rsync excludes are also
# delete-protected (we do NOT use --delete-excluded).
TOOLING_EXCLUDES=(
  --exclude='.git/'
  --exclude='README.md'
  --exclude='backup.sh'
  --exclude='.gitignore'
  --exclude='.backup-tooling/'
)

# Real files, so the repo is restorable outside a Muse container.
# rsync -L follows symlinks to /opt/muse/skills and /opt/hatch/connectors.
# Excludes match upstream .gitignore intent: build output is not versioned.
rsync -aL --delete --ignore-errors \
  "${TOOLING_EXCLUDES[@]}" \
  --exclude='dist/' --exclude='node_modules/' --exclude='*.tgz' \
  --exclude='__pycache__/' --exclude='.DS_Store' \
  "$SRC/" ./ || [ $? -eq 23 ]  # 23 = dangling symlinks in upstream, expected

git add -A
if git diff --cached --quiet; then
  echo "No changes — nothing to commit."
  exit 0
fi

DATE="$(date -u +%F)"
CHANGED="$(git diff --cached --stat | tail -1)"
# Agent cron fills in a human analysis of the diff before pushing when run
# via Muse; a plain shell run uses this factual fallback.
MSG="${COMMIT_MSG:-skills snapshot $DATE

$CHANGED}"
git -c user.name="file-integrity" -c user.email="file-integrity@local" commit -m "$MSG"
[ -n "${SKIP_PUSH:-}" ] || git push origin HEAD
echo "Committed: $MSG"
