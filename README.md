# muse-skills backup

A day-by-day history of the skill collection shipped with this Muse
container (`/opt/hatch/skills`) — built-in skills only — snapshotted daily. The newest commit is always
the current state.

## How it works
A scheduled daily job runs `backup.sh`:
1. Mirrors `/opt/hatch/skills` into `skills/` (dereferenced by default,
   so SKILL.md files are real and restorable — unlike a symlink-only mirror)
3. Excludes build output (`dist/`, `node_modules/`, `*.tgz`)
4. Commits only if something changed, then pushes

## Unofficial
Independent backup / change-tracking. Not affiliated with Meta.
