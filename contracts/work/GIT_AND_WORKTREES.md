---
contract_id: git-and-worktrees
title: Git and Worktrees
version: 2.0.0
status: canonical
layer: work
applies: [agents, humans, tools, automation]
triggers: [git, branch, branches, worktree, checkout, commit, push, merge, rebase, stash, cleanup, prune, delete branch]
rationale: Branches and worktrees record who owns which work in flight, so parallel work stays safe and nothing real is deleted on a guess.
---

<!-- contract-receipt: umber-reed-slate -->

# Git and Worktrees

## In short

Git is coordination, not just history: one branch per purpose, one
worktree per lane, explicit staging. Delete nothing until it's proven
stale — never because it looks stale.

## Applies when

Committing, branching, running parallel work in a repo, or cleaning up
worktrees and branches. Asking before hard-to-undo actions is the
floor (rule 6); here is the git-specific shape of that.

## Rules

1. One branch per purpose. The branch model — what may be committed
   where, how branches promote, who may merge — is documented in the
   repository, not folklore.
2. Parallel work uses one worktree per lane. Two people or agents
   never share a checkout while both are mutating. (MUST)
3. Another agent's active worktree is read-only to you. Its dirty
   files are its in-progress thought, not debris.
4. Stage explicit paths. Never `git add -A` in a shared checkout: it
   sweeps in whatever else is in flight. (MUST)
5. Prove stale, then clean. Before deleting any worktree, checkout, or
   branch, check: active worktrees, dirty files, commits that exist on
   no remote, remote backup, merge status, active owners. Ambiguous
   material is kept and escalated, never deleted on a guess. (MUST)
6. Force-pushes, history rewrites, and branch deletes happen only with
   explicit authority, coordinated with the owner — never silently by
   an agent. If history hides a leaked secret, rotate the secret
   first; rewriting never replaces rotation.
7. Push and merge authority come from the task packet. If the task
   didn't grant it, the agent doesn't have it.
8. Commit hygiene: one logical change per commit, a message that says
   why (the diff already says what), signed where the repo requires
   signatures.
9. In-flight work stays enumerable: current branches, worktrees, and
   their owners can be listed in one command or one status file.

## Examples

- Good: a cleanup script prints per worktree — dirty? unique commits?
  remote-backed? merged? — and refuses to remove anything ambiguous.
- Good: two lanes at `../proj-lane-a` and `../proj-lane-b`, each with
  its own checkout, never seeing each other's partial state.
- Bad: `git add -A`, then discovering the commit contains another
  agent's half-finished work.

## Why

Two hard lessons built these rules: a shared checkout let one `git add
-A` commit sweep a colleague's work-in-progress into an unrelated
change, and worktrees holding unmerged unique work nearly got deleted
for looking old. Proof-based cleanup and per-lane worktrees make
parallel work safe without everyone having to remember the hazard.

## You're done when

- Every lane has its own worktree, and no deletion of in-flight
  material happened without a proven-stale check.
- `git add -A` does not appear in shared-context workflows.
- Branch/worktree ownership is visible in one command or file.
- History was never rewritten by an agent without named authority.
