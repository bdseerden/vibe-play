# Phase 2 — Play metadata, default locale first, then every chosen locale

Writes the three indexed text fields — `title`, `short description`, `full
description` — plus the optional promo-video YouTube URL, for the default
locale, then adapts them into every Play translation locale the user chose.
Files land in the standard fastlane supply layout so `supply` can push them:

```
fastlane/metadata/android/<locale>/
  title.txt
  short_description.txt
  full_description.txt
  video.txt                  # optional; YouTube URL only
```

There is no `keywords.txt`. Do not create one.

## The locale set (verified against Play Console Help, 2026)

Official source: "Translate and localize your app"
https://support.google.com/googleplay/android-developer/answer/9844778

If you cannot see a code on that page (or in Play Console → Store listing →
Manage translations), do not invent it. Say "verify in Play Console".

```
af, am, ar, az-AZ, be, bg, bn-BD, ca, cs-CZ, da-DK, de-DE,
el-GR, en-AU, en-CA, en-GB, en-IN, en-SG, en-US, en-ZA,
es-419, es-ES, es-US, et, eu-ES, fa, fa-AE, fa-AF, fa-IR,
fi-FI, fil, fr-CA, fr-FR, gl-ES, gu, hi-IN, hr, hu-HU,
hy-AM, id, is-IS, it-IT, iw-IL, ja-JP, ka-GE, kk, km-KH,
kn-IN, ko-KR, ky-KG, lo-LA, lt, lv, mk-MK, ml-IN, mn-MN,
mr-IN, ms, ms-MY, my-MM, ne-NP, nl-NL, no-NO, pa, pl-PL,
pt-BR, pt-PT, rm, ro, ru-RU, si-LK, sk, sl, sq, sr, sv-SE,
sw, ta-IN, te-IN, th, tr-TR, uk, ur, vi, zh-CN, zh-HK, zh-TW
```

Default locale is whatever the app already uses on Play (often `en-US`); that
is the source. The rest are targets. **Ask the user once** whether they want
all of the official list or a subset (top markets), and reuse that answer for
screenshots and in-app strings.

Play codes that bite people coming from App Store Connect:

| Do not write | Play wants |
|---|---|
| `he` / `he-IL` | `iw-IL` (Hebrew; Play still uses the ISO 639 `iw` code) |
| `zh-Hans` | `zh-CN` |
| `zh-Hant` | `zh-TW` (and `zh-HK` is a separate Play locale) |
| `es-MX` as the LatAm bucket | `es-419` (Latin America Spanish) |
| Apple's `no` | `no-NO` |
| Apple's `sv` | `sv-SE` |
| Apple's `ja` | `ja-JP` |

`fil` (Filipino) **is** a Play locale. Apple rejects it; Play accepts it.

The Play Developer API describes `language` as a BCP-47 tag (example in the
docs: `de-AT` for Austrian German). The Console translation picker is the
list above. If an API write for a code not on that list no-ops or 4xxs, drop
it and say so — do not keep a shadow locale.

## Character limits (hard, per locale)

| Field | Limit | Indexed? |
|---|---|---|
| title | 30 | yes |
| short description | 80 | yes |
| full description | 4000 | yes |
| video | YouTube URL | n/a (not a keyword surface) |

Show every write as `(X/LIMIT)`. Validate after writing, every locale, with
`python3 scripts/validate_listing.py`. German, Finnish, Turkish, Hungarian,
Tamil and Malayalam explode compound words — flag any default-locale title
already over ~22 chars as a translation-length risk before generating.

### Title rules (30)

From Metadata policy + store-listing best practices
(https://support.google.com/googleplay/android-developer/answer/9898842,
https://support.google.com/googleplay/android-developer/answer/13393723):

- Keyword first, brand second (`Calorie Tracker — Glow Up` (25/30)).
- No emojis, emoticons, or repeated special characters.
- No ALL CAPS unless that is the brand.
- No "Free", "No Ads", "#1", "Best of Play", "App of the year", "Popular",
  price, or promo.
- No impersonation / "official app of …" claims.
- Unique enough that a user will not tap the wrong app.

### Short description rules (80)

Official: first text on the listing; users can expand it to the full
description. Highly recommended guidance from
https://support.google.com/googleplay/android-developer/answer/9866151:

- Benefit-led + the second keyword. One or two sentences max.
- Do **not** repeat it verbatim as the opening of the full description.
- Do not use slang the market would not type. Do not stuff keywords.
- No call-to-action ("download now", "install now", "try now").
- No ranking / price / promo language.
- No emojis, emoticons, line breaks, repeated punctuation, or decorative
  symbols (★ ☆ …). Standard writing marks of the language are fine (¿ ¡ æ Ø).
- © ® ™ allowed when they are actually the mark.
- Only use a period at the end if there are multiple sentences.
- Do not capitalize for emphasis; capitalize as the language normally does.

Glow Up: `Count calories and macros in seconds, not spreadsheets.` (55/80)

### Full description rules (4,000)

- Succinct, natural prose. Shorter usually reads better. 4,000 is a ceiling,
  not a quota — a tight 800–1,500 often converts better than a stuffed 3,900.
- First ~250 characters are the fold (what shows before "Read more" on many
  surfaces). Put the next two or three strongest leftover concepts there, in
  sentences.
- Weave the rest of the concept list into later paragraphs. **Never** as a
  comma-separated list.
- No unattributed / anonymous testimonials. If you quote, attribute a real
  named source the user can stand behind — or don't quote.
- No ranking / price / promo claims. No competitor-name bait.
- No "not a medical device…" *omission* if this is a health app that isn't a
  regulated device — Play's Health policy wants that disclaimer in the
  description when it applies (phase 6). Glow Up, if it is a wellness
  tracker and not a medical device, should say so in prose: `Glow Up is not
  a medical device and does not diagnose, treat, cure, or prevent any
  medical condition.`
- Metadata policy applies to **every translation**.

## Workflow — five steps per app

### 1. Get the default-locale source

If the app is already live, pull the live listing (source of truth) rather
than trusting local files:

```bash
python3 scripts/play_api.py listings
# or
fastlane supply init
```

`edits.listings.list` returns every localized `Listing`:
`language`, `title`, `fullDescription`, `shortDescription`, `video`.
Official: https://developers.google.com/android-publisher/api-ref/rest/v3/edits.listings

If this is a new app, write the default locale fresh from the phase-1 table:

- title = title keyword + brand (`Calorie Tracker — Glow Up` (25/30))
- short description = second keyword + benefit
- full description = prose from the concept list, fold first
- video.txt = YouTube URL or empty

### 2. Source analysis — BEFORE any translation

Read the default-locale files and write down, explicitly:

- **Brand structure**: the BrandWord (proper noun — `Glow Up`) vs the
  DescriptorWord (common noun — `Calorie Tracker`). The brand stays itself;
  the descriptor is search vocabulary.
- **Domain vocabulary**: for each term of art (macros, fasting window, meal
  plan…), decide: keep English everywhere / keep English in Latin scripts
  only / translate / transliterate.
- **Idioms in body copy** ("stays out of your way", "actually works") — mark
  for meaning-translation, never literal.
- **Verbatim atoms**: URLs, email addresses, EULA, numbers + units, the
  brand as the user styles it. These survive every locale untouched.

If a term is ambiguous, ask the user now — one clarifying question here is
cheap; a wrong guess replicated into 40 locales is not.

### 3. Generate all target locales in one pass

Write a small script with the full per-locale table embedded (translations
produced per the configured engine), emit all `<locale>/*.txt` files, and
print per-locale char counts as `(X/LIMIT)` as it writes. Never serialize
behind a single-language pilot; never pause for a per-language human review
unless the user asked for one.

**Title / short-description rules per script family:**

- **Latin-script locales**: keep the BrandWord verbatim; translate the
  DescriptorWord into the locale's *searched* term (that's what phase 1's
  per-market research found — use it, don't re-derive from translation).
- **Non-Latin scripts** (Cyrillic, Greek, CJK, Arabic, Hebrew, Thai, Indic):
  transliterate the BrandWord into the local script, translate the
  DescriptorWord. A Latin brand string in a Devanagari listing reads as
  foreign noise.
- The keyword-led order from phase 1 holds in every locale: descriptor first,
  brand second.

**Full description: ADAPT the concept list, never invent.** Same concepts,
local words people actually search, still prose. Do not pad with geo terms
("calorie tracker germany") or locale-invented extras; if a concept has no
local search equivalent, drop it.

**video.txt**: a localized YouTube URL if the user recorded per-market
trailers; otherwise copy the default URL or leave empty. Play wants a video
URL, not a playlist or channel, and no extra query params (timecodes). Ads
must be off; privacy public or unlisted; not age-restricted; embeddable.
Source: https://support.google.com/googleplay/android-developer/answer/9866151

### 4. Automated review — this IS the review

```bash
python3 scripts/validate_listing.py fastlane/metadata/android
```

Check every generated file; fix and re-check what fails; report findings:

- char limits per field per locale (`(X/LIMIT)`; over-limit is a hard fail);
- required files present and non-empty (`title.txt`, `short_description.txt`,
  `full_description.txt`);
- short description is not copied verbatim as the full-description opening;
- no comma-separated word-soup blocks;
- verbatim atoms survived byte-identical (a "translated" URL is a 404);
- brand shape: BrandWord present and correctly kept/transliterated;
- spot-check the hard scripts (CJK, RTL, Indic) plus any locale the user
  reads.

### 5. Upload

API path (existing app, service account present):

```bash
python3 scripts/play_api.py update-listings fastlane/metadata/android
# then
python3 scripts/play_api.py listings
```

Report only locales whose read-back title / short / full match the files.

fastlane path:

```bash
fastlane supply --skip_upload_apk --skip_upload_aab \
  --skip_upload_images --skip_upload_screenshots \
  --skip_upload_changelogs \
  --metadata_path fastlane/metadata/android
```

Then read back (`supply init` into a temp dir, or `play_api.py listings`).

Console-manual path (no credentials): give the user a per-locale paste list
and stop. That is a complete phase, not a failure.

Gotchas that cost real time:

- **An API edit is a snapshot.** `edits.insert` copies the live app; you
  mutate the edit; `edits.commit` publishes it. Editing the same app in
  Play Console while the edit is open **discards the API edit**. Official:
  https://developers.google.com/android-publisher/edits
- **The API cannot create the first store listing of a never-uploaded app.**
  Upload at least one APK/AAB via Console first.
- **Commit can take hours to show on the storefront**, same as Console.
- **`changesNotSentForReview`** on `edits.commit` parks the change until
  someone sends it for review in Console. Use it when the user is not
  ready to ship the text.
- **Name collisions** are rarer than on Apple but a locale's translated
  title can still be misleadingly close to another app — fix that one
  locale, save, re-validate.
- **Privacy policy URL is not a listings field.** It lives on App content
  (phase 6). `edits.details` can set `contactWebsite`, `contactEmail`,
  `contactPhone`, `defaultLanguage` — not the privacy policy.

## Listing resource (do not invent fields)

Official `Listing` JSON (edits.listings):

```
language          BCP-47 tag (e.g. "de-AT" in the API docs)
title             localized title
fullDescription   full description
shortDescription  short description
video             promotional YouTube URL
```

HTTP:

- `GET    /androidpublisher/v3/applications/{packageName}/edits/{editId}/listings`
- `GET    /androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}`
- `PUT    /androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}`
- `PATCH  /androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}`
- `DELETE /androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}`

Host: `https://androidpublisher.googleapis.com`. Scope:
`https://www.googleapis.com/auth/androidpublisher`.

## What you must NOT do

- Never emit a keyword field or a comma-separated keyword block.
- Never invent locale codes that are not on the official list above.
- Never translate URLs / emails / the brand form the user locked.
- Never mention pricing, discounts, "#1", "Best of Play", or "free" as a
  promo in any locale.
- Never exceed a char limit "just slightly" — Play rejects or policy-flags
  it, and `validate_listing.py` exits 1.
- Never skip step 2. It is where the silent bugs die.
- Never claim an API write that was not read back.

## Reporting

**Done** / **Problems** / **Needs you**.
