---
contract_id: public-private-boundaries
title: Public Private Boundaries
version: 1.0.0
status: canonical
layer: security
applies: [repositories, configuration, documentation]
triggers: [publishing, repo-work, docs, always-for-tracked-files]
rationale: Some repositories are public now, some will become public later, and none may ever leak private topology, credentials, or personal history. The boundary is enforced by canary tests, not good intentions.
---

<!-- contract-receipt: beacon-sable-echo -->

# Public Private Boundaries

## Purpose

Keep public and publishable repositories clean of private material: no private endpoints, credentials, personal data, deployment topology, or personal medical history — including in anything that might eventually be published.

## NORMATIVE RULES

1. No private endpoints, credentials, personal data, or deployment topology in any tracked file of a repository intended to be public or eventually public.
2. Use synthetic identities and reserved example domains (`service.example.invalid`, RFC 2606/6761 classes) in tests and documentation. Real hostnames, IPs of private networks, and live URLs never appear.
3. Review screenshots, SVG metadata, archive contents, design-file exports, and every commit in a PR — leaks hide in attachments, not only code.
4. An ignore rule does not remove files already tracked and does not erase history. Track the boundary with canary regression tests that scan every tracked text file.
5. Personal medical history, diagnoses, medications, and symptoms do not belong in shared libraries. The engineering lesson (e.g. "migraine-safe design" requirements) belongs; the personal reason does not.
6. A repo is public-safe or it is private — explicitly, as a recorded decision. "Probably fine to publish someday" is treated as "will be published": hold it to the public boundary.
7. When a credential was published: revoke/rotate immediately, investigate use, report only its type/path/commit — never re-transmit the value; coordinate history rewrites with the owner.

## RATIONALE

This ecosystem already contains both public repos and repos that will be public after a scrub. The only boundary that survives years of contributions is a mechanical one: a canary test that fails loudly, run in CI, scanning everything tracked. Intent-based boundaries decay; test-based boundaries persist.

## HUMAN EXAMPLES

- A test config uses `http://service.example.invalid:3000` and a synthetic token with an on-line canary marker — and the canary test proves the scanner catches both the shapes and respects the marker.
- A design handoff document goes public after a review pass finds one hostname in a screenshot's SVG metadata — caught by the checklist, not by luck.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- A public-safety regression suite (canary tests) runs locally and in CI on every tracked text file: credential shapes, private-IP ranges, real-looking hostnames, token-like strings.
- Findings report redacted: type, path, line — never the matched value.
- Synthetic canaries carry an inline marker (e.g. `pn-safety: synthetic`) so exceptions stay visible.
- Pre-publish checklists include binary-ish artifacts (images, archives, exports) which the text scanner flags for manual review.

## GOOD EXAMPLES

```yaml
base_url: http://service.example.invalid:3000
token: "synthetic-canary-pn-safety: synthetic"   # caught-by-design
```

## ANTI-PATTERNS

- Real LAN IPs in compose examples.
- A private hostname "just in a comment".
- Screenshots pasted into docs without metadata review.
- Treating `.gitignore` as history protection.
- Personal health context in a shared design contract's rationale.

## ACCEPTANCE CHECKS

- Does the canary suite pass on the full tracked tree?
- Do tests and docs use only reserved example identities?
- Would the repository survive being published today, by surprise?
- Is anything private present that is only protected by intent? (Must be no.)