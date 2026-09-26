---
contract_id: status-and-state
title: Status and State
version: 2.0.0
status: canonical
layer: everyone
applies: [ui, api, cli, agents, services, tools, automation]
triggers: [status, state, error, failure, health, dashboard, monitoring, degradation, outage]
rationale: One shared status vocabulary and honest errors let people and machines tell broken from not-set-up from not-checked without guessing.
---

<!-- contract-receipt: sedge-harbor-porch -->

# Status and State

## In short

Report state with the shared status words, never silence or guesswork.
Failures say what broke, what still works, and what to do next.

## Applies when

You build or change anything that shows, logs, or returns a state: screens,
APIs, CLIs, agents, services. Not this contract's job: what counts as
evidence (see truth-and-evidence) or undo paths (see recovery-and-history).

## Rules

1. **Use the shared words, only these:** healthy, warning, needs_attention,
   degraded, unavailable, not_configured, disabled, stale, unknown,
   working, waiting, blocked, deferred, partial, complete. The schema is
   the source (schema/status.schema.json); map provider states into these
   at your boundary. (MUST)
2. **Keep the distinctions.** unavailable ≠ not_configured; unknown ≠
   healthy; stale ≠ current; disabled ≠ failed; working ≠ complete. Never
   collapse two words into one screen state. (MUST)
3. **Every state names its age and source.** A status carries when it was
   observed and where from; data too old to trust shows as stale, not as
   current. Nothing checked means unknown, not healthy (see the floor,
   rule 8). (MUST)
4. **In-progress work says so.** Long operations expose working, waiting,
   or blocked instead of freezing or silently continuing. (MUST)
5. **Composite states stay honest.** When parts differ, show the mix
   ("degraded, two of five providers unreachable"), never a misleading
   average. Define the worst-wins order once, in the vocabulary module.
   (MUST)
6. **Human views may translate the words, not the meaning.** "Everything
   looks good" suits healthy; the machine view underneath keeps the shared
   word. (SHOULD)
7. **One part's failure stays its own.** An optional dependency going down
   degrades that capability; it must not blank unrelated features, corrupt
   state, or hang the whole surface. (MUST)
8. **Errors say, in this order:** what happened; what changed and what
   didn't; what still works; whether anything is unsafe; whether it can be
   retried; the next reasonable action; where the technical detail lives.
   Errors support recovery, not blame — never blame the person. (MUST)
9. **Stable machine error names; useful human words.** Surfaces return
   identifiers like provider_unreachable or not_authorized with a
   retryability flag; human views translate them. A meaningful error is
   never flattened to "Something went wrong." (MUST)
10. **Multi-item operations report per item.** When 2 of 7 saves failed,
    say which 5 worked and why those 2 didn't. (MUST)
11. **No fake success.** A swallowed error is a defect, whatever its
    short-term convenience. (MUST)
12. **Degraded stays inspectable.** The degraded state, its reason, and
    its last verified point are visible, not guessed. (SHOULD)

## Examples

- Good: `{"status": "needs_attention", "observed_at":
  "2026-09-11T14:00:00Z", "source": "provider-probe", "detail":
  "certificate expires in 2 days"}`
- Good: a provider outage renders its row unavailable, "last seen 2h
  ago"; every other row keeps working.
- Bad: a red "error" for a feature nobody configured, and a spinner that
  stays ten minutes with no intermediate state.

## Why

One closed vocabulary lets a UI, a CLI, an API and an agent tell the same
truth about the same state. Real outages showed both failure modes: one
dead integration blanked an entire dashboard, and readers had to guess
whether no news meant good news.

## You're done when

- Every status string a surface emits is on the shared list (diff it
  against schema/status.schema.json).
- A newcomer can tell "broken" from "not set up" from "not checked" on
  every surface you changed.
- You killed one dependency on purpose and everything unrelated kept
  working and said so.
- Every error path was run once, returned a stable identifier, and
  answered all of rule 8.

## Machine notes

Error envelope, uniform across surfaces: `error` (stable id) + structured
context + `retryable` flag + `still_works` + `next`. Status composition
("worst wins") is ordered once, in the shared vocabulary module, never
re-derived per surface.
