# Anomaly Message Interface — Specification

Version: 1.0 — **awaiting owner approval** (required before FILE #001 asset generation)
Canon basis: decision D6 (`docs/proposals/2026-10-03-file-001-continuity.md`) and `docs/visual-bible.md`, "Interfaces, telas e mensagens"
First use: FILE #001, storyboard scenes 02, 07 and 08

## Purpose
This is the fictional, in-world screen that shows anomalous messages on phones. It must:
1. read instantly in a Short (under 1 s for up to four words);
2. feel classified and anomalous, matching The Impossible Files;
3. **never** be mistaken for a real emergency alert, operating-system screen or government warning system.

"Anomaly Message Interface" is an internal production name. No name, sender or app label ever appears on screen.

## Hard exclusions (must NOT resemble)

| Real system | Elements we must not use |
|---|---|
| iOS emergency/government alerts | top banner or lock-screen notification card; rounded translucent cards; system fonts (SF family); headers like "Emergency Alert"/"Government Alert"; app-style alert icon; OK/Dismiss buttons |
| Android emergency alerts | modal dialog box; warning-triangle or exclamation icons; headers like "Extreme alert"/"Severe alert"/"Emergency alert"; OK button; Roboto/system typography |
| Government/public warning systems (any country) | agency names, seals, flags or crests; words such as ALERT, EMERGENCY, WARNING, PRESIDENTIAL, EXTREME, SEVERE, AMBER, PUBLIC SAFETY, TEST; yellow/orange hazard colors; the alert attention signal (two-tone ≈ 853 Hz + 960 Hz) or alert vibration cadence |

General rules:
- No real OS chrome: no status bar, clock widget, notification shade, app icons or home indicator.
- No real phone brand or logo.

## Layout (full-screen takeover)
The message replaces the **entire** screen. It is not a banner, card or dialog.

```text
┌──────────────────────────┐
│ 03:17:00 UTC             │  meta line: small mono, white 60%
│                          │
│                          │
│  DON'T LOOK              │  message: uppercase, bold mono, white,
│  AT THE MOON.█           │  left-aligned block in the upper-middle;
│                          │  red block cursor after the last character
│                          │
│                          │
│                          │  (bottom ~20% kept clear for Shorts UI)
└──────────────────────────┘
```

- **Background:** solid near-black, no texture or gradient. A faint scanline is allowed only during the entry flicker.
- **Meta line:** `03:17:00 UTC` at the top left. It is the only element besides the message.
- **Message:** at most 2 lines and 3 words per line, left-aligned, starting at about 12% from the left edge and about 38% from the top.
- **Red element:** one solid red block cursor (`█`) directly after the final character. It is the only red on screen. Red is never a header, bar, border or icon.
- **Nothing else:** no buttons, icons, sender, logo or brand symbol.

## Color (provisional, interface only)

| Token | Value | Use |
|---|---|---|
| `ami-black` | `#0B0B0B` | background |
| `ami-white` | `#F4F4F4` | message text |
| `ami-white-60` | `#F4F4F4` at 60% | meta line |
| `ami-red` | `#E0161E` | block cursor only |

The owner directed black/white/red for this interface on 2026-10-03. The overall brand palette in `docs/brand-bible.md` is still formally "in exploration"; these tokens do not lock it.

## Typography
- **Message:** IBM Plex Mono Bold, uppercase.
- **Meta line:** IBM Plex Mono Regular.
- **License:** SIL Open Font License 1.1. Record it in `episodes/<id>/assets.json`.

### Legibility minimums (final 1080×1920 frame)
- Full-screen interface shots: message cap height ≥ 7% of frame height (≈ 135 px).
- Phone-in-hand shots: the screen must be ≥ 40% of frame height. Otherwise cut to a full-screen insert.
- Contrast: white on near-black only. No text over imagery.
- Hold time: ≥ 2 s for a message of up to four words.

## Motion
- **Entry:** hard cut on, with a 2-frame scanline flicker. No slide-in, drop-down or bounce (these read as OS notifications).
- **Message 1** (`DON'T LOOK AT THE MOON.`): the cursor blinks at 1 Hz.
- **Message 2** (`WE SAW YOU TOO.`): a 3-frame horizontal displacement glitch on entry, then **completely still**. The cursor stays solid and does not blink. The stillness is the unnerving difference.
- **Exit:** hard cut.

## Sound

| Sound | Spec |
|---|---|
| First notification | short, dry, digital single tone (~200 ms), original. Many layered copies form the scene-01 cascade. |
| **Second-message tone** | distinct and unnerving: low sub-tone bed (≈ 60–120 Hz) with a slightly detuned high partial, reversed swell (~0.8 s) into an abrupt cut, total ≈ 1.2 s. Followed by true silence. |
| Prohibited | emergency/public-warning attention signals or anything close to them; any real OS, phone-maker or carrier tone; sirens. |

All sounds must be original or licensed, and recorded in the asset record with source and license.

## Production method
- Render the interface as a **2D graphic layer** (motion graphics or FFmpeg/editor overlay) and composite it onto phone screens or use it full-frame.
- Never ask the video model to generate the screen text. Generated text is unreliable and can drift toward real OS UI.
- Phones in generated clips should show a plain glowing or blank screen, which is replaced in compositing.
- Compositing/overlays belong to the edit stage and are owned by Codex; implementation is still pending. See `docs/file-001-handoff.md`.

## Archive overlay (editorial, different from the interface)
Editorial overlays (`03:17:00 UTC` in scene-01, `FILE #001 — ARCHIVED` in scene-09) belong to the archive/narration layer, **not** to the in-world sender (D3). They must look different from this interface:
- centered, letter-spaced sans (e.g., Inter SemiBold, OFL), white;
- thin horizontal rules above and below;
- no block cursor, no monospace and no red.

## Approval checklist
- [ ] Mock-up frames of messages 1 and 2 reviewed at phone size.
- [ ] Side-by-side check against current iOS, Android and public-warning alert screens. Use private reference only; do not commit third-party screenshots.
- [ ] Second-message tone reviewed against emergency attention signals.
- [ ] Owner approval recorded in `approvals.visual_interface`, pinning this file hash; decision-log reference included.

## Open items
- Brand symbol (`docs/brand-bible.md`) is not designed yet. It is not used in this interface.
- The pipeline needs a compositing/overlay stage for screen inserts and text overlays. Handoff to Codex.
