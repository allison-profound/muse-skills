# muse-skills backup

A day-by-day history of the skill collection shipped with this Muse
container (`/opt/hatch/skills`) — built-in skills only — snapshotted daily. The newest commit is always
the current state.

## How it works
A scheduled daily job runs `backup.sh`:
1. Mirrors `/opt/hatch/skills` into the repo root (dereferenced)
2. Excludes build output (`dist/`, `node_modules/`, `*.tgz`)
3. Commits only if something changed, then pushes

## Unofficial
Independent backup / change-tracking. Not affiliated with Meta.
