# Phase 5 — In-app string localization

Localizes the strings users see *inside* the app. Sibling of phase 2 (store
metadata); this one touches the Android / RN / Expo project — **not Xcode**.
The framework is the same spirit as vibe-aso: **cascade every locale in one
pass, review by detectors, never by a per-language human gate**; most
translation bugs are *domain* bugs that fluent output hides.

## Step 0 — Discover state

Inspect the project before proposing anything:

- **Native Android** — `res/values/strings.xml` (and `plurals.xml`,
  `arrays.xml` if present). Locale dirs look like `res/values-de/`,
  `res/values-b+zh+Hans/`, `res/values-zh-rTW/`.
- **RN / Expo / Flutter-in-JSON** — `i18n/*.json`, `locales/*.json`,
  `app.json` extra, or i18next resource files. Prefer the project's
  existing layout; do not invent a second system.
- **Already localized** → this is a *top-up*: only translate what's missing
  or new, and obey the top-up rules at the bottom.
- **Partially localized** (locale files exist but many values equal their
  English key / English source) → repair: fill the untranslated remainder.
- **Zero localization** (hardcoded literals in Kotlin/Java/JS/TS) → bootstrap.

Judge "translated" by **value ≠ source English**, never by "key exists" — a
seeded `<string name="stats">Statistics</string>` in 30 locales is coverage,
not translation.

Do not assume an `.xcstrings` catalog, an `.lproj`, or `xcodebuild`. If the
repo is a Kotlin Multiplatform / Compose / Flutter project, use *that*
project's string system.

## Locale set

Reuse the set chosen in phase 2, mapped to Android resource qualifiers
(in-app uses different codes than Play listings):

| Play listing | Typical `res/values-*` |
|---|---|
| `de-DE` | `values-de` |
| `pt-BR` | `values-pt-rBR` |
| `pt-PT` | `values-pt-rPT` or `values-pt` — check what the project already uses |
| `zh-CN` | `values-zh-rCN` (legacy) or `values-b+zh+Hans` (API 21+) |
| `zh-TW` | `values-zh-rTW` / `values-b+zh+Hant` |
| `zh-HK` | `values-zh-rHK` |
| `iw-IL` | `values-iw` or `values-he` — **Android accepts both**; follow the project's existing choice, do not add a second Hebrew dir |
| `es-419` | there is no perfect `values-` for "Latin America Spanish". Common pattern: `values-es` as LatAm, `values-es-rES` for Spain. Confirm with the user. |
| `en-GB` | `values-en-rGB` |

If a mapping is unclear, say "verify against the project's existing
`res/values-*` dirs" — do not invent a qualifier.

The store listing promising 40 languages while the app speaks one is a bad
look in reviews — align them.

## Bootstrap (zero-state projects)

1. **Prefer the project's native mechanism.** Android: `strings.xml` +
   `string` / `plurals` / `string-array`. RN/Expo: whatever `i18n` library
   is already imported. Flutter: ARB if the project already has it.
2. **Wrap user-visible literals** (`Text("…")` / `stringResource` /
   `getString` call sites / React `Text` with raw English). Do NOT wrap:
   resource/identifier parameters, icon names, analytics event names,
   single-word camelCase logic identifiers, log strings. Interpolations
   (`"Logged $n calories"`) become format strings
   (`Logged %d calories` / `Logged %1$d calories`) — they can't be wrapped
   mechanically without choosing a specifier.
3. **Brand pass (interactive).** Some strings must stay literal in every
   language: the brand name (`Glow Up`), plan names, product codes. Show
   the user the candidates and let them choose localize vs keep-literal.
   Record the decisions in a small per-project config file so future runs
   respect them.
4. Harvest all keys into the default-language source table; then translate.

## Translating — engine and batching

Use the engine from `~/.vibe-play/config.json` (same engines as vibe-aso /
phase 0):

- **subagents**: spawn one subagent per locale (or per few locales), each
  given the key list + context + the rules below, returning strict JSON.
- **deepseek / openai**: batched chat-completion calls, ~80 keys per batch —
  large batches keep register consistent; small batches flip-flop grammar
  between imperative and infinitive across a list. **Check the account
  balance before a cascade**.

Run locales as independent parallel jobs; each writes its own file; merge
after detectors pass. Chunk the shell commands per locale/batch.

**Every translation request carries:**

- the brand-literal list (output verbatim, never translated);
- format-specifier rules: Android `%s` `%d` `%1$s` `%1$d` `%%` and named
  `^1` / i18next `{{count}}` / RN `{name}` preserved exactly, **count AND
  order**; never inject a specifier into a string that has literal numerals.
  Positional reorder (`%2$d … %1$d`) is LEGAL and correct in some languages;
  force positional forms when order changes, don't "fix" them back;
- frequency labels on paywalls (`Yearly`, `Monthly`, `Weekly`) translate as
  **adverbs** ("billed yearly"), never the bare noun ("Year") — the noun
  collides with duration labels elsewhere on the same screen;
- a **sense glossary** for every ambiguous domain word, and
- **enum groups** for ordered sets that render side by side.

### The sense glossary — where translation actually fails

Fluent-but-wrong survives every automated check. The model translates the
*common* sense of a word, not your app's sense: in Glow Up, "log" is
recording a meal (not a tree trunk, not a login), "goal" is a daily calorie
target (not a sports goal), "serving" is a food portion (not a tennis serve,
not a web server). Declare each ambiguous term with its intended meaning
once, inject it into every request, and it fixes all locales at once.

Two limits:

- **Short keys defeat the glossary.** Two-word badge names give the model no
  context. Budget a post-cascade sweep: for each ambiguous term, grep all
  locales for the *wrong* sense's word family and force-retranslate hits.
- **"Only overwrite values that equal their source" can't fix wrong-sense
  values** — those *are* translated, just wrongly. Repairs need two passes:
  an identity fill AND the condemned-value scan above.

**Enum groups**: rank ladders, badge tiers, mode names that appear in one
list must not collapse onto one word. Declare the sets; after translating,
check pairwise distinctness per locale.

## The detector suite — this replaces the human gate

Run over every locale before anything lands:

| Detector | Catches |
|---|---|
| same-as-source | untranslated values (whitelist true cognates: "OK", "Pro", numerals, and per-locale loanwords) |
| specifier parity | `%s`/`%d`/`%1$s` / `{name}` / `{{count}}` count-or-order drift vs default — a crash, not a typo |
| never-translate atoms | emails, URLs, `mailto:`, specifier-only strings — only correct value is the source itself |
| brand atoms | `Glow Up` (or the user's locked form) present and untranslated |
| Latin leak | non-Latin locale values holding Latin word-runs that aren't kept tokens |
| caps + punctuation parity | ALL-CAPS keys stay shouty in cased scripts; trailing terminator matches the locale — Greek's question mark is `;`, CJK uses `。/？`, Thai ends sentences with nothing |
| enum-group collision | two members of a declared set sharing one translation |
| zh-CN / zh-TW script mix | Simplified/Traditional contamination. Use a converter (opencc) the same way vibe-aso does: round-trip is valid for Simplified; for Traditional test characters in isolation |
| RTL / CJK / Indic spot-check | 10–15 keys in Arabic (`ar`), Hebrew (`iw`/`he`), one CJK, one Indic — the detectors are necessary, not sufficient |
| shipped-vocab diff | new copy inventing a second word for a term the app already ships |

After the cascade, three cleanup passes in order:

1. **Echo retry** — re-ask ONLY keys that came back identical to English
   (up to 3 rounds); survivors are usually genuine cognates.
2. **Register harmonization** — any long list rendered together, sent as
   one request per locale with 6–8 of the app's own shipped strings as a
   **register anchor**. Afterwards re-check invented trailing periods and
   enum groups re-collapsing.
3. **Spot-read 10–15 keys in 4–5 languages** (include one CJK, one RTL).

## Data libraries (food databases, exercise catalogs…)

Bounded in-bundle content lists (50+ items with stable IDs) get a variant
pipeline: batch ~30 items **grouped by category** (siblings disambiguate
each other — "Chicken Breast/Thigh/Tenderloin" translated together come out
distinct; alone they collapse). Wire display through a lookup by ID with
English fallback; keep the English field for search. Filter hallucinated
keys at merge.

## Top-up rules (apps that already ship translations)

1. **Never rewrite whole locale files from harvested keys.** Any key reached
   through a runtime variable is invisible to call-site harvesting, and a
   rewrite silently deletes its translations. Merge: add new keys, overwrite
   only an explicit condemned list, and assert `old_keys − new_keys = ∅`
   per locale before writing. Back up the locale dirs first.
2. **Prune dead keys before translating** — keys no source references
   anymore are orphans.
3. **New copy inherits the shipped vocabulary.** Paste the app's own
   renderings into the prompt rather than letting the model pick a second
   word.
4. A sibling project's translations are **not** proof. Never bulk-import
   values that equal their source.

## Wear / widgets / other modules

Each Android module (`:app`, `:wear`, a widget, an Automotive flavor) that
shows user-visible strings needs its own `res/values*`. If the phone sends
an extension raw English strings at runtime, the extension's table must
carry those keys even though no call site in the extension references
them. Check which shape the app uses.

## Verify + ship discipline

- Native: assemble the default variant (`./gradlew :app:assembleDebug` or
  the project's documented task). Format-specifier mistakes often surface
  as `Resources$NotFoundException` or broken `String.format`.
- RN/Expo: run the project's typecheck / `npx tsc --noEmit` if it has one,
  and open one RTL locale in the simulator if the user can.
- **Freeze strings before the release bundle.** Any string edit after the
  AAB is built may or may not land — if strings change, bump `versionCode`
  and rebuild; never submit the earlier bundle.

Do not run `xcodebuild`. This is not an iOS project unless the user
explicitly opened one, in which case point them at vibe-aso.

## Reporting

**Done** / **Problems** / **Needs you**.
