# Automation Architecture — The Impossible Files

Version: 1.1

## Goal
Build a hybrid, semi-automated media production system where human creative approval remains central while AI agents and provider APIs handle repeatable work.

## Team model
### Human owner
- owns platform accounts and billing;
- authorizes credentials locally/CI;
- makes final brand and publishing decisions;
- approves public release.

### ChatGPT
- strategy and creative direction;
- scripts and episode concepts;
- visual direction and prompt design;
- review of analytics and experiments;
- maintenance of core project rules.

### Claude / Claude Code
- long-context consistency;
- lore and character continuity;
- documentation review;
- prompt/script review;
- implementation assistance.

### Codex
- CLI and automation engineering;
- API integrations;
- provider adapters;
- FFmpeg/media composition;
- validation, tests, packaging and operational tooling.

## Source of truth
GitHub is the canonical shared memory.
Chats are not canonical unless decisions are committed to this repository.

## Target production pipeline
1. Episode manifest created.
2. Script approved.
3. Storyboard and shot list approved.
4. Static keyframes generated.
5. Voice generated and timing aligned to the approved storyboard.
6. Video clips generated from prompts/keyframes and the narration timing.
7. Sound effects/music generated or selected from licensed sources.
8. FFmpeg/editor pipeline assembles 9:16 master.
9. Captions rendered/attached.
10. Automated QC runs.
11. Final MP4 uploaded to YouTube as PRIVATE.
12. Human reviews.
13. Human explicitly authorizes publishing.
14. Published metadata is recorded.
15. Performance metrics are periodically recorded and analyzed.

## Provider abstraction
Initial preferred providers:
- Images: OpenAI/ChatGPT image generation or approved image provider.
- Video: Runway API or interchangeable provider.
- Voice: ElevenLabs API or interchangeable TTS provider.
- Composition: FFmpeg locally/CI.
- Distribution: YouTube Data API.

All provider code should live behind adapters, for example:

```text
pipeline/
  providers/
    images/
    video/
    voice/
    youtube/
  compose/
  qc/
  cli/
```

The episode contract must not depend on a specific provider.

## CLI vision
Desired future commands:

```bash
python -m pipeline episode create file-001
python -m pipeline voice file-001
python -m pipeline clips file-001
python -m pipeline compose file-001
python -m pipeline qc file-001
python -m pipeline upload file-001 --privacy private
python -m pipeline publish file-001 --confirm-public
```

These are future command contracts; only validate and voice dry-run are implemented.

`upload` is private-only. `publish` is the only automated path to public visibility and requires **both**:
- `approvals.public_publish.approved = true` (plus `final_qc` approved, status `approved_for_publish`, and an existing private `youtube_video_id`) in the manifest;
- the explicit `--confirm-public` flag on that invocation.

No environment variable can replace either condition.

A later orchestration command may run approved stages:

```bash
python -m pipeline build file-001
```

It must stop on missing approvals or validation failures.

## Episode lifecycle
Valid conceptual lifecycle:

```text
idea
approved
script
storyboard
assets
voice
clips
edit
qc
upload_private
approved_for_publish
published
measured
```

Status transitions should be explicit and stored in the episode manifest.

`status` is the latest stage the episode has entered; work in it may still be in progress. `approved` means the premise is greenlit, not that the script is final. Status never authorizes anything by itself: the schema requires the matching approvals (see `docs/migrations/2026-10-03-episode-manifest-v3.md`).

The lifecycle status lives **only** in the manifest. Episode Markdown files must not keep their own status.

## Human approval gates
Required approval gates and their manifest fields (`approvals.*`):
- final script → `final_script` (required before `storyboard`);
- approved storyboard → `storyboard` (required before `assets`);
- approved interface → `visual_interface` (required before `assets`);
- first appearance/version of a recurring character → `recurring_characters[]` (every ID in `characters` needs an approved entry);
- substantial lore additions → `lore_additions[]`;
- final video QC → `final_qc` (required before `approved_for_publish`);
- public publish → `public_publish` (required before `approved_for_publish` and for any non-private visibility).

Operational gates also pin the exact reviewed files in `artifacts` (`path`, `sha256`). Validation rejects missing or changed files. Changing an upstream artifact invalidates its gate and all dependent gates; rebuild derived media and request review again. See the v3 migration and `docs/file-001-handoff.md`.

Each approved gate records `approved_by`, `approved_at` and `ref` (where the decision is documented). Agents never set a gate to `true` on their own initiative; they only record approvals given by the human owner.

## YouTube integration policy
Use OAuth 2.0.
Default upload privacy: `private`.
The pipeline must never assume public publishing.
`AUTO_PUBLISH` is not a publishing mechanism: it must stay `false`, and any other value is a configuration error. API public publishing only happens through the `publish` gate above; the manual Studio procedure follows the same human approval requirements.
Every upload sets `selfDeclaredMadeForKids` and `containsSyntheticMedia` from the manifest.
YouTube restricts uploads from unverified API projects to private. The human owner may publish manually in YouTube Studio after the same manifest approvals and reviewed-media checks. The CLI flag applies only to API publication; it is not evidence of a manual action. Record manual authorization in the decision log before the action, then record the actual video ID, public visibility and publication time in the manifest. Verify the result before setting `published`.

## GitHub collaboration
Agents coordinate through:
- commits;
- issues;
- PRs for material changes;
- episode manifests;
- decision log.

GitHub Issues may eventually represent production tickets, one per episode or experiment.

## Generated media storage
Do not commit large generated media to Git by default.
Recommended local structure:

```text
output/
  file-001/
    images/
    clips/
    audio/
    captions/
    final/
```

For durable large assets, evaluate Git LFS or external object storage later. The metadata, prompts and checksums should remain in Git.

### Tracked asset record
`episodes/<episode_id>/assets.json` is the committed record of every generated or licensed asset: the reproducibility fields below, plus `sha256` and, for music/SFX, `license`. Its contract is `schemas/assets.schema.json`; FILE #001 starts with an empty registry, not fictional generated assets. `output/<episode_id>/build-manifest.json` is only a local build log and is not tracked.

### Scenes
The approved storyboard is the canonical scene list. Scenes are `## scene-NN` headings (`scene-01`, `scene-02`, … without gaps). Scene count is derived from it and is never stored in the manifest.

## Reproducibility
For each generated asset, record when available:
- episode ID;
- scene ID;
- provider;
- model;
- prompt version;
- source keyframe/reference;
- generation ID/job ID;
- output filename;
- generation timestamp;
- relevant settings.

## Analytics loop
After publishing, record:
- views;
- viewed vs swiped away;
- average view duration;
- average percentage viewed;
- likes/comments/shares;
- subscribers gained;
- traffic geography when useful;
- notable audience comments/theories.

Codex owns collection; ChatGPT owns interpretation; Claude reviews continuity-related implications. Collect at 24 h, 72 h and 7 days after publication (manual collection until an adapter exists). Data API covers basic video statistics; use authorized YouTube Analytics reporting or owner-exported Studio reports for retention, viewed/swiped and subscribers. Record unavailable metrics as null with a reason, never zero. Store timestamp, source, reporting window and video ID in `analytics/file-001/`; this is a collection contract, not a configured automation.

Insights should flow into `analytics/learnings.md`; durable rules may later be promoted into `MASTER_RULES.md`.

## Principle
Automation should reduce repetitive work, not reduce originality.
The studio is optimized for consistent creative quality and learning speed, not bulk AI generation.

## Stage ownership and readiness
The FILE #001 handoff matrix, shot IDs, QC thresholds and revision policy are in `docs/file-001-handoff.md`. The canonical order is assets → voice/timing → clips → edit (including graphics, sound and captions) → QC. Provider names identify tools, not accountable agents. Codex owns technical delivery; ChatGPT accepts creative assets; Claude reviews continuity; the owner alone grants human gates.

Current implementation: manifest/asset validation and voice dry-run only. Generation, composition, QC, upload and publish remain unimplemented. Never describe a planned command as an operational integration.
