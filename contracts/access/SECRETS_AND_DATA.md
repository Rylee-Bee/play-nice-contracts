---
contract_id: secrets-and-data
title: Secrets and Data
version: 2.0.0
status: canonical
layer: access
applies: [services, configs, exports, logs, agents, data]
triggers: [secret, api key, token, password, credential, env, environment variable, config, export, backup, personal data, pii, data classification, log]
rationale: Secret values live only in secret storage, every record carries a class that decides where it may appear, and both are enforced by structure and tests, not by memory.
---

<!-- contract-receipt: quiet-cedar-satchel -->

# Secrets and Data

## In short

Configs carry references; values live in secret storage. Every record
has a class — public, private, secret — that decides where it may
appear. Enforce both by construction, not by care alone.

## Applies when

- You handle a credential of any kind, or write config, logs or
  exports that could carry one.
- You model data that mixes sensitivity levels, or share anything —
  files, backups, agent context — with other systems or people.
- Not this contract's job: who may do what (identity-and-roles);
  repository publish hygiene and canary scans (public-and-private).
  The floor already says keep secrets secret — see the floor, rule 11.

## Rules

1. Secret values live only in secret storage. Configs, code and docs
   name them (`token_env: GITEA_TOKEN`); the environment or a secret
   manager resolves the name at run time. (MUST)
2. Keep the secret store behind one interface: native storage and an
   external manager are interchangeable, so swapping one for the other
   is configuration, not surgery. (SHOULD)
3. A value that left secret storage is compromised: revoke and rotate
   with the issuer first, investigate use after, and discuss it only
   by type, path and commit — never by re-transmitting the value.
   Deleting or rewriting history is a last resort and never recalls
   a copy. (MUST)
4. Checking is structural, not by memory: a validator or CI scan
   rejects credential-shaped values in tracked text and reports
   findings redacted — type and path, never the value. (MUST)
5. Every record carries a class: at minimum `public` (may appear
   anywhere), `private` (owner-scoped, never in shared output),
   `secret` (rule 1). A system may add classes; the set stays closed,
   documented, and checked on import. (MUST)
6. Your system assigns classes when data is written. A payload's or
   provider's self-declared class is ignored; provenance does not
   launder classification. (MUST)
7. Handling follows the class automatically: exports, screens, logs
   and model context filter by the stored class, never by a decision
   made at render time. Unknown class is treated as at least
   `private`, never as `public`. (MUST)
8. Exports cannot carry secret values, and they carry per-record
   classes so imports preserve them. (MUST)
9. One person's `private` material is invisible to everyone else,
   including administrators — absent from the other's data, not
   merely hidden in the UI. (MUST)
10. Secret values appear only inside an explicitly authorized,
    step-up-checked workflow (see identity-and-roles). A debugging
    agent stays blind to the token it is fixing. (MUST)
11. Prove the classes by test: an export that leaks private material
    should fail a test, not just break a policy. (SHOULD)

## Examples

- Good: a connection config is `{"api_key_env": "SEARCH_KEY",
  "required": false}`; a scan proves no tracked file holds a
  credential shape.
- Bad: "just paste the token here so I can test" — the value is now
  in chat history and model context, so it is compromised (rule 3).
- Sharing a settings export shares preferences and layout choices and
  cannot include journals or tokens: the class filter makes it
  structurally impossible.

## Why

Credential incidents start as convenience shortcuts — a token pasted
into a config, a URL that carried it. Conventions fail for tired
humans and hurried agents; structure doesn't: references-only configs,
class-filtered exports, and scanners that catch the shapes.

## You're done when

- The credential-shape scan passes over the whole tracked tree, apart
  from marked synthetic canaries (public-and-private).
- For every export the system can produce, a test shows private and
  secret records cannot appear.
- You can name every place a secret value could be read, and prove
  agents and logs can't reach any of them.
- Rotating a token means editing one value in the store; a run proves
  nothing else moved.

## Machine notes

- Config shape: `{"type": "gitea", "capability": "source_control",
  "token_env": "GITEA_TOKEN", "required": false}`.
- Records carry `"classification": "public" | "private" | "secret"`
  or a documented extension; readers filter on the field.
- Scanners match common key prefixes with long hex/base64-shaped
  values; the exception marker is `pn-safety: synthetic`.
- Model-context builders select by class and owner; secret values
  never enter prompts.
