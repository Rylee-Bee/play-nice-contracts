---
contract_id: secrets
title: Secrets
version: 1.0.0
status: canonical
layer: security
applies: [configuration, infrastructure, agents, api]
triggers: [always, secrets-handling, config-work, ci, agent-actions]
rationale: Secret values live only in secret stores. Everything else references them symbolically. A secret that appears in a config file, a log, a URL, a commit, or model context has already failed, wherever it was headed.
---

<!-- contract-receipt: prairie-latch-gatehouse -->

# Secrets

## Purpose

Keep secret material out of everything except secret storage: out of configs, logs, commits, exports, URLs, chat, and model context — with structural guarantees, not conventions.

## NORMATIVE RULES

1. Configuration references secrets symbolically (`token_env`, `api_key_env`, `secret_ref`) and resolves through env indirection or a secret-management boundary. Inline secret values in shareable config are rejected structurally by validation, not by review alone.
2. Never: log credentials; put secrets into normal model context or ordinary UI rendering; inline secrets into config intended for sharing; pass secrets in URLs; commit secrets to any repository.
3. Secret stores are a capability (see Capability First): native storage and external providers (Vault-class) are interchangeable adapters behind one contract; swapping the store is not surgery.
4. Exports structurally exclude secret values. Export formats reference secrets symbolically; if a future feature exports provider configuration, it exports references.
5. Sensitive vault access requires step-up authorization (see Authorization); secret values render only inside explicitly authorized secure workflows.
6. Validators reject keys that look like inline secret material (common key prefixes with value shapes like long hex/base64), with a visible, marked exception mechanism for deliberate synthetic test canaries.
7. Exposure is treated as compromise: revoke and rotate immediately with the issuer, then investigate use; history rewrites are remediation of last resort and never recall existing clones.
8. Automated gates run everywhere: CI scans every tracked text file for credential shapes and reports findings redacted (the gate never prints the value it caught).

## RATIONALE

Every real credential incident in this ecosystem came from a convenience shortcut: a token pasted into a config, a URL that carried it, a client bundle that inlined it. Structural exclusion (validator-rejected key shapes, export whitelists, indirection-only config) is what survives tired humans and hurried agents — conventions do not.

## HUMAN EXAMPLES

- A connection config says `token_env: GITEA_TOKEN` — and a test proves no file in the repo contains a plausible token value.
- Rotation is a documented operation: change the value in the store; nothing else moves.
- An agent asked to "fix the auth issue" is structurally unable to read the token even while debugging it.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Secret resolution is a boundary (env/secret manager); consumers never see source material except the resolved value in-process.
- Public-safety CI gate: shape-scanning with redacted reporting and a marked synthetic-canary exception (e.g. `pn-safety: synthetic`).
- Export validators: structurally unable to include secret-classified fields.
- No secret value ever enters prompts, tool arguments, or logs — enforce at the boundary, log the reference instead.

## GOOD EXAMPLES

```json
{"type": "gitea", "capability": "source_control",
 "token_env": "GITEA_TOKEN", "required": false}
```

## ANTI-PATTERNS

- `{"api_key": "sk-EXAMPLE-..."}` in a tracked config (any realistic credential shape belongs nowhere; use reserved example values such as `sk-live-EXAMPLE` only in deliberate, marker-carrying canaries).
- Tokens in remote URLs (rewrite + rotate on discovery).
- "Just paste it here so I can test" in an agent session.
- Logs that dump request headers.
- An ignore rule trusted to protect an already-tracked file.

## ACCEPTANCE CHECKS

- Does the shape-scanning gate pass on the whole tree?
- Can any export produce a secret value? (Must be structurally impossible.)
- Are all secrets resolvable-but-invisible to agents and logs?
- Is rotation documented and does anything break when it happens? (List what.)