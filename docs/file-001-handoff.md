# FILE #001 — Production handoffs

Version 1.0 · 2026-10-03 · Operational correction authorized by owner.
This document defines delivery contracts, not human creative approval or completion.
Lifecycle status and human approvals live only in the manifest. Current readiness must
be read from that file, never inferred from this table. Canon D1–D6 is unchanged.

## Responsibility matrix

| Stage | Accountable agent / reviewer | Input | Output | Done when |
|---|---|---|---|---|
| Manifest | Codex | Brief, canon, decision log | Manifest v3, asset registry | Validation passes; referenced files exist |
| Script | ChatGPT / Claude | Canon D1–D6 | Versioned final script | Owner approves exact script hash |
| Storyboard | ChatGPT / Claude | Approved script | Nine scenes, shot list, timing | Owner approves storyboard and interface hashes |
| Keyframes | Codex executes / ChatGPT directs and accepts | Approved storyboard/interface | Reference images and registry entries | Creative review recorded; character/Moon continuity checked |
| Voice and timing | Codex / ChatGPT and Claude review | Approved narration, selected neutral voice | Narration, word timing and timing plan | English checked; timing fits approved windows, no Archivist |
| Clips | Codex + video provider / ChatGPT and Claude | Accepted keyframes and narration timing | Shot/take clips | Required shots covered; selected takes reviewed and registered |
| Sound | Codex executes / ChatGPT directs | Sound brief | Music/SFX assets | Sources/licenses recorded; first/second tones distinct |
| Composition | Codex + FFmpeg / ChatGPT | Selected clips, graphics and audio | 9:16 master | Screen replacements, exact text, continuity and mix checked |
| Captions | Codex / Claude | Narration and final timeline | SRT and captioned master | Correct English, sync and mobile legibility |
| Automated QC | Codex | Master and registry | qc-report.json | Technical thresholds below pass; report pins master hash |
| Private upload | Codex + YouTube API | Technical QC, master, metadata | Private video and ID | Actual private visibility verified; ID recorded |
| Final review | Owner / agents assist | Private video, master and QC report | final_qc approval or revision list | Owner approves exact reviewed files |
| Publication | Owner authorizes / Codex executes API | Final QC, frozen metadata, private video ID | Public video | Human gate plus CLI flag for API; manual Studio procedure below |
| Record result | Codex | Verified publication result | ID, UTC timestamp, privacy and lifecycle | Manifest matches actual platform state |
| Measurement | Codex collects / ChatGPT interprets | Published video, authorized reports | Dated metrics and learnings | Source, time window, missing-data reasons and evidence recorded |

Providers and FFmpeg are execution tools; they are not accountable agents.
The implementation currently supports validation and voice dry-run only.

## Shot IDs and output naming

| Scene | Required shot IDs | Content |
|---|---|---|
| scene-01 | shot-01, shot-02, shot-03 | Night, morning, midday phones in simultaneous panels |
| scene-02 | shot-01 | First-message 2D graphic |
| scene-03 | shot-01, shot-02, shot-03 | Friends, window man, morning woman |
| scene-04 | shot-01 | Normal Moon, window-man camera |
| scene-05 | shot-01 through shot-06 | Six stream sources; optional shots 07–09 if explicitly added before storyboard approval |
| scene-06 | shot-01 | Closer Moon matching scene-04 |
| scene-07 | shot-01, shot-02 | Observer's phone lights; non-observer keeps looking down |
| scene-08 | shot-01 | Second-message 2D graphic |
| scene-09 | shot-01 | Editorial archive sting |

Full IDs concatenate scene and shot: `scene-01-shot-01`.
Generated clips use `output/file-001/clips/scene-NN-shot-MM-take-TT.mp4`.
Graphics use the same shot IDs under `images/`. A composited scene render may use
`scene-NN.mp4`, but cannot overwrite a raw take. Caption/master paths:
`output/file-001/captions/captions.srt`, `output/file-001/final/file-001-short.mp4`.
All produced assets get a unique registry ID; no entries for media not yet produced.

## Handoff envelope and acceptance

Each focused commit/PR or linked handoff note must identify episode ID, source commit,
input paths and hashes, output asset IDs/hashes, producer, review reference, unresolved
items and next accountable agent. The receiver verifies these inputs before working.
Only one agent edits an episode manifest at a time; reconcile against latest main
before merging. Agent creative review selects takes through `selected` + `review_ref`
in `assets.json`. It does not grant human approval. Dependency IDs refer to registered
source assets; record provider/model/settings/prompt version/job ID when available,
and use null with an explanation in the handoff when not available.

`schemas/assets.schema.json` defines the registry. Codex must check local bytes and
all required shot coverage immediately before composition. Registry-only validation
can run on a checkout without large media; it does not establish build readiness.
Missing media must be restored from durable storage, not regenerated silently under
an existing ID or hash. Before costly generation, the owner chooses/configures a
durable media store and provider billing limits; record storage location and retry
budget in the handoff. Resume existing provider jobs by job ID to avoid duplicate charges.

## Approval binding and revisions

Operational gates use `artifacts: [{"path": "...", "sha256": "..."}]`.
The validator hashes Markdown, JSON and SVG after normalizing line endings to LF;
all other artifacts, including media, use exact bytes on disk. Do not refresh hashes under an existing
approval; edited files need renewed owner approval. Required bindings:

- `final_script`: script.
- `storyboard`: script and storyboard.
- `visual_interface`: interface specification.
- `final_qc`: script, storyboard, interface, registry, master and QC report.
- `public_publish`: master and `episodes/file-001/publishing-metadata.json`.

Freeze publishing metadata only when a real private upload ID exists. This JSON includes
`title`, `youtube_video_id`, `selfDeclaredMadeForKids`, `containsSyntheticMedia`,
plus any actual description/tags sent by the future adapter. The publish adapter must
use exactly the frozen metadata; no silent overrides.
When an input changes, mark its gate and dependent gates false, clear their audit
records/artifacts, return to the earliest affected lifecycle stage and rebuild only
affected outputs. Script changes invalidate storyboard, final QC and publishing;
interface/storyboard changes invalidate final QC and publishing; master/metadata
changes invalidate their corresponding final approvals. Preserve history in Git.
Original lore approvals stay intact unless the approved canon changes.

## Technical QC and human review

FILE #001 defaults: MP4/H.264, yuv420p, 1080×1920, constant 30 fps, 28–35 seconds;
AAC audio, 48 kHz stereo; target integrated loudness −14 LUFS ±1 and true peak ≤−1 dBTP.
Codex implements decoding, stream/duration, loudness, caption bounds/sync and asset
coverage checks. Speech captions must align within 150 ms; no cue beyond runtime.
Silence and black frames in scenes 05, 08 and 09 are intentional; QC must compare
against the approved timeline rather than reject them indiscriminately.
The QC JSON records each check, measurement, pass/fail, tool version and master SHA-256.
These are implementation acceptance thresholds; automated QC is not implemented yet.
Human review checks mobile legibility, hook, Moon phase/scale, look→message causality,
fictional interface, exact message spelling, distinct tones, licensed sources and
absence of Archivist. Fiction context must be explicit in the publishing description;
a fictional interface alone is not proof viewers will understand the work is fiction.

## Publication procedures

API: private upload → owner final QC → owner public authorization →
`approved_for_publish` → `publish --confirm-public` → verify result → `published`.
The future command revalidates current hashes, frozen metadata, approvals and private
video ID immediately before changing visibility. AUTO_PUBLISH never authorizes release.
Studio: same approvals and reviewed media/metadata; owner authorization recorded before
manual publication, then verify actual video ID/visibility/time and update manifest.
The CLI flag applies only to API execution. Neither path invents authorization or results.

## Measurement

Collect at 24 h, 72 h and 7 days after actual publication. Codex records source,
video ID, collected-at UTC, reporting interval, metrics and unavailable-data reasons
under `analytics/file-001/`; ChatGPT adds evidence-backed interpretations to learnings.
Use Data API for supported basic counts; authorized Analytics/Studio exports for
retention, viewed/swiped, AVD and subscriber metrics. Null means unavailable, not zero.
No recurring collection task has been configured by this documentation change.
