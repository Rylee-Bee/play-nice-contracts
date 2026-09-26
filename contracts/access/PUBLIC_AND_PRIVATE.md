---
contract_id: public-and-private
title: Public and Private
version: 2.0.0
status: canonical
layer: access
applies: [repositories, docs, examples, design, automation]
triggers: [public, publish, open source, repository, readme, docs, documentation, screenshot, demo, test data, sample data, deploy, share, leak, privacy]
rationale: A repository that is public now or later is held to the public standard today, and canary tests — not intentions — enforce that boundary.
---

<!-- contract-receipt: meadow-lighthouse-fence -->

# Public and Private

## In short

Decide now whether a repository may be public, and hold it to that
standard today. Real hosts, private topology and personal history
never enter tracked files; a canary test proves it, not good intent.

## Applies when

- You create, publish or contribute to a repository that is public
  now or could be later.
- You write docs, examples, tests, screenshots or design exports that
  might ship with it.
- Not this contract's job: handling live credentials and data classes
  (secrets-and-data); who may act (identity-and-roles).

## Rules

1. Every repository has one recorded status: publishable, or private.
   Treat "probably fine someday" as publishable. (MUST)
2. In a publishable repository, no tracked file carries private
   endpoints, real hostnames, internal IP addresses, credentials,
   personal data or deployment topology. (MUST)
3. Tests, docs and examples use reserved names
   (`service.example.invalid`) and synthetic tokens: real enough to
   catch carelessness, harmless to publish. (MUST)
4. Look beyond code: screenshots, SVG metadata, archives, design
   exports, and every file in a pull request. Leaks hide in
   attachments. (MUST)
5. An ignore rule neither untracks a tracked file nor erases history.
   Never treat it as protection. (MUST)
6. A canary scan runs locally and in CI over every tracked text file.
   It extends the credential-shape check (secrets-and-data) to
   private IP ranges and plausible real hostnames. Findings report
   type, path and line — never the matched value. (MUST)
7. A deliberate synthetic canary carries a visible marker
   (`pn-safety: synthetic`), so every exception stays reviewable.
   (MUST)
8. When the scan catches a real value, the exposure rule in
   secrets-and-data applies: revoke and rotate first, discuss only by
   type and location. (MUST)
9. Health history stays personal: diagnoses, medications and symptoms
   do not enter shared material. Keep the engineering lesson (say,
   motion that is safe for migraines); drop the personal reason. (MUST)

## Examples

- Good: a test config reads `base_url: http://service.example.invalid:3000`
  with a token marked `pn-safety: synthetic` — the scan catches both
  shapes and honors the marker.
- Bad: a real LAN hostname in a comment, or an internal service URL
  inside the SVG metadata of a harmless-looking screenshot.
- A design doc goes public only after the scan and a metadata check
  pass — caught by the routine, not by luck.

## Why

Repositories change hands and intentions: today's private folder
becomes tomorrow's public example. A boundary built on intent decays
one tired commit at a time; a canary test that fails loudly in CI
stays honest for years.

## You're done when

- The canary scan passes over every tracked file.
- Searching docs and tests for real hostnames, IPs and emails finds
  only reserved examples.
- The repository's publishable-or-private status is recorded where a
  newcomer can read it.
- Images and archives were scanned for metadata before the last
  publish, not eyeballed.

## Machine notes

- Scan `git ls-files`: credential shapes, RFC 1918 ranges, non-reserved
  domains; report `type, path, line` only.
- Reserved example names: the RFC 2606 / 6761 family
  (`example.invalid`, `example.com`, `.test`).
- The text scan flags binary artifacts (images, archives) for one
  human metadata pass before publishing.
