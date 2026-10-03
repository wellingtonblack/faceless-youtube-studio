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
```

or equivalent Python CLI.

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

## Human approval gates
Required approval gates:
- final script;
- first appearance/version of a recurring character;
- substantial lore additions;
- final video QC;
- public publish.

## YouTube integration policy
Use OAuth 2.0.
Default upload privacy: `private`.
The pipeline must never assume public publishing.
`AUTO_PUBLISH=false` is the default operational policy.

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
