# Phase 4 — Custom store listings + experiments

Play-only high leverage. Apple has one product page per locale. Play lets
you show a *different* listing to a *different* user — up to **50** custom
store listings, plus store listing experiments on top. This phase decides
when to split, writes the extra copy, and sets experiment hygiene. It does
not invent an API: custom listings and experiments are **Console-only** as
of the public Play Developer API v3 reference (no `edits.customlistings`
resource). Everything here is planned in files, pasted in Console, and
checked by the user.

Official:

- Custom store listings:
  https://support.google.com/googleplay/android-developer/answer/9867158
- Experiments (Play Console product page):
  https://play.google.com/console/about/store-listing-experiments/
- Preview assets / metadata policy still apply to every listing, every
  translation.

You need a **default store listing published** (and usually the app itself
published or at least past "create the default listing") before Console
will let you create a custom one.

## When to split (and when not to)

A custom listing is worth a slot when the *user in front of the page* wants
a different promise than your default. Fifty is a hard cap — spend them.

**Split when:**

| Targeting | Use it for Glow Up when… |
|---|---|
| Country / region | Germany cares about "Kalorienzähler" and meal-plan culture that the US listing does not mention. One listing can cover multiple countries; **a country can only be on one custom listing at a time**. |
| Search keyword | People arriving from "intermittent fasting" should see fasting-window screenshots, not barcode-scanner screenshots. Pick from Play's known-traffic keywords (and their variation bundles). |
| Unique URL | `https://play.google.com/store/apps/details?id={package}&listing={param}` — landing pages, newsletters, QR codes. `param` is unique across your custom listings; lowercase alphanumerics plus `.` `-` `_` `~`. |
| Ads traffic | Users coming from a Google Ads app campaign. Paste the AdGroup ID; assets should match the ad. Currently strongest on AdMob; do not expect it to match total UAC numbers. |
| Pre-registration | Countries still in pre-reg. Users already on production/testing tracks will not see it. |
| User state | Churned (uninstalled), lapsed (not opened in 28 days), lapsed+churned, non-buyers, one-time / repeat / lapsed buyers (no purchase in 180 days). Re-engagement copy, not acquisition copy. **Unavailable on a brand-new app.** |
| Custom audiences | Groups you defined in Play. Verify the current definition in Console. |

**Do not split when:**

- You only wanted another language. That is a **translation** on the default
  (or on the custom listing), not a new listing. Custom listings are **not**
  auto-translated — pick a default language and add translations yourself.
- You have no distinct promise. Two listings that differ by a synonym are
  two slots burned and a mess to maintain.
- You have not shipped the default listing yet.

Contact details, privacy policy, and category are **shared** across every
listing. You can change name, icon, descriptions, and graphic assets per
custom listing.

## Groups

Console lets you create a listing **group** that shares a pool of assets
(icon, screenshots, descriptions). Updating a group asset updates every
listing in the group. Use a group when the pixels stay the same and only
targeting changes (holiday icon for 12 countries). Use standalone listings
when the promise changes.

The default group is seeded from the default store listing.

## Workflow

1. Confirm the default listing from phase 2/3 is the one you want
   everyone-else to see.
2. Ask the user which splits they actually have traffic for. Do not open
   50 empty listings. A first pass for Glow Up might be:
   - `DE-AT-CH` — country, default `de-DE`, fasting + "Kalorienzähler"
   - `fasting` — search keyword "intermittent fasting" (+ variations)
   - `lapsed` — user state, "what's new since you left" (only if the app
     has users)
   - `ads-macros` — ads traffic, if they run a macros campaign
3. For each approved split, write a mini listing in the same fastlane
   shape, under a parallel tree so it cannot overwrite the default:

```
fastlane/metadata/android-custom/<listing-id>/<locale>/
  title.txt
  short_description.txt
  full_description.txt
  video.txt
  images/…
```

   Same char limits, same policy, same validator:

```bash
python3 scripts/validate_listing.py fastlane/metadata/android-custom/<listing-id>
```

4. Hand the user a Console checklist per listing (Needs you):
   Grow users → Store presence → Custom store listings → Create →
   targeting → paste text → upload graphics → add translations → save.
5. After they publish, ask them to confirm the listing is live for a
   test URL / country. There is no API read-back. "The files are written"
   is not "the listing is live".

Search-keyword listings: Console may offer a Gemini-generated description
from the default listing + the chosen terms. Treat that as a draft. Run it
through the same policy + limit checks; do not ship a word-soup block
Gemini happened to emit.

## Experiments — hygiene

Official Play Console experiments page (verify the current UI path; Google
has been folding experiments into the Store listings view):

- Test **graphics or text**, not both in the same experiment if you want a
  clean read.
- **One variable at a time.** Icon *or* feature graphic *or* short
  description *or* screenshot 1 — not a full redesign vs control. Google:
  "Get the clearest results by testing a single asset at a time."
- **Enough traffic, enough time.** Google: test at least a week (weekday vs
  weekend). Do **not** call a 2-day test a win. Low-traffic apps need longer;
  say so.
- **Metric:** Play Console's experiment UI is the source of truth. For
  years the success metrics were **first-time installers** and **retained
  first-time installers** (acquisition vs 1-day retention). Listing
  *performance reports* moved toward unique-user install / open / pre-reg
  clicks in 2026
  (https://support.google.com/googleplay/android-developer/answer/9859173).
  Pick the metric the experiment screen offers you. Do not invent a
  number from Installs in Statistics and call it the experiment result.
- Apply a winner; do not leave a finished experiment rotting. A clear
  winner gets applied. A tie or a loss is information — ship neither
  "because we ran a test".
- Metadata policy applies to every variant. An experimental "#1 calorie
  tracker" icon is still a violation.
- If Console asks whether assets were created or edited with AI, answer
  honestly. Verify the current wording in the experiment form.

There is no public Play Developer API for creating or reading experiments.
Plan the variants as files, paste them, and put "read the experiment
result in Console" in Needs you.

## What you must NOT do

- Do not claim a custom listing is live because the files exist.
- Do not invent a custom-listing REST path.
- Do not target the same country on two custom listings (Console will
  refuse; don't fight it).
- Do not use a custom listing as a junk drawer for leftover keywords.
- Do not call a 2-day experiment a win.

## Reporting

**Done** / **Problems** / **Needs you** — Needs you is almost always
non-empty here (Console clicks).
