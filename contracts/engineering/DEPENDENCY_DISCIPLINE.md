---
contract_id: dependency-discipline
title: Dependency Discipline
version: 1.0.0
status: canonical
layer: engineering
applies: [engineering, infrastructure]
triggers: [new-dependency, packaging, build-changes]
rationale: Every dependency is a promise to maintain, a supply-chain risk, and a future migration. Add them for demonstrated need, keep them few and boring, and pin what must be reproducible.
---

<!-- contract-receipt: inkstone-velvet-opal -->

# Dependency Discipline

## Purpose

Keep the dependency surface small, deliberate, and reproducible — so builds are trustworthy and replacements are possible.

## NORMATIVE RULES

1. Every dependency addition answers a demonstrated need: name the problem it removes, the complexity it adds, and why the existing seams (see Search Before Inventing) cannot cover it.
2. Prefer boring, well-maintained dependencies with stable APIs. Small, standard, and dull beats clever and novel.
3. Dependencies are pinned for reproducibility (lockfiles); lockfile drift is detected deterministically.
4. Adding a dependency that duplicates an existing capability requires a recorded justification — or removal of the one it replaces in the same change.
5. No dependency may become a hidden requirement for core operation (see Capability First, Deterministic First): optional providers stay optional; core boots without them.
6. Supply-chain minimums: pinned versions/lockfiles, integrity where the ecosystem supports it, no `curl | sh` installs in build paths, review of dependency changes like code.
7. Removal is a supported operation: a dependency that no longer earns its maintenance cost is retired (and recorded as success).
8. Vendored/derived artifacts (generated code, checked-in builds) declare their source and regeneration path (see Stable Truth).

## RATIONALE

Dependency creep is how small tools become un-updatable platforms: every addition is permanent until someone pays the removal cost. The "lean dependencies" correction pattern (Personal World P1 removed Storybook, React Query, and a pile of template cruft — 14 packages) exists because the original additions felt individually reasonable.

## HUMAN EXAMPLES

- A proposal to add a cache library is answered by "what does the existing 30-line TTL map not do?" and dies or survives with evidence.
- `uv.lock` / `package-lock.json` committed; CI fails if the lockfile doesn't match manifests.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Lockfiles are canonical and committed; CI verifies lockfile↔manifest coherence.
- Dependency review is a checklist item in PR templates for new top-level deps.
- Builds are reproducible from lockfile alone; no floating tags in build paths.

## GOOD EXAMPLES

```markdown
## Add lib X?
Problem: dedupe/invalidation/retry complexity removed: ~120 lines
Added: 1 dep (maintained, 2.3MB), 1 API surface
Existing seams: none cover this; checked lib-Y seam first.
```

## ANTI-PATTERNS

- Adding a framework for one utility function.
- Unpinned `latest` in CI.
- Two libraries for the same job, both half-used.
- "We'll vendor it and edit it" without regeneration/ownership notes.
- Dependency growth with no removal ever.

## ACCEPTANCE CHECKS

- Can each dependency state the problem it earns its keep on?
- Is the build reproducible from the lockfile?
- Is any optional dependency required for core boot? (Must be no.)
- When was a dependency last removed, and was it recorded as good?