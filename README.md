# Vibe Play — a Claude Code skill

You vibe-coded the Android app. Now vibe the Play listing.

The Google Play sibling of [vibe-aso](https://github.com/Kronop/vibe-aso) (Dan Kulkov / Kronop). Same job, other store: one skill that takes an Android app from "ready to submit" to a fully-optimized, fully-localized Google Play presence — driven from Claude Code, end to end.

1. **Keyword research** — popularity/difficulty-driven, intent-matched, per market. Decides what your **title** and **short description** say. Remaining concepts are woven into the **full description**. There is no hidden keyword field on Play.
2. **Store metadata in Play's translation locales** — keyword-led title, benefit-led short description, a full description that reads like prose (never a comma-separated word soup). Reviewed by automated checks, not vibes.
3. **Listing assets** — feature graphic (required), high-res icon, phone screenshots, and tablet slots when the app is a tablet app. Heading-burn rules with Play sizes. Localized screenshot text per language.
4. **Custom store listings + experiments** — Play-only high leverage. Split by country, user state, search keyword, or unique URL. A/B test one variable at a time.
5. **In-app localization** — `res/values/strings.xml` (or RN/Expo i18n JSON). Detectors catch the bugs fluent output hides (format-specifier drift, brand atoms, URL/email verbatim, RTL/CJK/Indic spot-checks).
6. **Submission checklist** — every field the Play Developer API / fastlane supply can set gets set and verified; everything it can't (Data safety UI, content rating, target audience, ads, App access, …) becomes an explicit manual-steps list instead of a silent gap.

No signup, no SaaS — you bring your own Play Console access (and, optionally, a Play Developer API service-account JSON). Translations run on Claude subagents by default (or your own DeepSeek / OpenAI-compatible key if you prefer).

This skill was adapted from [Kronop/vibe-aso](https://github.com/Kronop/vibe-aso). If you also ship on iOS, use that one. The two skills share a tone, a phase map, and the same Glow Up calorie-tracker worked example — they do not share rules. Apple's name / subtitle / hidden keyword field is a different machine from Play's title / short description / full description.

## Install

**Run these two commands in Claude Code one at a time — wait for the first to succeed before pasting the second.**

Step 1 — register the marketplace:

```
/plugin marketplace add bdseerden/vibe-play
```

Step 2 — install the plugin:

```
/plugin install vibe-play@vibe-play-marketplace
```

If the install summary says `Plugin is now active.` you're done; if it says `Run /reload-plugins to activate.`, run that (or restart Claude Code).

Or clone directly (no plugin manager):

```bash
git clone https://github.com/bdseerden/vibe-play /tmp/vibe-play
cp -R /tmp/vibe-play/skills/vibe-play ~/.claude/skills/vibe-play
```

## Use

Open Claude Code in your app's repo and say what you want:

```
do the Play ASO for my app
```

…or any slice of it: "find keywords for my calorie tracker", "localize my Play listing", "write the feature graphic and screenshots", "set up a custom listing for Germany", "localize the Android strings", "get my listing ready for submission". Claude loads the skill on its own from the description.

First run walks you through a short setup wizard:

- **Play Developer API service account** (optional). Play Console → Setup → API access / Users and permissions, plus a Google Cloud service-account JSON. Stored in `~/.vibe-play/play-sa.json`, chmod 600, never in a repo, never printed. Without it, the skill writes fastlane files and a Console-manual checklist — that path is first-class, not a consolation prize.
- **Translation engine** — Claude subagents (default, zero setup), DeepSeek, or any OpenAI-compatible API.
- **Keyword data source** — a Play-capable ASO tool with popularity/difficulty data (Astro or AppTweak / Sensor Tower / AppFigures / similar), or honest degraded mode without one.

## Requirements

Nothing up front — each phase checks its own prerequisites (`scripts/check_setup.sh` prints exactly what's missing and the fix command), and you only need the tools for the phases you actually use:

| You want | You need |
|---|---|
| Keyword research | nothing (a Play-capable ASO data tool with popularity/difficulty makes it much stronger) |
| Metadata generation | nothing |
| Metadata / image upload | `fastlane` (`gem install fastlane` or `brew install fastlane`) **or** Play Console by hand |
| API read-back | a Play Developer API service-account JSON at `~/.vibe-play/play-sa.json` |
| In-app localization | the project itself (`res/values/strings.xml`, or i18n JSON for RN/Expo) |

The skill writes the standard fastlane supply layout (`fastlane/metadata/android/<locale>/…`), so if you deliver with something else, everything up to the upload step still works as-is.

## What it costs

Nothing beyond what you already pay: your Claude usage, and — only if you choose the DeepSeek engine — cents for a full in-app cascade. The Play Developer API is free. There is no vibe-play account.

## Design principles

- **Fan out, then verify.** Every localization pass covers all chosen locales at once and is reviewed by automated detectors + targeted spot-checks — a human can't review 40 languages, and reviewing one proves nothing about the other 39.
- **Read-back or it didn't happen.** Every API write is verified with a GET. Every thing the API can't do lands in an explicit manual-steps list.
- **Intent over volume.** A keyword is worth ranking for only when the person typing it wants *your* app.
- **Play is not a reskin of Apple.** Title (30) + short description (80) + full description (4000) are **all indexed**. There is no hidden keyword field. A comma-separated keyword block is a Metadata policy violation.

## License

MIT. Copyright 2026 Bo Seerden / bdseerden.

Adapted from [vibe-aso](https://github.com/Kronop/vibe-aso) by Dan Kulkov (Kronop), MIT.
