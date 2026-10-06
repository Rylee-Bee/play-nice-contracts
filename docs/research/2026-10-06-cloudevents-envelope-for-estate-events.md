Research only. No broker or runtime dependency.

# CloudEvents envelope + OpenTelemetry context for estate events

Study for Rylee-Bee/play-nice-contracts#55. Envelope first, transport later.

- Clone examined: `Rylee-Bee/play-nice-contracts` at HEAD
  `a11563b1ab8e5fe4fd235d04972de062a93376eb`
  (`a11563b` "docs: point .project/CURRENT.md at the live Now block (#53)").
- The clone is shallow: `git rev-parse --is-shallow-repository` returns `true`
  and `git log --oneline | wc -l` returns `1`. Every claim about earlier
  receipt work below therefore rests on `CHANGELOG.md` and the code, not on
  commit history. Claims that need history are marked UNVERIFIED.
- No file other than this document was changed. The prototype script and the
  fetched specification files were scratch under `tools/ce-proto/` and are not
  committed, because the issue permits exactly one deliverable file.

## Summary

Every estate event this clone can actually observe already has a stable JSON
shape with its own vocabulary, its own timestamp field and its own source
field, and none of them carries a correlation id.
The identity fields these events carry name the entity an event is about, not the chain of actions that produced it, so they are not a correlation id.
A CloudEvents 1.0 envelope maps onto
all three prototype events cleanly and validates with zero errors against
the published CloudEvents JSON Schema, so the technology works; the question is
whether it removes anything. Of the six extensions the issue asks about, three
are already covered by standard CloudEvents attributes and two are already
covered by existing local vocabulary, leaving exactly one worth adopting
(`traceparent`/`tracestate`). Inside a single repository where producer and
consumer are the same process, a CloudEvents envelope adds a decode step to
every existing consumer and retires no adapter. No demonstrated replay,
fan-out or offline-delivery problem exists in the evidence available in this
clone, so no broker is justified either — REJECT.

## The rule this study answers

Rylee, 2026-10-06, verbatim:

> The success criterion is not 'the product works.' Their success criterion is:
> What existing estate machinery becomes simpler, standardized, smaller, or
> unnecessary? If a technology adds another service but removes no meaningful
> complexity, recommend rejection. And: The preferred result is fewer concepts
> and less custom plumbing. A successful evaluation may conclude that the
> technology should not be adopted. If nothing meaningful becomes simpler or
> disappears, default toward rejection.

The issue's own principle, verbatim:

> Envelope first. Transport later. NATS JetStream is a transport and storage
> candidate, not the contract. Do not deploy NATS as part of this issue.

And its decision rule, verbatim:

> Adopt a common envelope if it removes bespoke adapters between at least three
> real producers and consumers. Adopt a broker only if replay, fan-out or
> offline delivery solve demonstrated problems that direct calls and current
> durable state do not.

Both tests are applied below. Neither is met.

## Estate event inventory

Columns are the seven the issue names, plus the event name. "Owner" means the
system that answers "what is true now" about the thing the event is about — not
the system that emitted the message.

| Event | Canonical owner | Current producer | Current consumers | Delivery requirement | Replay requirement | Sensitivity | Event or durable state? |
|---|---|---|---|---|---|---|---|
| mission started | Project Home (UNVERIFIED — no artifact in this clone) | Project Home (UNVERIFIED) | human status surfaces | at-most-once notification is enough | none shown | internal | durable state (the mission record); the notification is an event |
| mission finished | Project Home (UNVERIFIED) | Project Home (UNVERIFIED) | humans, reports | at-most-once | none shown | internal | durable state + one event |
| mission failed | Project Home (UNVERIFIED) | Project Home (UNVERIFIED) | humans, alerts | must not be dropped; needs a person's attention (`contracts/people/ATTENTION_AND_QUIET.md` rule 1) | the failure reason belongs in the mission record, not the message | internal | durable state + one event |
| task claimed | Project Home (UNVERIFIED) | Project Home (UNVERIFIED) | the claiming worker | must not be double-delivered; the claim itself must be exclusive | none — an exclusive claim is state, not a broadcast | internal | **durable state, not an event.** Broadcasting "task claimed" cannot make a claim exclusive; only the owner can |
| task released | Project Home (UNVERIFIED) | Project Home (UNVERIFIED) | waiting workers | at-most-once notification; consumers must re-read the task before acting (`contracts/integration/EVENTS_AND_CACHING.md` rule 7) | none | internal | durable state + one event |
| approval requested | the asker/owner record; schema owned here at `schema/question.schema.json` | any participant, via the `play-nice/question-v1` family | the target participant | must persist across sessions — the schema states a question is "resumable workflow state" | **yes, within the artifact**: `status` moves OPEN → ANSWERED/DECLINED/EXPIRED, so the object is state and its transitions are events | internal; `secrets_policy` is `const: "excluded"` | durable state that already has an envelope |
| approval decided | same artifact | the answering participant | the asker, the audit trail | at-most-once | the decision is the artifact's new `status` plus `answered_by`/`answered_at`/`answer_kind` | internal | durable state + one event |
| CI run started | GitHub Actions (`.github/workflows/ci.yml` job `library`) | GitHub Actions | the merge gate waits on job name `library` via `library-gate` | durable until the run completes | not needed: a run in progress is re-readable from the run list | public (workflow is committed) | durable state + one event |
| CI run finished | GitHub Actions | GitHub Actions | the `library-gate` job, the PR page, humans | must not be dropped; it is the merge condition | not needed: the run's conclusion is durable at the source | public | durable state + one event |
| PR merged | the git remote of `Rylee-Bee/play-nice-contracts` | the merge itself | `tools/playnice/playnice.py:collect_github_state` and `reconcile_github` | at-most-once; consumers re-read the branch state | none — the merge is replayable from git history itself | public | durable state + one event |
| receipt emitted | the contract library (`contracts/everyone/FLOOR.md`) | `tools/playnice/playnice.py:run_repo_check` (called from `cmd_check`) | the bee badge, `README.md`, `AGENTS.md`, an agent's receipt line | at-most-once; the receipt is re-derivable by re-running the check | none — `playnice check` re-derives it from the library every time | public | an event, and a **deterministic function** of the library, not state at all |
| BOOP attention created | BOOP (UNVERIFIED — the string "BOOP" does not occur anywhere in this clone; verified with `grep -rni "boop" .` returning nothing outside `.git`) | BOOP (UNVERIFIED) | humans | must reach a person; batched (`ATTENTION_AND_QUIET.md` rule 5) | the attention item is durable at the owner | personal — see `contracts/access/PUBLIC_AND_PRIVATE.md` rule 9 | durable state + one event |
| service health changed | the thing observed — here, the git remote and the local checkout | `tools/playnice/playnice.py:cmd_status` via `collect_repo_state` | humans, status surfaces, the merge decision | at-most-once; must never cache success (`contracts/work/OBSERVABILITY.md` rule 8) | **no replay** — the contract requires re-observing the live source (`contracts/everyone/TRUTH_AND_EVIDENCE.md` rule 5) | internal | an event; the truth stays with the observed system |

Read across the table, the pattern is that **most of these are durable state
wearing an event's clothes**. Four of thirteen (`task claimed`, the approval
lifecycle, the CI run, the BOOP attention item) are state that changes over
time; one (`receipt emitted`) is a pure function of a file. Only
`service health changed` is a genuine notification whose value lies in not
having to re-read the source — and even that is re-derived by re-reading the
source today, in under a second, by design.

The `task claimed` row is the one that matters most for the envelope question.
An envelope cannot make a claim exclusive. Nothing in the transport can. Only
the owner's atomic compare-and-set can. Emitting `task.claimed` on a bus and
then treating the bus as the arbiter is exactly the failure
`contracts/integration/EVENTS_AND_CACHING.md` rule 7 forbids — "Treat a webhook
payload as a notification, not as truth: re-read the source before any
consequential action."

## The proposed envelope

### Shape

CloudEvents 1.0 structured mode, plus one required data object described by a
schema the `dataschema` attribute names. The standard attributes already cover
identity, time, kind and schema; nothing needs to be added to them.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "play-nice/estate-event-v1",
  "title": "Play-Nice Estate Event data",
  "description": "The data payload of a play-nice CloudEvent. Holds only what the event reports. It never holds mutable truth: the owner of the fact answers what is true now, not this message.",
  "type": "object",
  "required": ["schema", "observed_at", "source", "detail"],
  "additionalProperties": true,
  "properties": {
    "schema": { "const": "play-nice/estate-event-v1" },
    "status": {
      "$ref": "play-nice/status-v1",
      "description": "A word from schema/status.schema.json, mapped from the producer's own vocabulary at the boundary (STATUS_AND_STATE.md rule 1). Never a provider word."
    },
    "provider_words": {
      "type": "object",
      "description": "The producer's own words, kept beside the mapped word so the mapping stays auditable and reversible.",
      "additionalProperties": { "type": "string" }
    },
    "observed_at": {
      "type": "string",
      "format": "date-time",
      "description": "When this was seen (OBSERVABILITY.md rule 8)."
    },
    "source": {
      "type": "string",
      "description": "The command or surface that produced it (EVENTS_AND_CACHING.md machine notes)."
    },
    "detail": { "type": "string", "maxLength": 2000 },
    "actor": {
      "type": "object",
      "description": "Who acted, reusing the participant shape schema/question.schema.json already defines.",
      "required": ["type"],
      "additionalProperties": false,
      "properties": {
        "type": { "enum": ["human", "agent", "orchestrator", "worker", "service", "api", "tool", "automation"] },
        "id": { "type": ["string", "null"], "maxLength": 80 },
        "role": { "type": ["string", "null"], "maxLength": 80 }
      }
    },
    "task_id": { "type": ["string", "null"], "maxLength": 64 },
    "mission_id": { "type": ["string", "null"], "maxLength": 64 },
    "receipt_word": { "type": ["string", "null"], "maxLength": 64 },
    "receipt_line": { "type": ["string", "null"], "maxLength": 200 },
    "sensitivity": {
      "enum": ["public", "internal", "restricted", null],
      "description": "From PUBLIC_AND_PRIVATE.md rule 1 (publishable or private) and the floor's rule 11 (secrets never in messages)."
    },
    "evidence": {
      "type": "array",
      "items": { "type": "string", "maxLength": 300 },
      "description": "References only, the shape schema/references.schema.json already uses. No inline payloads, no secret values."
    },
    "truth_owner": {
      "type": "string",
      "description": "The system that answers what is true now. Required whenever this event reports an observation."
    }
  }
}
```

The `$ref: "play-nice/status-v1"` points at `schema/status.schema.json` in this
repo, unmodified. That is the whole point of the reuse: the envelope adds a
transmission format, and adds no vocabulary.

### Extension attributes, and why each exists or does not

The issue names six extension candidates. Here is what each one becomes.

| Issue's candidate | Decision | Where it lives | Why |
|---|---|---|---|
| World Tree role ID | **no new extension** | `data.actor.role` | `schema/question.schema.json` `$defs/participant` already defines `{type, id, role}` and is already the repo's participant shape. A second attribute for the same three facts is the custom plumbing the rule tells us to remove. Whether a "World Tree role id" is the same string as this `role` field is **UNVERIFIED** — no World Tree artifact exists in this clone. |
| receipt and provenance reference | **no new extension; one standard extension, optional** | `data.receipt_word`, `data.receipt_line`, `data.evidence[]`, and the standard `dataref` attribute for the artifact location | The receipt is already a deterministic function of the library, re-derived by `playnice check` on every run; it needs a field, not an extension. Provenance by reference is already the repo's shape (`schema/references.schema.json` uses `export`, `provenance.observed_at`, `provenance.method`). `dataref` is the claim-check pattern and is only worth carrying when the payload is large; in all three prototype events it points at a badge SVG. |
| Project Home task and mission correlation | **no new extension** | `data.task_id`, `data.mission_id`, and the standard `subject` attribute for the entity the event is about | CloudEvents' own Correlation extension (`correlationid`, `causationid`) exists, but the extensions index states these "have no official standing and might be changed, or removed, at any time." Two ids in `data`, reused from whatever Project Home already has, cost fewer concepts than an unstable attribute that also duplicates them. The Project Home id shape is **UNVERIFIED** — no Project Home artifact exists in this clone. |
| W3C trace context | **adopt, the only extension taken** | standard `traceparent` (+ optional `tracestate`) from the CloudEvents Distributed Tracing extension | This is the one with a real external standard behind it: W3C Trace Context, Recommendation 23 November 2021. `contracts/work/OBSERVABILITY.md` rule 3 already requires "a correlation or request id across services so one action can be followed from surface to dependency and back", and no such id exists anywhere in this repo — `grep -rni "traceparent\|trace_id\|opentelemetry\|otel"` returns nothing. This is a genuine gap, and the extension fills exactly that gap with a name everyone already knows. |
| schema and version | **no extension needed at all** | standard `dataschema` + `specversion` | The standard attributes already say which schema the data follows and which spec version produced the envelope. Proposing an extension here would add a second, competing way to say the same thing. |
| safe authority classification | **no extension; one required data field** | `data.sensitivity` | CloudEvents' Data Classification extension defines `dataclassification` with recommended labels `public`/`internal`/`confidential`/`restricted` and a `dataregulation` field. Adopting it would import GDPR-flavoured vocabulary on top of a library whose own rule is "one recorded status: publishable, or private" (`PUBLIC_AND_PRIVATE.md` rule 1). If cross-organisation classification ever becomes a real requirement, borrow that attribute's *name* then; do not pre-import its vocabulary now. |

Net result: **one extension adopted, one optional, zero new concepts.** Five of
the six candidates are already answered by a standard CloudEvents attribute or
by vocabulary this repo already owns and version-controls.

One caution that applies to all of them: the CloudEvents extensions index says
extension attributes "have no official standing and might be changed, or
removed, at any time," and the CloudEvents NATS protocol binding is still
labelled `1.0.3-wip`. Only `traceparent`/`tracestate` survives that caveat,
because it is not really a CloudEvents extension at all — it is a W3C header
that CloudEvents merely carries.

## Three real example mappings

Produced by `tools/ce-proto/ce_map.py`, a scratch stdlib-only script (not
committed — this issue permits one file change). Each mapping invokes the
repo's own CLI or the repo's own gate commands as a subprocess and reads what
they actually printed. Nothing is simulated.

The mapping logic, for reproduction:

```python
# service health changed
rc, out, _ = run([sys.executable, "tools/playnice/playnice.py", "status", "--json", "--no-github"])
raw = json.loads(out)
# STATE_MAP: CURRENT->healthy, BEHIND->stale, DIVERGED->degraded, UNKNOWN/NO_REMOTE->unknown
# provider words are kept beside the mapped word so the mapping stays auditable

# receipt emitted
rc, out, _ = run([sys.executable, "tools/playnice/playnice.py", "check", ".", "--json"])
raw = json.loads(out)
receipt_word = re.search(r"<!--\s*contract-receipt:\s*([a-z0-9-]+)\s*-->",
                         Path("contracts/everyone/FLOOR.md").read_text()).group(1)

# CI run finished: the three commands .github/workflows/ci.yml job `library` runs
for name, args in [("validate", [contractctl, "validate"]),
                   ("tests",    [sys.executable, "-m", "pytest", "tests/", "-q"]),
                   ("scan",     [contractctl, "scan"])]:
    rc, out, _ = run(args)   # real exit code, real last line of real output
```

### Example 1 — `playnice.service.health.changed`

Exact command:

```
python3 tools/ce-proto/ce_map.py health > tools/ce-proto/out-health.json
```

Observed output:

```json
{
  "data": {
    "detail": "remote refs/heads/main is 36cbccecbb89; no proven fast-forward from the adopted revision e570e2630702",
    "dirty": true,
    "head": "a11563b1ab8e5fe4fd235d04972de062a93376eb",
    "library_revision": "a11563b1ab8e5fe4fd235d04972de062a93376eb",
    "observed_at": "2026-10-06T12:07:09Z",
    "provider_words": { "play_nice": "DIVERGED", "repository": "DIRTY" },
    "remote_revision": "36cbccecbb89e6702b220fed0ab8d1fa3266438f",
    "source": "playnice status --json --no-github",
    "status": "degraded",
    "truth_owner": "git remote of Rylee-Bee/play-nice-contracts"
  },
  "datacontenttype": "application/json",
  "dataschema": "play-nice/estate-event-v1",
  "id": "2026-10-06T12:07:09Z-081623306390",
  "source": "urn:play-nice:source:playnice-cli",
  "specversion": "1.0",
  "subject": "Rylee-Bee/play-nice-contracts",
  "time": "2026-10-06T12:07:09Z",
  "traceparent": "00-00000000000000002bc77572b00b9492-064110c73db882f0-01",
  "type": "playnice.service.health.changed"
}
```

Two things worth reading closely. First, `dirty: true` is real: at mapping time
the untracked prototype scratch made the working tree dirty, and the envelope
reported it rather than hiding it — which is what `observed_at` plus `source`
are for. Second, `status: "degraded"` is the mapped word; `DIVERGED` and
`DIRTY` are the producer's own words, kept beside it rather than replacing it.

This mapping also exposed a **real defect the envelope does not fix**:
`playnice check` emits `worked`, `needs_fix` and `skipped`
(`tools/playnice/playnice.py:_check_item`, line 2500), and none of those three
is on the shared vocabulary in `schema/status.schema.json`. That is a violation
of `contracts/everyone/STATUS_AND_STATE.md` rule 1 ("Use the shared words, only
these") and of the floor's rule 8. `tests/test_status_words.py` checks the three
Markdown copies against the schema, not the CLI's emitted strings — so the test
suite is green while the tool diverges. Wrapping this in an envelope would give
the wrong words a standard transport and make the violation harder to see. The
fix is one `STATE_MAP` at the CLI boundary, which is exactly what the prototype
mapping does; it is a one-line-in, one-line-out fix that needs no envelope.

### Example 2 — `playnice.contract.receipt.emitted`

Exact command:

```
python3 tools/ce-proto/ce_map.py receipt > tools/ce-proto/out-receipt.json
```

Observed output:

```json
{
  "data": {
    "behind": false,
    "checks": [
      { "fix": "playnice start", "id": "agents-file", "name": "AGENTS.md Play-Nice block",
        "provider_state": "needs_fix", "words": "AGENTS.md has no play-nice block" },
      { "fix": null, "id": "html-basics", "name": "HTML basics (labels, lang, alt, headings)",
        "provider_state": "worked", "words": "4 page(s) checked: every control labeled, <html lang> set, every <img> has alt, headings in order" },
      { "fix": null, "id": "unsafe-html", "name": "No innerHTML built from fetched data",
        "provider_state": "worked", "words": "no innerHTML built from fetched data" },
      { "fix": null, "id": "secrets", "name": "No secrets in the repo",
        "provider_state": "worked", "words": "no banned public-boundary shapes found (values redacted scan)" },
      { "fix": "update the ids and re-pin the revision (contractctl sync)", "id": "adoption",
        "name": "Adoption manifest", "provider_state": "needs_fix",
        "words": "pin e570e2630702 is not the current library revision a11563b1ab8e" }
    ],
    "evidence": [
      "tools/playnice/playnice.py:run_repo_check",
      "tools/check.sh",
      ".github/workflows/ci.yml"
    ],
    "failing_checks": [ "agents-file", "adoption" ],
    "floor_recorded": null,
    "floor_version": "1.0.0",
    "observed_at": "2026-10-06T12:07:10Z",
    "receipt_line": "Play-Nice floor 1.0.0 · receipt honey-cell-lantern",
    "receipt_word": "honey-cell-lantern",
    "source": "playnice check . --json"
  },
  "datacontenttype": "application/json",
  "dataref": "assets/badge/badge-current.svg",
  "dataschema": "play-nice/estate-event-v1",
  "id": "2026-10-06T12:07:10Z-710403292811",
  "source": "urn:play-nice:source:playnice-cli",
  "specversion": "1.0",
  "subject": "fix needed",
  "time": "2026-10-06T12:07:10Z",
  "traceparent": "00-000000000000000033df710cbcbf3346-07691026641b5077-01",
  "type": "playnice.contract.receipt.emitted"
}
```

The receipt line this envelope carries is not decorative. It is the exact line
`contracts/work/CONTRACT_PROOF.md` rule 1 names, and it verifies:

```
$ python3 tools/playnice/playnice.py verify "Play-Nice floor 1.0.0 · receipt honey-cell-lantern" --json
{
  "exit": 0,
  "floor_version": "1.0.0",
  "given": { "read": [], "receipt": "honey-cell-lantern", "version": "1.0.0" },
  "message": "floor 1.0.0 and the receipt word match this library",
  "next": "keep working",
  "state": "CURRENT"
}
```

So the envelope carries a receipt that a human or an agent can re-verify with
one command and no broker. That is the strongest single argument in this
document for the envelope, and it is also available today without one: the
receipt line is a string, and `playnice verify` already checks it.

### Example 3 — `playnice.ci.run.finished`

Exact command:

```
PYTHONPATH=$PWD/.venv python3 tools/ce-proto/ce_map.py cirun > tools/ce-proto/out-cirun.json
```

Observed output:

```json
{
  "data": {
    "matrix_requested": [ "3.10", "3.11", "3.12" ],
    "merge_rule": "job 'library-gate' name 'library'",
    "observed_at": "2026-10-06T12:09:55Z",
    "runner": "local clone (GitHub-hosted runner fields: UNVERIFIED here)",
    "source": ".github/workflows/ci.yml job 'library' steps, run locally",
    "status": "complete",
    "steps": [
      { "command": "python3 tools/contractctl/contractctl.py validate", "exit_code": 0,
        "name": "validate library + lockfile",
        "output_tail": "VALID — 41 contracts; lockfile verified; receipts unique; index in sync" },
      { "command": "python3 -m pytest tests/ -q", "exit_code": 0,
        "name": "full test suite", "output_tail": "292 passed in 42.20s" },
      { "command": "python3 tools/contractctl/contractctl.py scan", "exit_code": 0,
        "name": "secret / private-material scan",
        "output_tail": "SCAN: CLEAN — <repo-root>=*** has no banned public-boundary shapes" }
    ]
  },
  "datacontenttype": "application/json",
  "dataschema": "play-nice/estate-event-v1",
  "id": "2026-10-06T12:09:55Z-131060301621",
  "source": "urn:play-nice:source:library-gate",
  "specversion": "1.0",
  "subject": "local-gate-2026-10-06T12:09:55Z",
  "time": "2026-10-06T12:09:55Z",
  "traceparent": "00-00000000000000007da37b7039ddf8fb-11f2c87dbf1fb5da-01",
  "type": "playnice.ci.run.finished"
}
```

`<repo-root>=***` is a redaction applied by the prototype, shown rather than
silently dropped, per `contracts/work/OBSERVABILITY.md` rule 4 and
`contracts/access/PUBLIC_AND_PRIVATE.md` rule 6. The GitHub-hosted runner fields
— `run-id`, `run-number`, `run-attempt`, the actual matrix job results — are
marked UNVERIFIED: this clone cannot reach GitHub Actions, and
`.github/workflows/ci.yml` is read but not executed.

### Validation against the published CloudEvents JSON Schema

Exact command:

```
python3 tools/ce-proto/ce_map.py validate tools/ce-proto/out-health.json tools/ce-proto/out-receipt.json tools/ce-proto/out-cirun.json
```

Observed output:

```
out-cirun.json: specversion=1.0 type=playnice.ci.run.finished
  required attributes present: True
  extension attributes: ['traceparent']
out-health.json: specversion=1.0 type=playnice.service.health.changed
  required attributes present: True
  extension attributes: ['traceparent']
out-receipt.json: specversion=1.0 type=playnice.contract.receipt.emitted
  required attributes present: True
  extension attributes: ['dataref', 'traceparent']
VALID against ce-cloudevents_formats_cloudevents.json: 3 event(s), 0 errors
```

`id`, `time`, `observed_at` and `traceparent` differ on every run by
construction — the id is derived from the observation time, and the trace id is
fresh per execution. Everything else in the three captured events above is
reproducible verbatim. The `command` field is the script's rendering of the
argument list; the `exit_code` and `output_tail` beside it are what those
commands actually returned.

The validator checks exactly the keywords the published schema uses — `type`,
`required`, `properties`, `$ref`, `minLength`, `format` — and nothing more.
Keywords it does not implement are not claimed. Note that the published schema
sets no `additionalProperties: false`, which is why extension attributes are
permitted by design.

The schema file is the one from the CloudEvents repository, fetched 2026-10-06
from `https://raw.githubusercontent.com/cloudevents/spec/main/cloudevents/formats/cloudevents.json`.

## The OpenTelemetry, CloudEvents and durable-state boundary

Stated explicitly, because the issue asks for it and because collapsing these
three is the most expensive mistake available here.

- **OpenTelemetry answers how an execution behaved.** Traces, metrics and logs
  describe latency, errors and structure of a run. They are sampled, partial by
  design, and expire. They answer "why was this slow / did it fail / which
  service was involved". They never answer "is this true now" and must never be
  treated as a record of what happened: `contracts/everyone/TRUTH_AND_EVIDENCE.md`
  rule 4 says an agent's message proves what the agent said, not what happened.
  The OTel project describes a Context as "a propagation mechanism which
  carries execution-scoped values across API boundaries" — execution-scoped is
  the operative word.
- **CloudEvents answers what event was emitted.** An envelope says: this
  occurrence, of this type, from this source, at this time, about this subject,
  carrying this data. It is a statement about one occurrence. It says nothing
  about the state after that occurrence and nothing about any other occurrence.
  A CloudEvent is the smallest honest unit of "something happened".
- **Project Home and the repositories answer what is true now.** A mission's
  current status, a task's current claim, a PR's current merge state, a
  library's current revision — these live with the system that owns them and
  nowhere else. `contracts/integration/EVENTS_AND_CACHING.md` rule 7 states it:
  treat a payload as a notification, not as truth; re-read the source before
  any consequential action. And rule 9 states the consequence: every
  event-driven path needs a periodic full reconciliation pass anyway.

Therefore, in this design:

1. A message never carries mutable state truth. No `status` field in any
   envelope may be read as "this is the current status" — it is "this is what
   was observed at `time`, by `source`". Both prototype mappings say so in the
   payload: `observed_at` and `source` alongside `status`, plus a
   `truth_owner` naming the system that answers the current question.
2. The message bus is not the source of truth for anything. A broker may store
   and replay notifications; it may never arbitrate a claim, a merge, or an
   approval.
3. Trace context crosses the boundary; it is not the boundary's payload.
   `traceparent` links an occurrence to the execution that produced it, which
   is precisely the "follow one action across services" that
   `OBSERVABILITY.md` rule 3 asks for and that nothing in this repo provides
   today.

If an envelope's `data` ever needs a field to answer "what is the current
state?", that field belongs in a read of the owner, not in the envelope.

## Transport comparison

JetStream against the simpler option: **direct HTTP plus durable owner state
plus telemetry**. NATS is evaluated here; nothing is deployed.

### What JetStream actually buys, from its own documentation

All NATS documentation claims below were read 2026-10-06 from `docs.nats.io`,
documentation version "2.15 (latest)".

| Property | What the docs say | Consequence for this estate |
|---|---|---|
| Delivery | "Core NATS delivers messages only to subscribers connected at the moment of publication — at most once, never replayed. JetStream adds a persistence layer on top, giving you at-least-once delivery — messages survive restarts and can be replayed." | Replay becomes possible. Nothing in the inventory shows a consumer that needs it — every row is either re-readable at the owner or, for `service health changed`, explicitly required to be re-observed live. |
| Fan-out | Core NATS: "Every subscriber gets a copy… Subscribing doesn't consume or remove messages." | Already available in Core NATS, with no JetStream and no persistence. |
| Load balancing | Queue groups are documented as "same pub/sub, but with built-in load balancing". | Two different things are being run together here. Queue groups route a message; they do not own a task. Exclusivity does not follow from routing: routing a claim to one worker does not make the claim exclusive, because exclusivity needs a single owner of truth to accept the claim atomically, which is durable owner state and not a transport property. |
| Retention | "The stream keeps messages until it hits a limit (size, age, or count). The other options are Interest and WorkQueue, which delete messages once a consumer has read them." | Work-queue retention and interest retention both delete on read, i.e. neither is a replay store. Only Limits retention replays, and only until a limit is hit. |
| Limits are mandatory in practice | "Unlimited defaults grow forever… a production stream needs at least one limit so old orders age out before the disk does." | A second durable store with its own sizing, expiry and archival policy — new operational surface. |
| Operational gotchas, documented | "A stream name is permanent. There's no rename." / "Only one stream can keep a given subject… If a subject overlaps, the server turns it down." / Duplicate window defaults to 2m0s, keyed on `Nats-Msg-Id`. | Every new event class is a stream-or-subject decision with a one-way door attached. |
| Consumer behaviour | Empty fetch is normal: the server replies 408 Request Timeout, or 404 No Messages for a no-wait fetch. `MaxAckPending` set below the batch size throttles the server rather than the client. | More consumer-side code than a synchronous call, for the same information. |
| The binding itself | The CloudEvents NATS protocol binding is headed "NATS Protocol Binding for CloudEvents - Version 1.0.3-wip". | Even if JetStream were adopted, the mapping between the envelope and NATS is a work-in-progress document. |

### What direct HTTP plus durable owner state plus telemetry already covers

| Need | Covered today by | Cost to add JetStream |
|---|---|---|
| A consumer learns something changed | A pull from the owner: `playnice status --json`, `playnice check . --json`, `git ls-remote`, the GitHub API | One more service to deploy, back up, monitor, patch and upgrade |
| What is true now | The owner. This is the only correct answer by the boundary above. | A second store that must be reconciled with the owner (EVENTS_AND_CACHING rule 9), forever |
| "What did this run do, and how did it behave?" | OpenTelemetry traces and metrics | Nothing — OTel is orthogonal to the transport |
| "What did we decide, and why?" | git history plus `schema/question.schema.json` artifacts plus the contract receipts | Nothing; git is already a replayable, durable, queryable log |
| Missed events | A periodic full reconciliation pass, which the contracts already require of every event-driven path | The reconciliation pass still has to exist; the broker does not remove it |
| Consumer independence | The consumer reads the owner directly, so no consumer can be down without affecting only itself | Every consumer gains a second failure domain |

### Do replay, fan-out or offline delivery solve a demonstrated problem here?

**No, on the evidence in this clone.** Concretely:

- The one event whose value is "don't make me re-read" (`service health
  changed`) is re-derived today by `playnice status`, which runs `git ls-remote`
  and completes in about a second. Replaying yesterday's `DIVERGED` tells you
  about yesterday.
- The one event that would genuinely benefit from replay — the receipt
  history — is already replayable, because it is a pure function of the library.
  `git log contracts/everyone/FLOOR.md` reconstructs every previous receipt,
  and `CHANGELOG.md` lines 144, 294, 328, 343-347 record them explicitly.
  A broker would add a place to lose them.
- The one event that genuinely needs exclusivity (`task claimed`) cannot get it
  from a transport at all.
- Fan-out is already available in Core NATS, which is not the thing under
  evaluation.

So the second half of the decision rule — "adopt a broker only if replay,
fan-out or offline delivery solve demonstrated problems that direct calls and
current durable state do not" — fails on all three clauses. The demonstrated
alternative (direct reads plus git plus OTel) wins every row in the table
above, and it is already built.

### The first half of the decision rule: three real producers and consumers

Counted strictly — separately deployed, separately versioned participants
across a process boundary, each of which today carries bespoke glue:

- Producers observable in this clone: `playnice` (`cmd_status`, `cmd_check`),
  the CI gate (`contractctl validate`, `pytest`, `contractctl scan`),
  `contractctl` itself (receipt rotation via `check_receipt_rotation`).
- Consumers: the handoff file writer (`format_handoff`), the badge renderer,
  `cmd_status`'s text and JSON renderers, and the `library-gate` job.

Every one of these is in the same repository, in the same process, or in the
same CI job. They already receive the same Python dict. Wrapping that dict in
a CloudEvents envelope would require each consumer to decode the envelope and
then re-project it to the shape it already had — strictly more code on the
consumer side, zero adapters removed on the producer side. The threshold in
the decision rule ("removes bespoke adapters between at least three real
producers and consumers") is not met, because at zero of those pairings is
there an adapter to remove.

## Adapters and code that could be retired

Honest accounting: this is the short list. The envelope retires none of it.

| Candidate | Current bespoke machinery | Could an envelope retire it? |
|---|---|---|
| Per-surface re-rendering of the same facts | `format_handoff`, `_verified_line`, `_contracts_line`, `_unknown_line`, `_deferred_line` in `tools/playnice/playnice.py` (lines 1500-1571) each re-assemble status, receipts, contracts and unknowns into their own string format | **Not by the envelope.** The duplication is real and worth fixing, but the cause is five formatters over one dict, not a missing wire format. One emitter plus one renderer per surface fixes it with no new dependency |
| Bespoke correlation ids | None exist — `grep -rni "traceparent\|trace_id\|correlation"` finds only the requirement in `OBSERVABILITY.md` rule 3 and the word "correlation" in `contracts/surfaces/API.md` | **Yes, partially.** `traceparent` fills this gap. But the gap can be closed with one `correlation_id` field at an equally low cost, and this repo's consumers are all local |
| Provider status words leaking out | `playnice check` emits `worked` / `needs_fix` / `skipped` (`_check_item`, line 2500) against a closed 16-word vocabulary | **No.** One `STATE_MAP` at the CLI boundary, plus one test that diffs emitted strings against `schema/status.schema.json` the way `tests/test_status_words.py` diffs the Markdown copies. That is the highest-value change found by this study, and it needs no envelope |
| Bespoke receipt handling | `RECEIPT_RE` + `check_receipt_rotation` + `bundle_receipt` + `_RECEIPT_WORDS` in `tools/contractctl/contractctl.py`, and `playnice verify` | **No.** This is a deliberate, working, fully deterministic mechanism with a lockfile and a test. An envelope would wrap it in a format without replacing a line of it |
| Approval lifecycle | `schema/question.schema.json` — already an envelope-shaped artifact with `schema`, stable id, lifecycle `status`, `observed_at`-equivalent fields, `evidence`, and `secrets_policy: "excluded"` | **No.** It is already what a CloudEvents-shaped record looks like, in the repo's own vocabulary, enforced by `contractctl validate-question` |
| Reference and provenance records | `schema/references.schema.json` — already carries `status` canonicality plus `provenance.{participant,source,observed_at,method}` | **No.** Same |
| CI run consumption | `library-gate` waits on a job *name*; no event machinery | **No.** A direct read of the run's conclusion is simpler and already correct |

Summed up: the envelope removes **no** adapter. The one thing it genuinely
offers — a correlation id that crosses process boundaries — is not needed by
any pairing that exists in this clone. Meanwhile the study turned up a real
defect (the `worked`/`needs_fix`/`skipped` divergence) whose fix is smaller,
local and testable, and which an envelope would obscure rather than fix.

## Sources

Every external claim above. All were read on **2026-10-06**.

- CloudEvents, specification `ce@v1.0.2`, published 2022-02-06 —
  <https://github.com/cloudevents/spec/releases/tag/ce@v1.0.2>
  (release title and publication date read from the GitHub releases API; this
  is the latest release of the specification)
- CloudEvents core specification, `main` branch as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md>
  Used for: `id`/`source` uniqueness ("Producers MUST ensure that `source` +
  `id` is unique for each distinct event"); the four REQUIRED attributes
  (`id`, `source`, `specversion`, `type`); `source` semantics.
- CloudEvents JSON Event Format schema, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/formats/cloudevents.json>
  Fetched to `tools/ce-proto/ce-cloudevents_formats_cloudevents.json` and used
  verbatim for validation. Draft-07; requires `id`, `source`, `specversion`,
  `type`; sets no `additionalProperties: false`.
- CloudEvents Extension Attributes index, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/README.md>
  Used for: extension attributes "have no official standing and might be
  changed, or removed, at any time", and "Support for any extension is
  OPTIONAL".
- CloudEvents Distributed Tracing extension, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/distributed-tracing.md>
  Used for: `traceparent` (REQUIRED within the extension) and `tracestate`
  (OPTIONAL), and the explicit statement that the extension is for carrying
  context when instrumenting CloudEvents systems with OpenTelemetry.
- CloudEvents Correlation extension, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/correlation.md>
  Used for: `correlationid` and `causationid` semantics; assessed and not adopted.
- CloudEvents Dataref (Claim Check Pattern) extension, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/dataref.md>
  Used for: `dataref` semantics and the caution that dropping `data` in favour
  of `dataref` requires out-of-band agreement among receivers.
- CloudEvents Data Classification extension, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/data-classification.md>
  Used for: `dataclassification` and `dataregulation`; recommended labels
  `public`, `internal`, `confidential`, `restricted`.
- CloudEvents Partitioning and Sequence extensions, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/partitioning.md>
  and <https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/sequence.md>
  Read during evaluation; neither adopted.
- CloudEvents NATS Protocol Binding, `main` as of 2026-10-06 — headed
  "Version 1.0.3-wip" —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/bindings/nats-protocol-binding.md>
  Used for: the binding's unreleased status; that it "does not prescribe rules
  constraining transfer or settlement of event messages with NATS"; that binary
  content mode requires NATS 2.2 message headers.
- CloudEvents release notes, `main` as of 2026-10-06 —
  <https://github.com/cloudevents/spec/blob/main/cloudevents/RELEASE_NOTES.md>
  Used for: v1.0.2 dated 2022/02/05; v1.0.1 dated 2020/12/12; "Information
  Classification Extension" (#785) as a v1.0.2-era addition.
- W3C Trace Context, W3C Recommendation 23 November 2021 —
  <https://www.w3.org/TR/trace-context/>
  This version: <https://www.w3.org/TR/2021/REC-trace-context-1-20211123/>
  Used for: `traceparent` / `tracestate` as stable, separately-standardised
  fields with a normative format.
- NATS documentation, version "2.15 (latest)" as of 2026-10-06 —
  JetStream: <https://docs.nats.io/nats-concepts/jetstream>
  Streams and retention: <https://docs.nats.io/nats-concepts/jetstream/streams>
  Consumers: <https://docs.nats.io/nats-concepts/jetstream/consumers>
  Publish-Subscribe: <https://docs.nats.io/nats-concepts/pubsub>
  Used for every delivery, retention, limits and operational claim in the
  transport comparison above.
- nats-server, latest release `v2.15.0`, published 2026-09-17 — read from the
  GitHub releases API — <https://github.com/nats-io/nats-server/releases/tag/v2.15.0>

### Repository sources cited by path

Every path below was opened in this clone at HEAD
`a11563b1ab8e5fe4fd235d04972de062a93376eb`.

- `contracts/integration/EVENTS_AND_CACHING.md` — rules 1, 3, 5, 7, 8, 9;
  "Machine notes" cached-item shape
- `contracts/work/OBSERVABILITY.md` — rules 1, 2, 3, 4, 7, 8
- `contracts/everyone/STATUS_AND_STATE.md` — rules 1, 2, 3, 11; "Machine notes"
- `contracts/everyone/FLOOR.md` — rules 1, 5, 6, 7, 8, 10, 11, 15; floor
  version 1.0.0; receipt `honey-cell-lantern`
- `contracts/work/CONTRACT_PROOF.md` — rule 1 (receipt line format), rule 2
  (`playnice verify`), rule 5 (badge from the project's own CI)
- `contracts/everyone/TRUTH_AND_EVIDENCE.md` — rules 1, 4, 5, 6, 7
- `contracts/people/ATTENTION_AND_QUIET.md` — rules 1, 2, 4, 5, 14
- `contracts/access/PUBLIC_AND_PRIVATE.md` — rules 1, 2, 3, 6, 9
- `contracts/work/ORCHESTRATION.md` — rules 4, 5, 6, 10, 11
- `schema/status.schema.json` — the 16-word closed vocabulary and its `$defs`
- `schema/question.schema.json` — `question-v1` family; `$defs/participant`;
  `secrets_policy: "excluded"`
- `schema/references.schema.json` — `status` canonicality enum; `provenance`
  sub-object
- `schema/attestation.schema.json` — `play-nice/attestation-v1`
- `tools/playnice/playnice.py` — `_check_item` (line 2500), `run_repo_check`
  (line 2628), `load_v2_floor` (line 2131), `summarize` (line 2483),
  `format_handoff` (line 1500), `_verified_line` (line 1530), `_contracts_line`
  (line 1539), `_unknown_line` (line 1549), `_deferred_line` (line 1564),
  `collect_repo_state` (line 473), `collect_github_state` (line 911),
  `discover_carryover` (line 686)
- `tools/contractctl/contractctl.py` — `RECEIPT_RE` (line 60),
  `check_receipt_rotation` (line 1674), `bundle_receipt` (line 675),
  `_RECEIPT_WORDS` (line 697), `check_freshness`
- `tools/check.sh` — the deterministic gate, one command
- `.github/workflows/ci.yml` — job `library`, job `library-gate` (name
  `library`), matrix `3.10`/`3.11`/`3.12`, commit identity guard
- `tests/test_status_words.py` — what the existing status test actually checks
- `CHANGELOG.md` — lines 3, 144, 294, 328, 343-347 (receipt rotation history,
  including the "gracefully when Git history is unavailable" note at line 144)
- `.contracts/adoption.yaml` — pin `e570e2630702ddb6c61f7d1d89ab0ce439cdc608`,
  freshness policy `require-current`, update `automatic`
- `.project/CURRENT.md` — points at the live Now block rather than restating
  live state

### Commands run, with observed results

```
$ python3 tools/playnice/playnice.py check . --json          -> 5 checks; 2 needs_fix
                                                                 (agents-file, adoption)
$ python3 tools/playnice/playnice.py status --json --no-github
    -> play_nice.status "DIVERGED", repository.status "NO_REMOTE"/"DIRTY"
$ python3 tools/playnice/playnice.py verify "Play-Nice floor 1.0.0 · receipt honey-cell-lantern" --json
    -> state CURRENT, exit 0
$ python3 tools/contractctl/contractctl.py validate
    -> VALID — 41 contracts; lockfile verified; receipts unique; index in sync
$ python3 tools/contractctl/contractctl.py scan
    -> SCAN: CLEAN — no banned public-boundary shapes
$ PYTHONPATH=$PWD/.venv python3 -m pytest tests/ -q
    -> 292 passed in 44.07s
$ grep -rni "boop\|world tree\|world-tree\|project home\|project-home" .
    -> no matches outside .git (BOOP, World Tree and Project Home are UNVERIFIED
       from this clone)
$ grep -rni "traceparent\|trace_id\|opentelemetry\|otel" .
    -> no matches (only the OBSERVABILITY.md rule 3 requirement and the word
       "correlation" in contracts/surfaces/API.md)
$ grep -n "needs_fix\|\"worked\"\|\"skipped\"" tools/playnice/playnice.py
    -> the three provider words are emitted at lines 2485-2853
$ git rev-parse --is-shallow-repository   -> true
$ git log --oneline | wc -l               -> 1
```

## Recommendation

**The answer is neither. Adopt no envelope and no broker today.**

**Envelope only — rejected.** The technology works: three real mappings from
this repository's own tools validate with zero errors against the published
CloudEvents JSON Schema, and the receipt line one of them carries re-verifies
with `playnice verify` returning `CURRENT`. It is rejected because it removes
nothing. Five of the six extensions the issue asks about are already answered by
a standard CloudEvents attribute or by vocabulary this repo already owns
(`schema/status.schema.json`, `schema/question.schema.json`'s participant shape,
`schema/references.schema.json`'s provenance); only `traceparent` survives, and
the gap it fills has no cross-process consumer in this clone. The decision
rule's threshold — bespoke adapters removed between at least three real
producers and consumers — is not met at any pairing: producer and consumer are
the same process or the same CI job, already sharing one Python dict, so an
envelope would add a decode step to every consumer and retire zero adapters.
What the study actually found is smaller and more valuable: `playnice check`
emits `worked`, `needs_fix` and `skipped`, none of which is on the closed
16-word shared vocabulary, and `tests/test_status_words.py` does not catch it.
One `STATE_MAP` at the CLI boundary plus one test fixes that today.

**Envelope plus NATS — rejected.** The issue's broker test requires replay,
fan-out or offline delivery to solve demonstrated problems that direct calls and
current durable state do not. None of the three does. Replay is unnecessary
because the estate's replayable history already exists as git history and the
contract receipts are a pure function of the library; fan-out is a Core NATS
feature, not a JetStream one, and is not the thing under evaluation; offline
delivery is unaddressed by either option, because
`contracts/integration/EVENTS_AND_CACHING.md` rule 9 requires a periodic full
reconciliation pass for every event-driven path regardless. The `task claimed`
event shows why a broker cannot be the answer to the estate's hardest event at
all: no transport makes a claim exclusive, and `schema/question.schema.json`
already shows what a well-shaped lifecycle artifact looks like without one.
JetStream would add a second durable store that must be reconciled with the
owner forever, with documented one-way doors (stream names are permanent, one
stream per subject, limits mandatory or the disk fills) and an unreleased
CloudEvents binding (`1.0.3-wip`).

**What to do instead, none of it requiring this technology:**

1. Fix the vocabulary leak in `tools/playnice/playnice.py:_check_item` — map
   `worked` / `needs_fix` / `skipped` onto `schema/status.schema.json` at the
   CLI boundary, and extend `tests/test_status_words.py` to diff the CLI's
   emitted strings against the schema the way it already diffs the three
   Markdown copies. This is the finding with the clearest payoff.
2. Add one correlation id to the per-surface formatters
   (`_verified_line`, `_contracts_line`, `_unknown_line`, `_deferred_line`)
   so one handoff line can be followed across surfaces, as
   `contracts/work/OBSERVABILITY.md` rule 3 asks. Use the W3C Trace Context
   format now if a name is wanted — that choice is compatible with a future
   CloudEvents adoption and is not the same decision.
3. Reopen the envelope question the moment a second **separately deployed,
   separately versioned** consumer of an estate event appears. At that point
   CloudEvents costs one small mapper at each boundary and buys interoperability
   that no local convention can. Until then it costs a decoder everywhere and
   returns nothing.

REJECT -- The answer is neither envelope nor envelope plus NATS: every estate
event observable in this clone already carries its own versioned vocabulary, its
own timestamp field and its own source field, and none of them carries a
correlation id.
The identity fields these events carry name the entity an event is about, not the chain of actions that produced it, so they are not a correlation id.
All three prototype mappings validate against the published CloudEvents JSON
Schema with zero errors, and yet the envelope retires no bespoke adapter.
Every producer and consumer found in this clone is in the same process; cross-repository producer and consumer pairings were not measured.
So the envelope should not be adopted now and the broker should never be adopted
without a demonstrated replay, fan-out or offline-delivery problem that direct
calls plus durable owner state plus telemetry do not already solve.

## Unresolved

- **Project Home, World Tree and BOOP could not be examined.** None of the
  three appears anywhere in this clone (`grep -rni "boop\|world tree\|project
  home"` returns nothing outside `.git`), and reading other repositories was out
  of scope for this study. Six of the thirteen inventory rows — mission started,
  mission finished, mission failed, task claimed, task released, BOOP attention
  created — are therefore reconstructed from `contracts/work/ORCHESTRATION.md`,
  `contracts/people/ATTENTION_AND_QUIET.md` and `contracts/access/PUBLIC_AND_PRIVATE.md`,
  not from the systems' own artefacts. Their owners, producers, consumers and
  delivery requirements are **UNVERIFIED**. If those systems already emit a
  shared envelope, this conclusion changes.
- **Repository history is unavailable.** The clone is shallow with one commit,
  so "relate the work to the already-merged receipt work in this repo" is
  answered from `CHANGELOG.md` and the code, not from the commits that merged
  it. The specific commits that introduced receipt rotation, `bundle_receipt`
  and `check_receipt_rotation` are UNVERIFIED.
- **The first half of the decision rule was applied to one repository.** Three
  real producers and three real consumers were found inside this repo, all
  in-process. Whether three producers and consumers exist *across* repositories
  in the wider estate is unmeasured. The rule's threshold is unmet on the
  evidence available, and the rule says default toward rejection — but the
  absence of evidence here is partly an artefact of the scope, and that is the
  weakest joint in this recommendation.
- **The GitHub-hosted CI record was never observed.** The CI mapping ran the
  gate commands locally; `run-id`, `run-number`, `run-attempt`, the real
  three-version matrix results, and the exact shape GitHub would deliver to a
  webhook are UNVERIFIED. The conclusion does not depend on them: a webhook
  delivering the same conclusion to a receiver would still be a notification
  that the receiver must re-read, per `EVENTS_AND_CACHING.md` rule 7.
- **`specversion` value.** The prototype emits `"1.0"`, the major.minor the
  specification defines, while the latest released specification is `ce@v1.0.2`.
  The published JSON Schema does not constrain the value of `specversion` at
  all, so both are schema-valid; whether `1.0` or `1.0.2` is the right wire
  value is a detail this study did not settle.
- **The JSON Schema above is a proposal, not a library change.** It references
  `play-nice/status-v1` and would live beside `schema/status.schema.json` if
  ever adopted. It is not committed here, because this issue permits one file.
- **No scaling or load evidence exists.** Whether the estate will ever need
  fan-out at a volume that justifies a broker is unknowable from one repository
  and one clone.