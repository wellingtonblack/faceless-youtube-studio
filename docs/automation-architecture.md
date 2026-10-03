# Automation Architecture — The Impossible Files

Version: 1.0

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
5. Video clips generated from prompts/keyframes.
6. Voice generated.
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
npm run studio -- episode create 001
npm run studio -- voice 001
npm run studio -- clips 001
npm run studio -- compose 001
npm run studio -- qc 001
npm run studio -- upload 001 --privacy private
npm run studio -- publish 001 --confirm-public
```

or equivalent Python CLI.

`upload` is private-only. `publish` is the only path to public visibility and requires **both**:
- `approvals.public_publish.approved = true` (plus `final_qc` approved, status `approved_for_publish`, and an existing private `youtube_video_id`) in the manifest;
- the explicit `--confirm-public` flag on that invocation.

No environment variable can replace either condition.

A later orchestration command may run approved stages:

```bash
npm run studio -- build 001
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

`status` is the latest stage the episode has entered; work in it may still be in progress. `approved` means the premise is greenlit, not that the script is final. Status never authorizes anything by itself: the schema requires the matching approvals (see `docs/migrations/2026-10-03-episode-manifest-v2.md`).

The lifecycle status lives **only** in the manifest. Episode Markdown files must not keep their own status.

## Human approval gates
Required approval gates and their manifest fields (`approvals.*`):
- final script → `final_script` (required before `storyboard`);
- first appearance/version of a recurring character → `recurring_characters[]` (every ID in `characters` needs an approved entry);
- substantial lore additions → `lore_additions[]`;
- final video QC → `final_qc` (required before `approved_for_publish`);
- public publish → `public_publish` (required before `approved_for_publish` and for any non-private visibility).

Each approved gate records `approved_by`, `approved_at` and `ref` (where the decision is documented). Agents never set a gate to `true` on their own initiative; they only record approvals given by the human owner.

## YouTube integration policy
Use OAuth 2.0.
Default upload privacy: `private`.
The pipeline must never assume public publishing.
`AUTO_PUBLISH` is not a publishing mechanism: it must stay `false`, and any other value is a configuration error. Public publishing only happens through the `publish` gate above.
Every upload sets `selfDeclaredMadeForKids` and `containsSyntheticMedia` from the manifest.
YouTube restricts uploads from unverified API projects to private. Until the API project is audited, the human owner may publish in YouTube Studio and then record the result in the manifest.

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
`episodes/<episode_id>/assets.json` is the committed record of every generated or licensed asset: the reproducibility fields below, plus `sha256` and, for music/SFX, `license`. `output/<episode_id>/build-manifest.json` is only a local build log and is not tracked.

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

Insights should flow into `analytics/learnings.md`; durable rules may later be promoted into `MASTER_RULES.md`.

## Principle
Automation should reduce repetitive work, not reduce originality.
The studio is optimized for consistent creative quality and learning speed, not bulk AI generation.
