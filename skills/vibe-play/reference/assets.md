# Phase 3 — Feature graphic, icon, screenshots

Produces (or collects) the pixels a Play listing cannot ship without, plus
the ones that convert. Only **overlay text** is localized; the app UI inside
a screenshot may stay in the default language — the accepted low-effort
tradeoff that captures most of the conversion value. If the user already
has localized UI screenshots, use those instead.

Official preview-asset rules:
https://support.google.com/googleplay/android-developer/answer/9866151

There is no bundled renderer and no Figma URL in this skill. Document the
contract, write any heading copy, validate sizes, upload if credentials
exist. Do not invent a design file.

## What is required vs recommended

| Asset | To publish | For promo / browse eligibility |
|---|---|---|
| High-res icon | required | 512×512, 32-bit PNG (with alpha), ≤1024 KB |
| Feature graphic | required | 1024×500, JPEG or 24-bit PNG, **no alpha** |
| Short description | required (phase 2) | first text on the listing |
| Phone screenshots | min **2** across device types to publish | Google's promo surfaces ask **4+** at ≥1080 px, 9:16 or 16:9 |
| 7-inch / 10-inch tablets | separate slots | include them if the app is a tablet app |
| Promo video | optional | YouTube URL; high-leverage, especially for games |
| TV banner | required only for Android TV apps | 1280×720, JPEG or 24-bit PNG, no alpha |
| Wear / TV / Automotive / XR | only if you distribute there | see official page; do not invent sizes |

Max **8 screenshots per device type**. JPEG or 24-bit PNG, no transparency,
≤8 MB, each side 320–3840 px. The long side may not be more than twice the
short side.

## Fastlane on-disk layout

Matches `fastlane supply` (https://docs.fastlane.tools/actions/supply/):

```
fastlane/metadata/android/<locale>/images/
  icon.png                  # or .jpg — filename stem is `icon`
  featureGraphic.png        # stem `featureGraphic`
  tvBanner.png              # Android TV only
  phoneScreenshots/         # any names; Play shows them in alphanumerical order
  sevenInchScreenshots/
  tenInchScreenshots/
  tvScreenshots/
  wearScreenshots/
```

`supply` also documents a `promoGraphic` filename. The current Play
Developer API `AppImageType` enum does **not** list a promo graphic
(https://developers.google.com/android-publisher/api-ref/rest/v3/AppImageType).
Do not treat `promoGraphic` as required. If a file is sitting there from an
old project, verify in Play Console whether that slot still exists before
uploading it.

## Pixel contract

### Icon — 512×512, 32-bit PNG with alpha, ≤1024 KB

Does not replace the launcher icon; it is the store icon. No badges or text
that suggest ranking, price, or Play programs. No misleading notification
dots or download glyphs. Follow Play's icon design specifications (verify
the current spec in Play Console / the icon help article — do not invent
mask/safe-zone numbers here).

### Feature graphic — 1024×500, JPEG or 24-bit PNG, no alpha

**Required to publish.** Used as the cover for the preview video and on
large-format browse / ads surfaces.

- Keep the focal point **centered**. Official guidance: do not put the logo,
  app name, slogan, or main UI in the cutoff zones at the edges — some
  surfaces crop.
- Do not clone the app icon into the feature graphic (it sits next to the
  icon and looks duplicated).
- Avoid pure white / black / dark gray backgrounds (they disappear into
  Play's chrome).
- Minimize text. Google's own listing guidance: "Minimize your use of text."
- No ranking / price / promo / "Free" / "#1" / award badges.
- No device bezels that will date. No Play badge. No third-party marks
  without permission.
- Localize any burned-in words per language.
- Write alt text (≤140 chars, no "image of") when the Console field is
  available — assistive tech, and Google asks for it.

Glow Up: a 1024×500 plate with the food-log UI large in the center, brand
wordmark small, no "Best calorie tracker 2026" stripe.

### Phone screenshots

To publish: at least two screenshots **across device types**, 320–3840 px
per side, JPEG or 24-bit PNG, no alpha, ≤8 MB.

To be eligible for the large-format recommendation shelves (official
"highly recommended", treated as a requirement for those surfaces):

- Apps: at least **four** screenshots, min 1080 px on the short side.
  Portrait 9:16 (min 1080×1920). Landscape 16:9 (min 1920×1080).
- Games: at least **three** 16:9 or 9:16 at those minima, showing actual
  gameplay.

Preferred working sizes (pick one portrait size and stick to it):

- 1080×1920 (9:16)
- 1242×2208 (older 16:9-ish marketing frames; confirm the long/short ratio
  is ≤2 before upload — 2208/1242 ≈ 1.78, fine)

Do not invent other "required" iPhone-like sizes. If the user exports a
different portrait size inside 320–3840 with ratio ≤2, it is valid.

Tablet: 7-inch and 10-inch are **separate slots**. Official large-screen
guidance (same preview-assets page): 1080–7680 px, 16:9 or 9:16, and "a
minimum of 4 screenshots" to demonstrate the large-screen experience. If
the app is a tablet app, fill both slots. If it is phone-only, say so and
skip — do not upload stretched phone shots into the tablet slots.

### Promo video

`video.txt` is a YouTube URL. Not a playlist, not a channel, no timecode
params. Public or unlisted, ads off, not age-restricted, embeddable. First
30 seconds may autoplay muted — put the actual in-app experience in the
first 10 seconds. Localized videos per market when the user has them.

## Heading-burn rules (when the user wants marketing frames)

Same spirit as vibe-aso, Play sizes.

Ask for three things and **confirm all three before translating anything**:

1. **Background PNGs** in a project folder: `phone_1..N.png` and — if the
   app is a tablet app — `seven_1..N.png` / `ten_1..N.png`, exported with
   the heading layer hidden. Sizes: phone 1080×1920 or 1242×2208 (or any
   valid Play size the user already uses); feature graphic 1024×500 as
   `feature_en.png` (or per-locale).
2. **The English headings, in order** — one per screenshot. Confirm the
   order matches the PNG numbering. If the user has no headings yet, draft
   them from the phase-1 vocabulary: short benefit statements
   (`Track every calorie`, `See your macros at a glance`) — verb + noun,
   at most one ALL-CAPS emphasis word. Taglines only if needed; official
   cap is **taglines should not take up more than 20% of the image**.
   Prefer no tagline when the UI already says the thing.
3. **Two font colors** as odd/even for alternating light/dark frames.

Store as `headings.json` (`{ "<locale>": ["heading 1", ...] }`, default
locale first) and `app.json` (`{ "name": "Glow Up", "colors": { "odd":
"#FFFFFF", "even": "#1A1A1A" } }`) next to the PNGs.

### Translating the headings

- Anchor to phase 2's vocabulary. A screenshot that says "Kalorien" while
  the short description ranks for "Kalorienzähler" wastes the reinforcement.
- Headings are marketing keywords, not UI strings — translate by meaning
  and search value.
- ALL-CAPS emphasis mirrors only into scripts that have case; drop it for
  CJK, Indic, Arabic, Hebrew, Thai.
- Keep headings **short**. Agglutinative languages produce long words —
  tighten the copy, don't ship a 12 px caption.
- Generate ALL locales in one pass; review via char length + spot-checks
  of CJK / RTL / Indic. No per-language human gate unless the user asks.
- In-app UI inside the shot does not have to be localized; **overlay
  taglines do**.

### What must not appear on any graphic

From preview-assets + metadata + best-practices:

- Ranking / awards / "#1" / "Best of Play" / "Million Downloads"
- Price / promo / "Free" / "Discount" / "Sale"
- Call-to-action ("Download now", "Install now")
- Unattributed testimonials
- Sexually suggestive imagery, graphic violence, drug use — listing must
  be suitable for a **general audience** even if the app is not for kids
- Notification-bar junk (carrier names, unread badges). Battery / Wi-Fi /
  cell icons should be full if the status bar is visible
- People tapping the device unless the core use is off-device
- Play Store (or any store) badge

## API image types (do not invent)

Official `AppImageType`
https://developers.google.com/android-publisher/api-ref/rest/v3/AppImageType

```
phoneScreenshots
sevenInchScreenshots
tenInchScreenshots
tvScreenshots
wearScreenshots
icon
featureGraphic
tvBanner
```

Upload (media):

```
POST https://androidpublisher.googleapis.com/upload/androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}/{imageType}
```

List:

```
GET https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{packageName}/edits/{editId}/listings/{language}/{imageType}
```

A language with no listing is a no-op on upload. `edits.images` has
`delete`, `deleteall`, `list`, `upload` only — no patch. Replacing a set
means deleteall + upload, or `supply` (which replaces, not appends).

Read back after upload: `list` the image type and check count + sha256
against the local files. `play_api.py list-images` does this.

## Validate

```bash
python3 scripts/validate_listing.py fastlane/metadata/android \
  --feature-graphic path/to/featureGraphic.png
```

The script fails (exit 1) if a passed feature graphic is not 1024×500.
It does not need network. It does not upload.

## Upload

```bash
fastlane supply --skip_upload_apk --skip_upload_aab \
  --skip_upload_metadata --skip_upload_changelogs \
  --metadata_path fastlane/metadata/android
```

Or `python3 scripts/play_api.py upload-images …` for one locale / one type,
then `list-images` to confirm.

Hazards:

1. **Validate one locale first.** Cheap proof the sizes, auth, and listing
   language exist.
2. **`supply` image upload replaces the current images of that type**, it
   does not append. An interrupted run can leave a locale with two
   screenshots. Count after.
3. **Feature graphic without alpha.** A 32-bit PNG with an alpha channel
   is the wrong file. Flatten it.
4. **Default-locale graphics are what Play shows when a translation has
   no localized graphics.** If you add text translations without localized
   feature/screenshots, the default pixels show — including English
   taglines on a German listing. Either localize the overlays or keep
   taglines off the pixels.

## Reporting

**Done** / **Problems** / **Needs you** (export the pixels, record the
YouTube URL, confirm tablet yes/no).
