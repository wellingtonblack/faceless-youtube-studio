# Proposal — FILE #001 Continuity and Early-Season Diversity

Date: 2026-10-03
Author: Claude Code (review), decisions by human owner (`wellingtonblack`)
Status: **Part A APPROVED** · **Part B DECIDED in part** (see "Owner decisions for Part B"; replacement titles provisional)

Related files:
- `content/season-01/file-001.md`
- `episodes/file-001/manifest.json`
- `docs/story-bible.md`
- `docs/visual-bible.md`
- `characters/archivist/profile.md`
- `docs/decision-log.md`

---

## Part A — Approved canon decisions

These were raised in the 2026-10-03 continuity review of FILE #001 and approved by the owner on the same date. They are now canon and have been applied to the files listed under each decision.

### D1 — 03:17 means 03:17 UTC
**Problem found:** "every phone on Earth" at "3:17 AM" cannot be true locally everywhere. The draft also showed a night-time global livestream montage, while half the planet would be in daylight.

**Decision:**
- When 03:17 marks a global event, it means **03:17 UTC**, a single global instant.
- Visuals must show different local times and daylight conditions around the world.
- Never imply it is 3:17 AM locally everywhere.

**Notes for the script:**
- The public title `Everyone Received the Same Message at 3:17 AM` stays unchanged (approved in the decision log). The on-screen timestamp should read `03:17 UTC`, so the title and video stay consistent.
- Reference local times for 03:17 UTC vary with the date and daylight-saving time. Writers must compute them for the in-story date instead of reusing a fixed list.
- Daytime locations may not be able to see the Moon. This can be used as a visual beat (people searching a bright sky), but it is optional.

**Applied to:** `docs/story-bible.md` (recurring motif), `content/season-01/file-001.md`, manifest `lore_tags` and `approvals.lore_additions`.

### D2 — Direct consequence for looking
**Problem found:** the warning was about *looking*, but the payoff (the Moon moves) affected everyone equally, so looking had no consequence.

**Decision:** after looking at the Moon, the people who looked receive a second message:

`WE SAW YOU TOO.`

Keep it unsettling and unexplained. Do not reveal who "we" are, what "too" refers to, or what happens next.

**Applied to:** `content/season-01/file-001.md`, manifest `approvals.lore_additions`.

### D3 — End sting: `FILE #001 — ARCHIVED`
**Problem found:** the draft sting `FILE #001 HAS BEGUN` was sent by the in-world sender. That implied the anomaly knows our editorial file numbering and that a "file" is an event rather than a record.

**Decision:**
- Use `FILE #001 — ARCHIVED` as the end sting. It is an editorial/archive overlay, **not** a message on the in-world phones.
- Do **not** use `FILE #001 HAS BEGUN`.
- Rule: in-world senders and entities never reference the `FILE #NNN` numbering.

**Applied to:** `content/season-01/file-001.md`, `docs/story-bible.md` (continuity rules).

### D4 — The Archivist is not introduced in FILE #001
**Problem found:** the manifest's voice preset `archivist-v1` silently made The Archivist the narrator. That skipped the "first appearance of a recurring character" approval gate.

**Decision:**
- No Archivist narration, voice or visual appearance in FILE #001.
- Voice configuration stays neutral (`voice.preset: null` until a neutral narrator preset is approved).
- The first appearance of any recurring character requires its own approved canon decision.

**Applied to:** manifest (`characters: []`, `voice.preset: null`), `characters/archivist/profile.md`, `content/season-01/file-001.md`.

### D5 — Moon-related overlap
**Problem found:** FILE #001 already shows the Moon moving. The approved season list also contains #006 `The Moon Moved` and #008 `Something Was Detected Behind the Moon`, which makes three Moon files out of 15.

**Decision:**
- Flag FILE #006 and FILE #008 for rewrite or replacement.
- Do not delete them yet.
- Create a proposal for more diverse early episodes (see Part B).

**Applied to:** `docs/story-bible.md` (season list annotated), `content/season-01/file-001.md` (expansion paths).

### D6 — Phone/UI visuals
**Problem found:** a global message to every phone resembles real emergency-alert systems. Imitating them risks confusion with real events and misuse of platform/government UI.

**Decision:**
- Do not imitate real emergency alerts, iOS emergency screens, Android emergency alerts or any government system.
- Use a fictional, branded anomaly-message interface.

**Open item:** the fictional interface has not been designed yet. It needs a visual study and approval, recorded in `docs/visual-bible.md`, before the assets stage of FILE #001.

**Applied to:** `docs/visual-bible.md`, `content/season-01/file-001.md`.

---

## Part B — Proposal: more diverse early episodes (NOT CANON)

Everything in this part is a **proposal**. Nothing here changes `docs/story-bible.md` until the owner approves it.

### Current anomaly-category balance of the 15 approved files
Using the categories in `docs/story-bible.md` (some files fit more than one):

| Category | Files |
|---|---|
| Planetary/cosmic | #001, #002, #006, #008, #012, #015 |
| Spatial | #003, #007, #010, #014 |
| Temporal | #001, #004, #009 |
| Technological | #001, #004, #011 |
| Human | #005, #013 |
| Biological/environmental | #015 (borderline) |

Observations:
- Planetary/cosmic content dominates, and the Moon alone appears in three files.
- Biological/environmental is nearly empty, although it is a defined category.
- Human anomalies about collective memory are listed in the bible's categories but have no file.

### Candidate replacements for #006 and #008
The owner may choose any of these, or none:

| Option | Category | Source | Note |
|---|---|---|---|
| The Entire World Forgot His Name | Human (collective memory) | already in `content/backlog.md` | Fills an empty category; strong single-sentence premise. |
| Every Bird on Earth Landed at the Same Second | Biological | new | Global-instant structure is close to #001; avoid 03:17 here so the motif stays rare. |
| The Rain Fell Upward for One Minute | Environmental | new | Visually immediate; cheap to read without captions. |
| His Shadow Moved Before He Did | Human/temporal | new | Small-scale, intimate; contrasts with the global files. |
| Nobody Is Allowed to Open This Door | Spatial | already in backlog | **Not recommended**: spatial and door premises already crowded (#003, #007, #014). |

### Options for the existing Moon files
- **#006 The Moon Moved:** (a) replace; or (b) keep as a *later* direct follow-up to FILE #001, only if #001 clearly outperforms. It must still work on its own (story bible: "Um vídeo deve funcionar sozinho").
- **#008 Something Was Detected Behind the Moon:** (a) replace; or (b) move to a later season, after the audience has seen non-cosmic files.

**Recommendation:** replace #006 and #008 in the first season with one human-memory file and one biological/environmental file. Keep both Moon premises in the backlog as possible follow-ups for FILE #001.

### Other drift found (not decided)
Titles differ between `content/backlog.md` and the approved list in `docs/story-bible.md`:
- `He Received a Photo Taken Tomorrow` vs #004 `He Received a Phone Call From Tomorrow`
- `Everyone Froze Except One Person` vs #005 `Everyone Froze Except Him`
- `He Woke Up as the Last Human on Earth` vs #013 `He Woke Up as the Last Human Alive`
- `Every Clock on Earth Stopped at the Same Time` vs #009 `Every Clock Stopped at the Same Time`

Proposal: the story bible list is canonical for approved files, and the backlog should match it or mark items as variants.

### Owner decisions for Part B (2026-10-03)
1. **#006 `The Moon Moved`: REPLACED.** Provisional replacement: `The Rain Fell Upward for One Minute` (awaiting title confirmation).
2. **#008 `Something Was Detected Behind the Moon`: DEFERRED** to a later lore slot, outside the first 10 releases, as a possible consequence of FILE #001. The slot is provisionally filled by `The Entire World Forgot His Name` (awaiting confirmation).
   - Note: the owner's instruction called this file "NASA Detected Something Behind the Moon". The canonical title has no agency name, and the brand bible forbids real agency branding, so the canonical title is kept.
3. Replacement ideas with different visual themes are in `content/backlog.md`, "Temporada 1 — substituições de slots".
4. Backlog/story-bible title alignment: **still open.**
