# Play Nice, Opus — TLDR

> **NON-NORMATIVE companion document.** The [contracts](../contracts/) are
> authoritative; a reader must not mistake this page's philosophy,
> interpretation, or case-study lessons for requirements.

> **Everything should play nicely with everything else.**

Play Nice is a protocol for cooperation among participants that are
**different, fallible, partially known, and independently owned.** Nobody
has to become like anybody else. A participant may leave any room with
everything that is theirs. The contract gate (`resolve → read → verify →
acknowledge task-impact → check for conflicts → attest → commit → work`)
is never authorization — authority comes from the task and the
Authorization contract, not from the ceremony.

Four design values hold the whole thing up:

- **Interoperability without forced sameness.** No universal app, schema,
  or agent. VEFR stays VEFR; Project Worlds stays Project Worlds.
- **`UNKNOWN` is a valid, first-class state.** Never silently turn
  `UNKNOWN` into `healthy`. Failure to prove something is not evidence of
  its opposite.
- **Evidence before reputation.** Capability is earned by evidence, not by
  parameter count, price, or folklore. A claim is worth exactly the
  measurement behind it — and the measurement is worth exactly its
  conditions.
- **Translation is a trust boundary.** A layer that carries meaning either
  preserves what it carries or betrays it. Never quietly turn `INFERRED`
  into `OBSERVED`, `PROPOSED` into `AUTHORITATIVE`, `UNKNOWN` into `TRUE`.

The Small Model Olympics (27 models, 53 tasks each) cabled these values
into this document. Every stuck run was a harness defect, never a model
fault; three "model failures" were zero of the models. Models still failed
individual tasks on the merits — the standings record real passes and real
failures. The eight lessons:
capability is earned by evidence; `UNKNOWN` is information; failure
attribution matters; the judge is also a participant; environment is part
of the evidence; participants get profiles, not reputations; trust is
earned and revocable; translation is a trust boundary.

Close the letter, keep the house. We will say what we know, trust evidence
over reputation, let difference stand, ask before we guess, fail honestly
and fix the harness, say who made what, keep the exits open, recover,
honor attention, adapt — and be adapted to — know what we are not, and
play nice: **keep making the cooperation worth having.**

---

This companion document is **NON-NORMATIVE**. It creates no requirements,
adds no contract, and changes no count, lockfile, or receipt. The contracts
in [`contracts/`](../contracts/) are authoritative. For the argument in
full, read [the Opus](PLAY-NICE-OPUS.md).

*“If that sentence ever stops being odd, that is the moment it starts
working.”*