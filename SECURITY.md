# Security

Play Nice Contracts is a specification, a tooling layer, and a
small test suite. The threat model reflects that — it is not a
service, not a database, and not a daemon.

## Supported versions

| Branch | Supported |
| --- | --- |
| `main` (latest release) | yes |
| older release tags | best-effort, security fixes backported by judgement |

The library is small enough that there is no LTS matrix to
maintain. If you depend on a specific tag, pin to it and check
back here when upgrading.

## Reporting a vulnerability

Please do **not** open a public GitHub issue for anything that
looks like a real vulnerability, an active leak, or a credential
that should not be public.

Use one of these instead:

- **GitHub private vulnerability reporting** — the
  Settings → Code security → Private vulnerability reporting form
  on the canonical repository. This is the fastest path when
  the repo is configured for it.
- **GitHub Security Advisories** — the workflow at
  `.github/workflows/security.yml` (if present) is the supported
  intake when private reporting is enabled.

When you write in:

- describe what you found, where, and how to reproduce
- include the commit SHA or release tag if you have one
- do **not** paste the leaked secret value itself — a fingerprint
  (first 4 + last 4 chars, or the file + line) is enough

You should hear back within a week. A real secret in history is
treated as urgent; a quirk in a docs example is not.

## Reporting a leaked credential in this repository

If you find an SSH key, API token, password, or other credential
that should not be public:

1. Do **not** open a public issue with the value.
2. Use the private channel above. Tell us:
   - the file and line number (commit SHA if you have it)
   - which environment the credential belongs to
   - whether you tested it (please don't, if you can avoid it)
3. We will rotate the credential, scrub the history if needed,
   and publish a post-mortem once the rotation is complete.

We will not ask you to rotate anything on your side; that's on us.

## Threat model in plain English

Play Nice Contracts is honest about what it is and isn't:

- **What it is** — a versioned library of contract specifications
  (markdown), a small Python CLI (`tools/contractctl`) for
  validating/locking/attesting the library, a test suite, and
  example adoption manifests.
- **What it isn't** — a hosted service, a multi-tenant system, a
  database, a network daemon, or anything that reaches out to
  the internet on its own.

Implications:

- The library has no network calls. The tooling reads files; it
  does not phone home.
- Contract receipts are deterministic, locally generated, and
  derived from the canonical contracts. There is no upstream
  service to compromise.
- The library runs as the user who invokes it. It writes to
  the working directory and to the path passed via flags.
- The library never writes outside the directory it is invoked
  in, except where the operator explicitly tells it to.

## Public-private boundary

A public Play Nice Contracts checkout contains the canonical
contracts, the contractctl tooling, the test suite, and the
documentation needed to implement Play Nice. It does not
contain any private infrastructure, hostnames, credentials, or
operational state from the author's environment.

A `Secret / private-material scan` job in `.github/workflows/ci.yml`
catches obvious private-material leakage (RFC1918 IPs, homelab
hostnames, credential prefixes, private-key headers) in PRs and
pushes to `main`.

## What this file does not promise

- No SLA on patch turnaround. We are a small project.
- No backport matrix. If you need a fix on an older tag, the
  fastest path is usually to upgrade.
- No guarantee that every reported issue is in scope. Bug
  reports and feature requests belong in public issues.
