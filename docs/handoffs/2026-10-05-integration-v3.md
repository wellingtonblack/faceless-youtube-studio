# Handoff — Integration of local `main` with PR #1 (manifest v3)

Date: 2026-10-05
Branch: `claude/integrate-v3` (merge of local `main` `5c19155` + `origin/main` `fbbb350`)
Producer: Claude Code. Review: human owner. Next accountable: owner (approvals), then Codex (items in section 4).
This branch grants **no** approval. It records state and what the owner needs to re-sign.

## 1. Why integration was needed
| | local `main` (`5c19155`, 2026-10-05) | `origin/main` (`fbbb350`, PR #1) |
|---|---|---|
| Manifest | v2, status `assets`, `final_script` approved | v3, status `script`, every operational gate `false` |
| Approvals | recorded as decision-log entries (2026-10-03/04) | must pin reviewed files by SHA-256 (`docs/file-001-handoff.md`) |
| Asset registry | 3 entries, old format | v1 schema, empty |

## 2. How conflicts were resolved
| File | Resolution | Reason |
|---|---|---|
| `episodes/file-001/manifest.json` | PR #1 (v3) unchanged: status `script`, all operational gates `false` | v3 is the active contract. Agents may not bind approval hashes on the owner's behalf. |
| `production/storyboards/file-001-storyboard.md` | PR #1 content, header renamed **v1.2 — awaiting owner approval** | Both sides had called different content "1.1". PR #1 changed creative content the owner had not approved (below). |
| `docs/visual/anomaly-message-interface.md` | Local `main` version, byte-identical | This is the v1.2 the owner approved (decision log, 2026-10-03). PR #1 made no content change. |
| `episodes/file-001/assets.json` | Converted the 3 local entries to registry v1 | Each has provider, model, job ID, prompt, timestamp, settings and checksum. All 3 checksums match the files on disk. |
| `docs/decision-log.md` | Kept both histories in order, plus one integration entry | Nothing deleted. |

## 3. Owner re-approval checklist
The v3 rule: *edited files need renewed owner approval; never refresh hashes under an existing approval.*

| Gate | What the owner approved before | What changed since | Action |
|---|---|---|---|
| `final_script` | script v1.0 (2026-10-03) | PR #1 changed **only the version line** (1.0 → 1.1); narration and beats identical | Re-approve v1.1 |
| `storyboard` | local v1.1 (2026-10-03) | **Creative changes:** (a) scene-01 uses three *simultaneous stacked panels* instead of "panels or hard cuts"; (b) scene-07: the ground woman *keeps her gaze down and never looks up* (before: "she slowly looks up from it"); (c) shot/take naming | Review (a) and (b), then approve v1.2 |
| `visual_interface` | v1.2 (2026-10-03) | nothing (byte-identical) | Bind the hash once the CRLF issue is fixed (4.1) |
| Selected assets | scene-06 keyframe, scene-04 keyframe, scene-06 clip (2026-10-03/04) | registered as `selected: true`, `review_ref: docs/decision-log.md` | Re-confirm after the storyboard re-approval: change (b) does not affect scenes 04/06 |

My review of the PR #1 storyboard changes: both improve the causal logic. In (b), a woman looking up at the end could be read as "she looked at the Moon too", which blurs the look→message rule. In (a), simultaneous panels show "the same second" better than sequential cuts. I recommend approving them, but it is the owner's decision.

## 4. Blockers and handoffs to Codex

### 4.1 Approval hashes break across operating systems (blocker for binding any gate)
The validator hashes raw bytes (`hashlib.sha256(file.read_bytes())`). The repo has **no `.gitattributes`** and this Windows machine uses `core.autocrlf=true`, so working-tree text files are CRLF here and LF in CI (Linux). Verified: the script, storyboard and interface spec each contain 85–112 CRLF lines in this checkout. A hash taken here fails in CI, and vice versa.

Fix options (Codex, then the owner binds the hashes):
- (a) add `.gitattributes` forcing `eol=lf` for `*.md`, `*.json`, `*.svg` and renormalize; or
- (b) normalize line endings before hashing text artifacts, and document it in the v3 migration.

Coordinate with any open working-tree changes before renormalizing.

### 4.2 Nine media files on disk without provenance
`output/file-001/` has 12 files; 3 are registered. These 9 have no prompt, job ID or review record in the repo, so they were not registered (the handoff forbids guessing):
- `clips/`: `scene-01-global-message.mp4`, `scene-03-reaction.mp4`, `scene-03-reaction-v2.mp4`, `scene-04-normal-moon.mp4`
- `images/`: `scene-01-global-message-keyframe.png`, `scene-01-global-message-keyframe-v2.png`, `scene-03-reaction-keyframe.png`, `scene-03-reaction-keyframe-v2.png`, `scene-05-stream-grid-keyframe.png`

Codex should register them with real job IDs and prompt versions from provider history, or mark them as discarded.

Note that v3 requires **three separate shots** for scene-01 and for scene-03. A single `scene-01-global-message.mp4` or two `scene-03-reaction` takes may not cover them. Check against the storyboard v1.2 once it is approved.

### 4.3 File naming
Registered paths keep their existing names (e.g. `scene-06-moon-reveal.mp4`). The new convention is `scene-NN-shot-MM-take-TT.mp4`. Renaming would change the paths the registry and decision log point to, so it was left to Codex. The checksums would stay valid, since renaming doesn't change bytes.

### 4.4 Registry field gap
`schemas/assets.schema.json` has no field for the prompt location. To keep provenance, the 3 entries store it as `settings.prompt_path`. Codex may promote it to a proper field.

### 4.5 Stale tests on local `main`
Two `test_voice_planner` tests on local `main` failed only because they assume `final_script` is not approved. On this branch, `final_script` is pending again, consistent with v3.

## 5. What did not change
- Canon D1–D6, lore approvals, the narration text, the publishing state (private, nothing uploaded).
- Codex's uncommitted work in the main working tree (`pipeline/compose/`, ElevenLabs adapter, `assets/`) is untouched and not included here.
