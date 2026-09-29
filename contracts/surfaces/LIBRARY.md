---
contract_id: library
title: Library
version: 1.2.0
status: canonical
layer: surfaces
applies: [docs, apis, services, ui, integrations]
triggers: [library, book, books, shelf, journal, explainer, teaching, glossary, words to know, under the hood, how it works, tap to learn]
rationale: Many apps can teach people how they work only if their books share one shape that a beginner and an expert can both read, and one home can gather them without rewriting them.
---

<!-- contract-receipt: compass-shelf-wren -->

# Library

## In short

A library is shelves of short books, each written in layers: one plain
sentence, plain pages, the keeper's own voice, words to know, and what's
under the hood. Any app can keep one. A home (Worlds) gathers every
connected library, and never merges or rewrites another keeper's books.

## Applies when

You write explainers, handbooks, journals-as-books, or "how this works"
pages, or you build a home that shows them. Not this contract's job:
reference docs for maintainers (those stay canonical where they live;
books point to them).

## Rules

1. A book has a `title`, a one-sentence `short` in plain words, and at
   least one page. The first page is plain words. (MUST)
2. Pages come in four kinds: `plain` (no jargon), `voice` (the keeper's
   character speaking, e.g. a bee's word for it), `words` (each official
   term with its plain meaning), and `technical` (files, endpoints, code).
   Only `plain` is required. A `voice` or `technical` page never holds the
   only copy of something a person needs. (MUST)
3. A book says what is true today and names where the full truth lives
   (`source`: a doc path or link). When they disagree, the source wins
   and the book is fixed. (MUST)
4. Books carry no secret values and, in a public library, no private
   hosts, addresses or home paths (see the floor, rule 11). (MUST)
5. Every library has a `keeper` (`id`, `name`). A home shows each
   keeper's shelves under that keeper's name, side by side. It never
   merges two keepers' books or rewrites them, even on the same topic.
   (MUST)
6. `look` (on a keeper or a shelf) and `cover` (on a shelf or a book) are
   display hints: a look name the home may style, and a picture name the
   keeper serves. An unknown look falls back to a plain shelf, and a
   missing cover to no picture. Neither ever changes what a book says.
   (MUST)
7. Served over HTTP, a library answers one read-only document with
   `contract: "library/0"` and a `generated_at` time. A room serves it at
   `GET /room/library` and lists `library` in its `offers`. Its covers
   come from the room's `art` extra. (MUST, when served)
8. Kept as files, a book is Markdown with a header (`title`, `kind:
   book`, `short`, optional `order`, `shelf`, `cover`, `source`), pages
   split by a line `* * *`, and a page kind set by its first line:
   `## In <name>'s words` (voice), `## Words to know`, `## Under the
   hood`. Anything else is plain. (SHOULD)
9. A home shows the `short` first and the `technical` pages folded away,
   opens a book with one tap, reads well at phone width and with a screen
   reader, and says when a library couldn't be read, with the last time
   it was. (MUST)
10. When a keeper's library changes, it may ping its home (see room,
    rule 15); the home reads it again rather than waiting. (MAY)
11. **Tap to learn.** A library may carry one shared `glossary`: each term
    with a one-sentence `plain` meaning, the keeper's own name for it
    (`local`, e.g. VEFR's "Keep" for *commit*) and other spellings
    (`also`). An *italic* word in a page that matches a term (by its key
    or an `also`, ignoring case) is tappable: the home shows a small card
    with the word, its plain meaning and "In <keeper>: <local>" when
    there is one, closes it on request and returns focus to the word. An
    italic word with no entry stays plain italic. Nothing shows until it
    is asked for. (MAY; MUST as described when a glossary is present)
12. A keeper with a glossary checks it: every italic term on its shelves
    has an entry, or is on an explicit skip list of ordinary words. A
    book's `words` page may be generated from the terms it uses, so the
    two never drift. (SHOULD)
13. **One book per idea.** An idea has one canonical book, kept once. The
    home keeps concept books on its own shelf (Worlds: "Words for what you
    make"). A glossary entry may point at that book with
    `book: "<keeper>:<book id>"` instead of copying it, and keeps its own
    `local` word. A shelf may hold another keeper's book by reference,
    `{ref: "<keeper>:<book id>"}`, and the home shows the canonical book
    in that shelf's look. Copying a canonical book is a bug. (SHOULD)
14. **Teach while building.** A glossary entry may carry `teach` (a group
    name) and `when` (one sentence describing the shape of what a person
    makes that embodies it). An assistant may offer the term *after* the
    person has made the thing: once, briefly, dismissibly, as an ignorable
    glow (never a popup), and never while they are typing. Tone is
    recognition, never correction ("You just used a design pattern
    called gating."). The stages are first ("There's a name for that"),
    again ("You've seen this idea before", with where it was first met),
    and familiar (no offer; the word is simply tappable). Familiarity is
    the person's own record, kept at their home, holding only a concept id
    and a few words. Concept ids are `slug(term)`. The person picks one
    mode for everywhere: teach me as I build, occasional tips, or plain
    words. Silence is always better than a wrong lesson. (MAY; MUST as
    described when offered)

## Examples

- Worlds' book "Confirm it's you": the short line says "before something
  important, Worlds asks you to prove it's really you". The plain pages
  explain the two ways. "Words to know" gives *step-up authentication*.
  "Under the hood" names `require_step_up` and the 120-second rule.
- Hive Works keeps a book on the same topic in a bee's voice. Worlds shows
  both, each under its keeper, and never blends them.
- VEFR's book on saving says "each *commit* is a checkpoint". Tapping
  *commit* shows "A saved snapshot of the project you can go back to"
  and "In VEFR: Keep".
- Bad: a book whose only explanation is in the technical page; a home
  that "tidies" two keepers' books into one.

## Why

Explaining how things work is part of the product, not an afterthought.
One shape lets a beginner stop at the first sentence and an expert drill
down to the code, and lets every app teach through one home without
giving up its own voice.

## You're done when

- Every book has a plain `short` and starts with a plain page, and the
  served document validates against `schema/library.schema.json`.
- The home shows each keeper's shelves under its name, folds technical
  pages, and survives an unreadable library by saying so.
- No book carries a secret or a private address.

## Machine notes

```text
GET /room/library -> {contract:"library/0", generated_at, keeper:{id,name,look?},
                      shelves:[{id,name,look?,cover?,blurb?}],
                      books:[{id,shelf,title,short,order?,cover?,source?,link?,updated_at?,
                              pages:[{kind:"plain"|"voice"|"words"|"technical",
                                      text, voice?}]}],
                      glossary?:{"<term>":{plain, local?, also?:[...], book?, teach?, when?}}}
shelves[].books?: [{ref: "<keeper>:<book id>"}]   (shelving another keeper's book by reference)
```

`text` is Markdown; `*italic*` marks a glossary term (rule 11). `voice` names the speaker of a `voice` page. Glossary keys are lower-case. `cover`
is a picture name served at `/room/art/{cover}.webp`. `link` is a
same-origin path on the keeper's site (room, rule 6). Looks in use:
`scifi-storybook` (Worlds), `hive-corporate` (Hive Works), `vefr` (VEFR).
