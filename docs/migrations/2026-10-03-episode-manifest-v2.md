# Migration — Episode Manifest v1 → v2

Date: 2026-10-03
Schema: `schemas/episode.schema.json` (`schema_version: 2`)
Approved by: human owner (`wellingtonblack`), as the "mechanical fixes" listed in the FILE #001 continuity review
Related: `docs/proposals/2026-10-03-file-001-continuity.md`, `docs/automation-architecture.md`

## Why
v1 had several problems:
- No way to record the human approval gates required by `docs/automation-architecture.md`.
- Two publish-approval sources that could disagree.
- A hard-coded `scene_count` with no source.
- A `script_path` that pointed to a missing file.
- No YouTube disclosure metadata.

## Changes

| Change | v1 | v2 | Reason |
|---|---|---|---|
| Added `schema_version` | — | required, `const: 2` | Enables future migrations. |
| Added `characters` | — | required array of recurring-character IDs | Makes a character appearance explicit. `[]` means none. |
| Added `approvals` | — | required object with `final_script`, `recurring_characters[]`, `lore_additions[]`, `final_qc`, `public_publish` | One field per human gate. A gate set to `approved: true` must record `approved_by`, `approved_at` and `ref`. |
| Removed `publishing.public_publish_approved` | boolean | — | Duplicated the publish approval. `approvals.public_publish` is now the only source of truth. |
| Added `publishing.selfDeclaredMadeForKids` | — | required boolean | Mirrors YouTube Data API `videos.status`. |
| Added `publishing.containsSyntheticMedia` | — | required boolean | Mirrors YouTube Data API `videos.status`; altered/synthetic content disclosure. |
| Removed `video.scene_count` | integer | — | Derived from the storyboard instead (see below). |
| Conditional rules | none | `allOf` / `if-then` | See the next table. |

### Conditional rules enforced by the schema

| Condition | Requirement |
|---|---|
| status ≥ `storyboard` | `approvals.final_script.approved = true` |
| status ∈ {`approved_for_publish`, `published`, `measured`} | `final_qc` and `public_publish` approved |
| `youtube_privacy` ∈ {`unlisted`, `public`} | `public_publish` approved (unlisted counts as non-private) |
| status ∈ {`published`, `measured`} | `youtube_privacy = public`, `youtube_video_id` and `published_at` present |

`status` remains the full canonical lifecycle (unchanged, see `AGENTS.md`). It describes the latest stage entered and **never authorizes anything by itself**. The schema prevents status and approvals from disagreeing.

## FILE #001 manifest migration
- `schema_version: 2` added.
- `script_path`: `content/scripts/file-001-everyone-received-the-same-message-at-0317.md` (missing) → `content/season-01/file-001.md` (existing).
- `voice.preset`: `archivist-v1` → `null` (canon decision D4: no Archivist in FILE #001).
- `characters: []`.
- `video.scene_count: 9` removed. The value had no source; the v0.1 beat sheet had 6 beats and no storyboard exists.
- `approvals.lore_additions`: the approved decisions D1 (03:17 UTC) and D2 (`WE SAW YOU TOO.`). All other gates are `false`.
- `publishing.public_publish_approved: false` removed; `selfDeclaredMadeForKids: false` and `containsSyntheticMedia: true` added.
- `status` stays `script`: the beat sheet is v0.2 and the final script is not approved.

## Derived scene count
The approved storyboard (`storyboard_path`) is the canonical scene list. Each scene is a heading `## scene-NN` (`scene-01`, `scene-02`, … without gaps). Scene count = number of such headings. The same IDs are used for `output/<episode>/clips/scene-NN.mp4` and in the asset record.

## Tracked asset record
`episodes/<episode_id>/assets.json`, committed to Git. It holds one entry per generated or licensed asset with the fields listed under "Reproducibility" in `docs/automation-architecture.md`, plus `sha256` and, for music/SFX, `license`. `output/<episode>/build-manifest.json` stays a local, untracked build log. Defining `schemas/asset-record.schema.json` is an open task for the pipeline owner.

## Handoff to the pipeline owner (Codex)
The dependency-free validator in `pipeline/manifest_validator.py` was already being adapted to v2 in a parallel change (its 9 tests pass against this schema). Remaining rules that JSON Schema cannot express:

1. **Characters ↔ approvals:** every ID in `characters` must have an entry with `approved: true` in `approvals.recurring_characters`.
2. **Working files exist by stage:** `script_path` must exist once status is past `script`; `storyboard_path` must exist once status is past `storyboard`.
3. **Storyboard scenes:** past `storyboard`, the storyboard must contain ≥1 `## scene-NN` heading, numbered without gaps.
4. **Public publish gate (CLI):** `upload` stays private-only. A separate command, e.g. `studio publish file-001 --confirm-public`, must refuse unless **all** of these hold:
   - the `--confirm-public` flag is present on that invocation;
   - `approvals.public_publish.approved` and `approvals.final_qc.approved` are true;
   - status is `approved_for_publish`;
   - a private `youtube_video_id` exists.
5. **`AUTO_PUBLISH`:** no environment variable may enable public publishing. If `AUTO_PUBLISH` is set to anything other than `false` or empty, the CLI should exit with a configuration error.
6. **Small bug:** `const`/`enum` comparison in Python treats `1 == True`. JSON distinguishes them; compare with a bool-aware check.

Note: YouTube keeps videos uploaded through unverified (unaudited) API projects private. Until the project is audited, the publish step may have to be done by hand in YouTube Studio. The manifest must still be updated (`status`, `youtube_privacy`, `published_at`) and pass validation.
