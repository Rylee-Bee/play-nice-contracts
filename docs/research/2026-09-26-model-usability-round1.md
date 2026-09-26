# Model usability test, round 1 (2026-09-26)

> **Status:** Historical · evidence for the v2 fixes in the same release.

Seven models, same task, each in its own copy of a small app ("Garden Notes")
with the v2 library vendored: find the rules that apply, prove you read
them, add a settings page and API endpoint following them, hand off, and
write a friction report.

| Model | Proof line | Unsafe HTML fixed | Tests | Reported old problems (status / 404 / states) | Read before starting | Friction items |
|---|---|---|---|---|---|---|
| deepseek-v4-pro | yes | yes | pass | yes / no / no | ~6,500 words | 30 |
| deepseek-v4.1-flash | yes | yes | pass | yes / yes / no | ~2,200 | 13 |
| qwen3.8-max | yes | yes | pass | yes / yes / yes | ~4,000 | 14 |
| qwen3.8-flash | yes | yes | pass | yes / yes / yes | ~17,000 | 10 |
| mimo-v2.6-pro | yes | yes | pass | yes / yes / yes | unstated | 34 |
| mimo-v2.6-flash | yes | yes | pass | yes / yes / yes | ~2,200 | 28 |
| minimax-m3 | yes | yes | pass | no / yes / yes | ~2,500 | 12 |

Scoring was automated and approximate (grep over each tester's code and
reports).

## What they agreed on (and the fix in this release)

| Friction | Testers | Fix |
|---|---|---|
| README linked a missing floor path, taught the retired gate, said 68 contracts | 6/6 | README rewritten; maintainer material moved to docs/MAINTAINING.md |
| `playnice verify` / `check` named but missing | 6/6 | Added (`tools/playnice`) |
| AGENTS.md and QUICK_REFERENCE stale | 4/6 | AGENTS.md marked maintainers-only; QUICK_REFERENCE points at the floor |
| `resolve` required a manifest; keyword matching brittle | 5/6 | Manifest-free resolve with role base sets; triggers fixed |
| `init-adoption` / `onboard` taught retired ids and flow | 3/6 | Templates and onboarding on v2 |
| Proof-line grammar unclear | 4/6 | Grammar in contract-proof Machine notes |
| Rules didn't scale down to a tiny local app | 2/6 | Scale-down notes in api and friendly-site |
| Version muddle | 3/6 | Library 2.0.0 |

Two complaints were about the test harness, not the library (its brief said
both "commit" and "commit nothing"; the app lacked a .gitignore).
