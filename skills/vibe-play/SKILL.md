---
name: vibe-play
description: Full-funnel Google Play store-listing optimization for an Android app — keyword research (popularity/difficulty driven), a keyword-led title and short description with remaining concepts woven into the full description, Play metadata localized into the official translation locales, feature graphic and localized screenshots, custom store listings and experiments, and in-app string localization. Use when the user wants to "do the ASO", "do the Play ASO", "find keywords", "localize my app / my Play listing / my screenshots", "pick a title and short description", "set up a custom listing", "run a store listing experiment", or is preparing a Google Play submission.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Vibe Play — the whole Play listing funnel, from Claude Code

You built an Android app. This skill takes it the rest of the way: what people
search, what your listing says in every language, what the feature graphic and
screenshots say, which custom listings and experiments to run, and what the
app itself says once installed.

It is organized as six phases. Run them in order for a new app, or jump to the
one the user asked for. Each phase has a reference file with the full rules —
**read the reference file before starting a phase**; this page is the map, not
the territory.

| Phase | Does | Reference |
|---|---|---|
| 0 SETUP | one-time wizard: Play Developer API service account, translation engine, data source | below |
| 1 RESEARCH | keyword research → title keyword, short-desc keyword, description concept list | `reference/keyword-research.md` |
| 2 METADATA | title / short description / full description / video URL, default locale first, then all chosen Play locales | `reference/metadata.md` |
| 3 ASSETS | feature graphic + icon + phone (and tablet) screenshots, localized headings | `reference/assets.md` |
| 4 CUSTOM LISTINGS + EXPERIMENTS | Play-only splits (geo / keyword / user state / URL) and A/B hygiene | `reference/custom-listings.md` |
| 5 IN-APP | localize the app's own UI strings (`strings.xml` or RN/Expo i18n JSON) | `reference/app-localization.md` |
| 6 SUBMIT | upload, verify, and the manual-steps list the Play API can't do | `reference/submission-checklist.md` |

A worked example runs through every reference file: a calorie-tracking app
whose brand name is **Glow Up**. Every rule is illustrated on it; none of the
rules are specific to it.

This skill is the Google Play sibling of [vibe-aso](https://github.com/Kronop/vibe-aso).
Do not import Apple rules. Play indexes the title, the short description, **and**
the full description. There is no hidden keyword field. A comma-separated
keyword block is a Metadata policy violation.

## Phase 0 — Setup wizard (first run, or whenever a check fails)

Run `scripts/check_setup.sh` first. If everything passes, skip to the phase the
user wants. Otherwise walk ONLY the missing pieces, in this order:

**1. Play Developer API service account** (needed by phases 2, 3, 6 if you
want API upload + read-back; not required — the Console-manual path is
honest and complete).

The Play Developer Publishing API can only edit an app that already has at
least one APK/AAB uploaded through Play Console. A brand-new unsubmitted
package has no API surface yet; write the files and use Console.

If the user wants API access:

1. In Google Cloud, enable **Google Play Android Developer API**
   (`androidpublisher.googleapis.com`) on the Cloud project linked to the
   Play Console developer account.
2. Create a **service account**, download its JSON key (once).
3. In Play Console → Users and permissions, invite the service account's
   email and grant it permission to view and edit store listing / app
   information (Admin is simplest; least-privilege is fine if listing +
   metadata are checked).
4. Then:

- Store the JSON at `~/.vibe-play/play-sa.json`, `chmod 600`.
- Create `~/.vibe-play/` with `chmod 700`.
- Write `~/.vibe-play/config.json` (`chmod 600`):

```json
{
  "play": {
    "package_name": "com.example.glowup",
    "service_account_path": "~/.vibe-play/play-sa.json"
  },
  "translation": { "engine": "subagents" },
  "keyword_source": "manual"
}
```

- Verify with `python3 scripts/play_api.py ping` → must print `OK` (mints a
  token; no write). Then, if the package already exists on Play,
  `python3 scripts/play_api.py listings` → must print live locales.

If credentials are missing, say so and continue on the Console-manual path:
write the fastlane files, validate them, and hand the user a paste/upload
checklist. Do not pretend an API write happened.

**Security is non-negotiable:** the key lives in `~/.vibe-play/`, never inside
any project directory, never in a repo, never in a commit, never echoed to the
terminal, never pasted into a file the user might share. If the user pastes
the JSON contents into chat, save it and tell them to revoke-and-regenerate
if this conversation ever leaves their machine.

**2. Translation engine** (phases 2, 3, 5). Ask via AskUserQuestion:

- **Claude subagents** (default; recommended) — translations are generated by
  spawned subagents, batched per locale. No extra account, no extra key. Cost
  is the user's existing Claude usage.
- **DeepSeek API** — cheapest for very large volumes (a whole in-app catalog ×
  40 locales runs on cents). Key goes to `~/.vibe-play/deepseek-key`
  (`chmod 600`), config: `{"engine": "deepseek", "api_key_path":
  "~/.vibe-play/deepseek-key", "base_url": "https://api.deepseek.com", "model":
  "deepseek-chat"}`.
- **Any OpenAI-compatible API** — same shape: `{"engine": "openai",
  "api_key_path": "...", "base_url": "...", "model": "..."}`. The user brings
  whatever provider they like.

For API engines, verify the key works with one tiny request before any long
run. For DeepSeek specifically, **check the account balance, not just the
key** — a valid key on an empty account fails every request with `HTTP 402`,
and it will do so 30 minutes into a cascade rather than up front
(`check_setup.sh` does this).

**3. Keyword data source** (phase 1). The research method needs, per keyword:
**popularity** (search volume proxy), **difficulty**, and ideally "how many
apps use this in their title/short description". Ask what the user has:

- **Astro** (or any Play-capable ASO tool with an MCP / export) — best when
  connected; the reference file maps each step to the lookups, not to one
  vendor's UI.
- **Another ASO tool** (AppTweak, Sensor Tower, AppFigures, Mobile Action…) —
  the method is identical; the user runs the lookups in their tool and pastes
  numbers when asked.
- **No tool** — phase 1 still works but degrades honestly: Play's own search
  suggestions + competitor listings give the keyword *candidates*, and the
  skill says plainly that popularity/difficulty calls are guesses. Recommend
  getting a data tool before betting the app **title** on a keyword.

Store the answer in config as `"keyword_source": "astro" | "manual" | "none"`.

## Cross-phase laws

These hold in every phase; the reference files repeat them where they bite.

1. **Fan out to all locales in one pass, review by automated checks.** Never
   pause a localization run for a per-language human review unless the user
   explicitly asks for one. A human cannot review 40+ languages, and reviewing
   one language proves nothing about the other 39. The review that works:
   char-limit checks, format-specifier parity, verbatim-atom checks,
   same-as-source detection, plus spot-checks of the hard scripts (CJK, RTL,
   Indic) — all defined in the reference files.
2. **Ask which locales, once, in phase 2.** Default: the official Play
   translation list in `reference/metadata.md`. The user may cut the set
   (e.g. top-15 markets); whatever is chosen there is the set for screenshots
   and in-app strings too. Do not re-ask per phase. If you cannot verify a
   locale code against that list, do not invent it — say "verify in Play
   Console".
3. **Play Console is the source of truth** for anything Google owns — live
   metadata, images, review state, Data safety. Pull from it before editing
   (`play_api.py listings` or `fastlane supply init`); never trust a possibly
   stale local copy over the live listing.
4. **Sweep once, slice locally.** The Play API is rate-limited and an in-flight
   Console edit **discards** an API edit in progress (official Edits docs).
   Anything that walks many locales gets dumped to a local file once; every
   follow-up question is answered from the file, never by re-sweeping because
   the analysis changed. Do not edit the same app in Console while an API
   edit is open.
5. **A 2xx is not verification.** After any write, GET the field back and
   check the value. Report only what a read-back confirmed. (`applications.dataSafety`
   is write-only — that one is called out as Console-verify, not faked.)
6. **Character limits are hard**: title 30, short description 80, full
   description 4000. Show counts as `(X/LIMIT)`. Validate after writing, per
   locale. The validator **fails** (exit 1) on any over-limit file — never
   "just slightly".
7. **Some strings never localize**: Android / Google product names the user
   wants kept (Pixel, Wear OS when they're product names), URLs, email
   addresses, the brand name as the user styles it, package names, product
   codes. A translated support email is a dead mailto; a "translated" URL is a
   404.
8. **Chunk long-running work.** Translation cascades and bulk uploads run as
   many small foreground commands (per locale, per batch), never one giant
   call that outlives the shell's patience. Report only what is verified on
   disk or read back from the API — "the cascade is running" is not a result.
9. **Never emit a Play "keyword field".** Play does not have one. Title +
   short description + full description are the three indexed surfaces. A
   comma-separated block (`car racing, car driving, race cars…`) is a
   Metadata policy violation. Remaining concepts are woven into natural
   prose in the full description; they are not listed.

## Scripts and assets in this skill

```
scripts/check_setup.sh       # PASS/WARN/FAIL per prerequisite, with fix commands
scripts/validate_listing.py  # hard-fail on over-limit / empty required files
scripts/play_api.py          # documented Play Developer API client (edits.listings / edits.images / edits.details)
reference/*.md               # the six phase guides — read before the phase
```

There is no bundled screenshot renderer and no invented Figma URL. Phase 3
documents the asset contract and validates sizes; the user (or their existing
pipeline) produces the pixels.

## Reporting

End every phase with three short sections: **Done** (what happened, verified),
**Problems** (what surprised you and how it was handled), **Needs you** (manual
steps only the user can do — or "nothing"). Keep it outcome-level; skip file
paths and internals unless asked.
