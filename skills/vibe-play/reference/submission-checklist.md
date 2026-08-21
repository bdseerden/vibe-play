# Phase 6 — Submission: fill everything, verify everything, list what's manual

A new app's Play Console page is almost entirely empty, and **most of the
fields that block a first review have no public API**. The failure mode this
checklist kills is the **silent skip** — a run that sets "the important
fields", reports success, and leaves the app blocked on Data safety or
content rating. Two rules:

> **1. An item is done when a GET (or a Console screenshot the user confirms)
> shows the intended value** — never when the PUT returned 2xx.
> **2. Every item the API cannot set goes, explicitly, into a final
> "MANUAL STEPS REMAINING" list.** An item you didn't do is reported FAILED
> or MANUAL — never omitted.

The Play Developer Publishing API **cannot create the first APK/AAB** and
**cannot flip an app from unpublished → published** or sign the legal
consents. Official: https://developers.google.com/android-publisher/edits
("you will have to upload at least one APK through the Play Console before
you can use this API").

## Who can set what

**[api]** = Play Developer API v3 (and/or `fastlane supply` wrapping it).
Set it AND read it back, except where noted write-only.
**[manual]** = Console only; goes in the final list.
**[api-write-only]** = an official write endpoint exists; there is no GET.
Confirm in Console.

| # | Surface | Who | Notes |
|---|---|---|---|
| 1 | Default language | [api] | `edits.details` field `defaultLanguage` (BCP-47, e.g. `en-US`) |
| 2 | Title / short / full description / video, all locales | [api] | `edits.listings` — phase 2 |
| 3 | Feature graphic, icon, screenshots | [api] | `edits.images` — phase 3 |
| 4 | Contact website / email / phone | [api] | `edits.details`: `contactWebsite`, `contactEmail`, `contactPhone` |
| 5 | Privacy policy URL | [manual] | App content. **Not** an `edits.listings` or `edits.details` field. Active, non-geofenced URL, also linked in-app when you collect personal data |
| 6 | Category / tags | [manual] | Store settings. Verify current fields in Console |
| 7 | Data safety | [api-write-only] | `POST /androidpublisher/v3/applications/{packageName}/dataSafety` body `{ "safetyLabels": "<csv>" }`. Format: https://support.google.com/googleplay/android-developer/answer/10787469 (export a CSV template from Console; do not invent columns). Response is empty — **verify in Console** |
| 8 | Content rating questionnaire | [manual] | App content → Content ratings (IARC). No public edits resource |
| 9 | Target audience and content | [manual] | App content. Declare ads + app access + privacy policy **first**. https://support.google.com/googleplay/android-developer/answer/9867159 |
| 10 | Ads declaration | [manual] | App content. "Contains ads" label is user-visible |
| 11 | App access (login-gated) | [manual] | Instructions + demo account if any part is restricted |
| 12 | News / magazine declaration | [manual] | If in scope. https://support.google.com/googleplay/android-developer/answer/16189314 |
| 13 | Government apps | [manual] | If developed by/for a government entity. Verify the current form in App content |
| 14 | Financial features | [manual] | If the app has any financial feature. App content form |
| 15 | Health apps | [manual] | Health declaration. Medical-device apps declare as such; wellness apps (Glow Up) need the "not a medical device…" description disclaimer when that policy applies |
| 16 | Photos / videos permissions | [manual] | If the app reads photos/videos. Prefer the system photo picker unless a core feature needs broad access |
| 17 | SMS / Call Log and other sensitive permissions | [manual] | Permissions declaration form after the bundle is uploaded |
| 18 | Custom store listings + experiments | [manual] | Phase 4. No public API |
| 19 | Release (internal / closed / open / production) | [api] | `edits.tracks` / `edits.bundles` / `edits.apks` — only if the user asked this skill to ship a binary. Otherwise leave to their existing release lane |
| 20 | Store listing experiments start | [manual] | Phase 4 |
| 21 | Final review / managed publishing send | [manual] | Publishing overview. API `edits.commit` publishes the *edit*; it does not replace "Send for review" for App content items |

If Console shows a declaration this table doesn't name, **add it as MANUAL
with the Console label** — do not drop it, do not invent an API path for it.

## API writes this phase will actually do (when credentials exist)

1. Open an edit: `POST /androidpublisher/v3/applications/{packageName}/edits`
2. Put listings from the fastlane tree (`edits.listings.update` per locale).
3. Put images the user provided (`edits.images.upload` per type).
4. Patch details if the user gave contact info / default language:
   `PATCH /androidpublisher/v3/applications/{packageName}/edits/{editId}/details`
5. `POST …/edits/{editId}:validate` then `POST …/edits/{editId}:commit`
   (or abandon with `DELETE …/edits/{editId}` if validate fails).
6. Read back: `listings.list`, `details.get`, `images.list`. Report only
   what those GETs show.
7. Data safety CSV **only** if the user exported a filled template and
   asked to push it. Then tell them to open App content → Data safety and
   confirm. Do not author a CSV from vibes.

`play_api.py` implements the paths above and refuses anything else.

## The traps, in the order they bite

- **App content is a stack.** Target audience refuses to start until ads,
  app access, and privacy policy are done. Do them in that dependency
  order.
- **Data safety is required** for closed / open / production (internal-test
  only is the usual exception — verify in Console). Apps that collect
  nothing still file "no collection" and still need a privacy policy that
  says so.
- **`applications.dataSafety` is write-only.** A 2xx empty body is not
  proof the form the user sees is right. Console-verify.
- **Listing must be suitable for a general audience** even when the app is
  not for kids. A calorie tracker whose feature graphic looks like a kids'
  cartoon can get pushed into Families policy. Glow Up's pixels should look
  like a tool for adults.
- **Health disclaimer.** If Glow Up is *not* a regulated medical device,
  the description should say it does not diagnose, treat, cure, or prevent
  any medical condition (Health Content and Services policy). If it *is*
  a medical device, that is a different declaration and proof of
  clearance — stop and get the user.
- **Login-gated apps without App access instructions** bounce in review.
  Demo account, or an explicit "no account needed" note.
- **An in-flight Console edit discards an API edit.** Don't click around
  in Console while `play_api.py` has an open edit.
- **Commit is not storefront-instant.** Hours, same as Console.
- **Managed publishing** can hold listing changes. If the user has it on,
  `edits.commit` still only queues; they must hit Publish.

## Copy rules Play actually rejects on

- No unattributed testimonials.
- No "#1" / "Best of Play" / award badges / "Million Downloads".
- No price or promo in any text or graphic ("Free", "50% off").
- No impersonation / official-app claims.
- No keyword-stuffed word blocks.
- Metadata policy applies to every translation.
- Don't call the app "free" in the listing if a paywall hard-gates first
  launch.

Sources:
https://support.google.com/googleplay/android-developer/answer/9898842
https://support.google.com/googleplay/android-developer/answer/13393723

## Final output — required shape

1. A table with one row per checklist item: **SET** (read-back shown) /
   **FAILED** (attempted, read-back disagrees — never reclassified as
   MANUAL to look done) / **MANUAL** / **N/A (reason)**.
2. Then, verbatim heading:

```
MANUAL STEPS REMAINING
1. Privacy policy URL — Policy → App content → Privacy policy
2. Ads declaration — App content → Ads
3. App access — App content → App access (demo account if login-gated)
4. Target audience and content — App content (after 1–3)
5. Content rating questionnaire — App content → Content ratings
6. Data safety — fill / confirm in App content (even if the CSV was POSTed)
7. News / government / financial / health / photos-videos / SMS — only the
   forms Console shows for this app
8. Category / store settings
9. Custom listings + experiments (phase 4) if any
10. Send for review / Publish (Publishing overview)
```

For a first release this list is **never empty** — an empty MANUAL list
means the run skipped something.

## Reporting

**Done** / **Problems** / **Needs you**.
