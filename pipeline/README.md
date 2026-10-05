# Studio Pipeline

This directory will contain the executable automation layer for The Impossible Files.

## Current foundation

The first implementation uses Python's standard library only. This keeps manifest
validation reproducible before provider SDKs are introduced. Run it from the
repository root:

```bash
python -m pipeline episode validate file-001
python -m pipeline episode validate file-001 --json
python -m pipeline voice file-001
python -m unittest pipeline.tests.test_manifest_validator
```

`episode validate` applies `schemas/episode.schema.json` and studio-specific
safeguards: canonical episode IDs, repository-relative working-file paths, no
secret-shaped manifest keys, and human approval before public privacy. The CLI
also reserves the planned stage commands, but they intentionally make no provider
calls until their adapters are implemented. The future `upload` surface accepts
only `--privacy private` at this stage.

## ElevenLabs connection check

After setting `ELEVENLABS_API_KEY` in the untracked local `.env`, confirm the
key and its **Voices: Read** permission without creating audio or using speech
credits:

```bash
python -m pipeline provider elevenlabs verify
```

This command reads the accessible-voices metadata only. Narration and sound
effect generation remain deliberately unimplemented until their own explicit,
approval-gated commands are added.

## Voice preflight

`python -m pipeline voice <episode-id>` is a provider-neutral dry-run. It
validates the manifest and refuses unless the human owner has recorded
`approvals.final_script.approved = true`. It creates no files, reads no
credentials, and makes no network request. A provider implementation is not
enabled yet, so this command only reports the deterministic narration target.

## Planned modules

```text
pipeline/
  cli/
  providers/
    images/
    video/
    voice/
    youtube/
  compose/
  captions/
  qc/
  utils/
```

## Responsibilities
- read/validate an episode manifest;
- generate approved assets through provider adapters;
- generate narration and SFX;
- compose media with FFmpeg;
- run automated QC;
- upload final output to YouTube as private;
- record provider/job/output metadata back to episode working files.

## Non-goals
- no automatic public publishing by default;
- no secrets in repository files;
- no direct dependency between episode manifests and one provider implementation;
- no mass generation of generic videos without creative approval.

## Implementation order
1. Manifest validator.
2. CLI skeleton.
3. ElevenLabs voice adapter.
4. FFmpeg composition utilities.
5. Runway video adapter.
6. Caption pipeline.
7. QC module.
8. YouTube OAuth/private-upload adapter.
9. End-to-end `build` command.

## Definition of done for v1
Running a documented CLI command for `file-001` should eventually produce:

```text
output/file-001/
  audio/narration.mp3
  clips/scene-01.mp4
  ...
  captions/captions.srt
  final/file-001-short.mp4
  build-manifest.json
```

The upload command may then upload `file-001-short.mp4` as **private** only.
