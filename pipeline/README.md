# Studio Pipeline

This directory will contain the executable automation layer for The Impossible Files.

Manifest contract: v3; see `docs/migrations/2026-10-03-episode-manifest-v3.md`. The tracked asset registry is validated against `schemas/assets.schema.json`.

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

## YouTube OAuth connection

After setting `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` in the ignored
local `.env`, authorize the local upload adapter:

```bash
python -m pipeline provider youtube authorize
python -m pipeline provider youtube verify
```

`authorize` opens Google's owner-controlled consent page, requests
`https://www.googleapis.com/auth/youtube` so the adapter can perform an
explicitly approved private upload or change the visibility of that same video,
and stores the refresh token only in the ignored `.env`. `verify` only
exchanges that refresh token for an access token; it neither uploads media nor
changes video visibility.

After the owner has approved final QC, plan a **private-only** upload with an
explicit fiction disclosure. The command is dry-run by default:

```bash
python -m pipeline upload file-001 --description "FILE #001 is a work of fiction from The Impossible Files." --tag mystery
python -m pipeline upload file-001 --description "FILE #001 is a work of fiction from The Impossible Files." --tag mystery --execute
```

`--execute` uploads only the manifest-pinned final MP4 as `private`, disables
subscriber notifications, then records the returned video ID and freezes the
exact metadata under `episodes/<id>/`. It refuses stale QC, an existing video
ID, non-private configuration, missing fiction disclosure, or any
`AUTO_PUBLISH` value other than empty/`false`.

## Public publication

Public publication is a separate command and is dry-run by default. It never
uploads a new file: it changes visibility only for the existing private video
ID recorded by the upload command.

```bash
python -m pipeline publish file-001
python -m pipeline publish file-001 --confirm-public
```

It refuses unless the manifest is at `approved_for_publish`, final QC and the
human `public_publish` gate are approved and pinned to the master MP4 plus the
frozen YouTube metadata. The literal `--confirm-public` is required on the
same invocation. If YouTube blocks API-public videos from an unaudited Google
project, no local lifecycle state is changed; the owner may use YouTube Studio
manually after the same manifest approval, then record and verify the result.

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
- no automatic public publishing;
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
  clips/scene-01-shot-01-take-01.mp4
  ...
  captions/captions.srt
  final/file-001-short.mp4
  build-manifest.json
```

The upload command may then upload `file-001-short.mp4` as **private** only.

Before provider execution, consume the handoff contracts in `docs/file-001-handoff.md`. Voice preflight remains provider-free; it only requires a current final-script approval and does not authorize other stages. General production additionally requires storyboard and interface gates. Compositing includes screen replacement, editorial overlays, sound mixing and captions.
