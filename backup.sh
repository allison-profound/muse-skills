#!/usr/bin/env bash
# Daily snapshot of Muse skills -> git -> GitHub
# Mode: dereferenced (default, usable backup) or faithful (obra-style symlinks)
set -euo pipefail
MODE="${MODE:-dereferenced}"   # dereferenced | faithful
SRC="/opt/hatch/skills"
REPO="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO"

# Keep our tooling out of the snapshot itself
mkdir -p .backup-tooling
cp -f backup.sh .backup-tooling/ 2>/dev/null || true

if [ "$MODE" = "dereferenced" ]; then
  # Real files, so the repo is restorable outside a Muse container.
  # rsync -L follows symlinks to /opt/muse/skills and /opt/hatch/connectors.
  # Excludes match upstream .gitignore intent: build output is not versioned.
  rsync -aL --delete \
    --exclude='.git/' --exclude='.backup-tooling/' \
    --exclude='dist/' --exclude='node_modules/' --exclude='*.tgz' \
    --exclude='__pycache__/' --exclude='.DS_Store' \
    "$SRC/" ./skills/ || [ $? -eq 23 ]  # 23 = dangling symlinks in upstream, expected
else
  rsync -a --delete \
    --exclude='.git/' --exclude='.backup-tooling/' \
    "$SRC/" ./skills/
fi

# Your own work — the part that is NOT shipped upstream
rsync -a --delete --exclude='.git/' ~/workspace/custom-skills/ ./custom-skills/ 2>/dev/null || mkdir -p custom-skills
rsync -a --delete --exclude='.git/' ~/workspace/custom-connectors/ ./custom-connectors/ 2>/dev/null || mkdir -p custom-connectors

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
echo "Pushed: $MSG"
