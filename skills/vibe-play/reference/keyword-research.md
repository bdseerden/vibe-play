# Phase 1 — Keyword research

Everything downstream (title, short description, full description, screenshot
headings, custom-listing splits) inherits from this phase. The output is
small and precise:

1. **Title keyword** — the strongest intent-matched term. Leads the 30-char title.
2. **Short-description keyword** — the second-strongest term, paired with a
   benefit, inside the 80-char short description.
3. **Description concept list** — remaining searchable ideas to weave into
   natural prose in the 4,000-char full description (first ~250 characters
   are the fold; they matter most).
4. Per major market: whether the same terms hold, or the local language
   searches something else.

There is **no hidden keyword field on Google Play.** Never emit one. Never
hand the user a comma-separated keyword block "for Play". That shape is an
Apple leftover and a Play Metadata policy violation.

## The three surfaces keywords land on

Play indexes three text inputs for search: the **title** (30 chars), the
**short description** (80 chars), and the **full description** (4,000 chars).
All three are per-locale. All three are indexed. The research phase decides
what goes where; phase 2 writes it.

This is the opposite of App Store Connect. On Apple, the description has not
been indexed since iOS 11; the hidden 100-char keyword field carries leftover
terms. On Play, leftover terms go into the full description as **sentences**,
not as a list.

## Rule 1 — Lead with the keyword, not the brand

If the calorie tracker's brand is **Glow Up**, the title
`Calorie Tracker — Glow Up` (25/30) beats `Glow Up — Calorie Tracker` (25/30).
People type "calorie tracker" into Play search; almost nobody types your brand
until you're already big. Position weight is real: the earlier a term appears
in the title, the more it counts. Brand-first naming is a vanity trade against
downloads — make it consciously if the user insists, never by default.

The short description takes the **second** keyword the same way, plus a
benefit. `Count calories and macros in seconds, not spreadsheets.` (55/80)
is a short description; `Feel amazing every day with Glow Up!` is a wasted
80 characters (and the exclamation mark + slogan do no search work).

## Rule 2 — Do not spend the same phrase twice on title + short description

Title and short description are both high-visibility **and** indexed. Repeating
the exact title phrase as the opening of the short description wastes the
second surface. If the title is `Calorie Tracker — Glow Up`, the short
description should not start with "Calorie tracker". Use the second keyword
(`calorie counter`, `macro tracker`, `food diary` — whichever phase 1 picked)
and a benefit.

A *different phrase containing an overlapping word* is fine when it's a
genuinely distinct search ("ai calorie tracker" vs "calorie tracker") — the
rule bans duplicate phrases, not shared words.

The full description **will** reuse the title concept — that's correct, it's
indexed prose — but must **not** repeat the short description verbatim as its
opening. Google calls that out in store-listing best practices.

## Rule 3 — Relevance means intent-match, and two failure classes fake it

A keyword is relevant only when **the person typing it expects an app like
yours**. Both failure classes look attractive in a tool because their
popularity is high:

- **Too generic.** "tracker" for a calorie tracker. Huge popularity, zero
  signal — the searcher may want sleep, budget, or flight trackers. Ranking
  for it (you won't) would still convert terribly.
- **Adjacent but wrong intent.** "muscle growth" for a calorie tracker.
  Related to the *idea*, but the searcher wants workout apps. You might even
  rank; the installs won't come, and the ones that come won't stay. Ask of
  every candidate: *how many people typing this want THIS app?* If the honest
  answer is "some, indirectly" — cut it.

## Rule 4 — Popularity: the floor is a gamble

Popularity scales are a proxy, and they have a **measurement floor** (on a
5–100 scale, that floor is 5; other tools use 0–10 or raw volume — same idea).
A floor value does not mean "no traffic" — it means *unknown, below the
instrument's resolution*. One floor-value concept in the full description is
a lottery ticket; a title and short description built mostly of floor-value
keywords means the listing is invisible and you're gambling the launch. The
title keyword and short-description keyword must have popularity clearly
above the floor. Floor-value long-tails are acceptable only as later
paragraphs in the full description, after the proven terms are placed.

## Rule 5 — Difficulty: pick fights you can win

A keyword must be relevant **and winnable** — relevant-but-unwinnable is
wasted title, winnable-but-irrelevant converts nothing.

- **New app:** anything under ~50 difficulty (or the equivalent lower half of
  the tool's scale) is winnable at some point; the lower the better. Put
  "calorie tracker" (difficulty 60+) in a brand-new app's title and you must
  understand you will *not* rank for it for a long time — the title slot is
  then a bet on the future, and the short description + full description must
  carry winnable terms for the present.
- **Established app** (installs, ratings, retention): difficulty 50–70 becomes
  contestable. Authority compounds; the same short description that did
  nothing at launch starts ranking once the app has a few thousand installs.

An app with very few installs ranking ~1000 for a term in its own title has
an **authority problem, not a keyword problem** — adding more keywords will
not fix it; installs will.

## Rule 6 — Cross-check demand with "apps using this keyword"

Good tools show how many apps carry a keyword in their title / short
description. Many apps betting their title on a term is *evidence people
search it* — devs converge on what works. Zero apps using a high-popularity
term is a smell: either you found a genuine gap (rare) or the metric is
lying (common).

## Rule 7 — Research per market, not per translation

Each locale's listing is localized — and so is the *research*. Germans don't
search a translation of your English keyword; they search what Germans type
("kalorienzähler", not "kalorien tracker" — check, don't assume). For every
major market in the chosen locale set, re-run the popularity lookups on
local-language candidates. Where the tool has no data for a locale, translate
the *concepts* and say plainly that those locales are unverified.

## Play-specific hygiene (this is where Apple habits get people rejected)

- **Complete, readable phrases in prose** — every concept something a human
  would actually type, then written as a sentence. No word-soup fragments.
- **Never a comma-separated keyword block.** Google's own example of a
  violation is exactly this shape: `"Car racing, car driving, race cars, car
  races, race track, driving, drive, race, cars, vehicles, automobiles,
  trucks"`. That is forbidden in the full description, the short description,
  the title, and every translation. Metadata policy
  (https://support.google.com/googleplay/android-developer/answer/9898842)
  and store-listing best practices
  (https://support.google.com/googleplay/android-developer/answer/13393723).
- **No ranking / price / promo tokens in any keyword you plan to place.**
  "Free", "#1", "Best of Play", "top", "discount" are policy violations in
  title, short description, full description, and graphics — they are not
  "strong keywords".
- **No competitor-name bait.** Don't research "MyFitnessPal alternative" as a
  title or short-description phrase. Misleading references are a listed
  violation.

## Workflow with a data tool (keyword_source: astro | manual)

1. Work inside the app's existing entry, or create a **temporary project /
   tag** for a not-yet-released app — keeps research separate from live
   tracking.
2. Seed candidates: the app's own concept list, the tool's keyword
   suggestions, and competitor-term extraction on the 3–5 closest Play
   competitors (find them with Play search on the default storefront).
3. For every candidate record popularity, difficulty, and apps-using-it.
   Dump the table to a local file; slice follow-ups from the file.
4. Apply rules 3–6 to cut the list; sort survivors by popularity × winnability.
5. Assign:
   - strongest surviving keyword → **title** (keyword first, brand second);
   - second → **short description** (keyword + benefit, ≤80);
   - the rest → **description concept list**, to be woven into prose in
     phase 2. First ~250 characters of the full description get the next
     two or three strongest leftover concepts. Never dump the list as a list.
6. Per major market, re-run steps 2–4 on local-language candidates.

## Workflow without a data tool (keyword_source: none)

Honest degraded mode. Do not fake popularity numbers.

1. Candidates from: Play search autosuggest (type the concept on play.google.com
   or a device, note the completions — they're ordered by real volume),
   competitor titles and short descriptions on the storefront, and the user's
   own understanding of the niche.
2. Apply rule 3 (intent) — it needs no tool.
3. State clearly which choices are data-backed (autosuggest order is weak but
   real evidence) and which are judgment calls. Recommend validating the
   title keyword with a real tool before committing the app *title* to it.
4. Still produce the same output table — popularity/difficulty cells say
   `unverified` rather than a guessed integer.

## Output of this phase

A short table the user signs off on — keyword, surface it's assigned to,
popularity, difficulty, and the one-line intent argument. Get explicit
approval on the **title keyword and short-description keyword** before
phase 2 spends dozens of locales on them.

Glow Up example (illustrative numbers — replace with the tool's):

| Keyword | Surface | Pop. | Diff. | Intent |
|---|---|---|---|---|
| calorie tracker | title | 78 | 62 | people typing this want a food-logging app |
| calorie counter | short description | 71 | 54 | same intent, distinct phrase |
| macro tracker | description (fold) | 64 | 48 | adjacent, still this app |
| food diary | description | 58 | 41 | same job, different words |
| fasting window | description | 44 | 35 | feature-level, later paragraph |
| barcode scanner | description | 39 | 29 | feature-level, later paragraph |

Then stop and wait for the sign-off. Phase 2 does not start on a shrug.

## Reporting

**Done** / **Problems** / **Needs you** — including "approve the title +
short-description keywords" in Needs you until they have.
