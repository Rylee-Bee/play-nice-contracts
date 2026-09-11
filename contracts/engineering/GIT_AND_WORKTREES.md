---
contract_id: git-and-worktrees
title: Git and Worktrees
version: 1.0.0
status: canonical
layer: engineering
applies: [engineering, agents, collaboration]
triggers: [git-work, parallel-work, agents, cleanup]
rationale: Git is durable coordination state, not just history. Deletion requires proof of staleness; shared checkouts are hazards; work in flight is preserved until proven stale.
---

<!-- contract-receipt: bramble-urnfield-inkstone -->

# Git and Worktrees

## Purpose

Treat Git as the coordination fabric for humans and agents working in parallel: worktrees for lanes, explicit staging for safety, and deletion only on proof of staleness.

## NORMATIVE RULES

1. Git is durable coordination state. Branches, worktrees, and dirty files answer "who owns what work in flight".
2. Rule of deletion:
   ```text
   PROVE STALE → CLEAN
   ```
   Never: `LOOKS STALE → DELETE`. Before deleting any worktree, checkout, or branch, inspect: active worktrees, dirty state, unique commits (ahead of all remotes), remote backup, merge status, active agent ownership. Ambiguous material is preserved.
3. Parallel workers use separate worktrees — one checkout per lane. Never run two lanes in the same directory.
4. Never `git add -A` in a shared checkout: it stages whatever else is in flight. Stage explicit paths only.
5. Active agent worktrees are read-only to other agents. No force pushing without explicit authority. Ambiguous state is escalated to the owner, never resolved by a guess.
6. Branch models are explicit and small (e.g. main / dev / feature): direct-commit rules, promotion paths, and merge authority are documented per repository, not folklore.
7. History is evidence: rewriting history is remediation of last resort, coordinated with the owner, and never silently performed by an agent.
8. Commit hygiene: signed where the repo requires it, atomic commits per logical change, messages that explain why (the diff already says what).

## RATIONALE

Two hard lessons: (1) a shared checkout let one agent's `git add -A` sweep another agent's WIP into an unrelated commit; (2) worktrees were nearly deleted that contained unmerged unique work. The "prove stale" rule and per-lane worktree discipline are the structural fixes — they make parallel human/agent work safe without relying on everyone remembering the hazard.

## HUMAN EXAMPLES

- Before pruning old worktrees, a script prints: dirty? unique commits? remote backing? — and refuses to delete anything ambiguous.
- Two agents on two lanes in `../proj-lane-a` and `../proj-lane-b` never see each other's partial state.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Safe-commit tooling: stage-by-path, preflight checks (detached HEAD, mid-merge/rebase, off-branch, dirty tree refuse-to-run).
- Cleanup tooling enumerates safety signals before deletion; `--force` exists but is loud and logged.
- Agent harness conventions mark worktree ownership (branch names, lock files, STATUS docs).

## GOOD EXAMPLES

```text
worktree ../pw-frontend-a: branch feature/frontend-shell
  dirty: 2 files (WIP, owner: agent-2)  → do not touch
worktree ../pw-old-lane: branch lane/finished-2026-08
  clean, merged, no unique commits, backed remotely → PROVEN STALE → safe to remove
```

## ANTI-PATTERNS

- `git add -A` then "oops, that committed someone's WIP".
- Deleting a branch/worktree because "it looked abandoned".
- Two agents in one checkout because "they're small tasks".
- Agent force-push "to clean up history".
- Rewriting history to hide a leaked secret instead of rotating it first.

## ACCEPTANCE CHECKS

- Does deletion of any work-in-flight artifact require proof of staleness?
- Is each lane isolated in its own worktree?
- Is staging path-explicit in shared contexts?
- Can current in-flight work be enumerated in one command?