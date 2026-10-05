# FILE #001 — Codex status handoff

Date: 2026-10-05
Episode: `file-001`
Producer: Codex
Source commit: `b0839c76c66e5c6d99b44d1581eaf49cc5fdd536` (`claude/integrate-v3`)
Next accountable agent: owner (fresh hash-bound approvals), then Codex (provenance recovery and gated production).

## Envelope

Input artifacts inspected:

| Path | SHA-256 (canonical text hash where applicable) |
|---|---|
| `content/season-01/file-001.md` | pending owner binding after the line-ending fix |
| `production/storyboards/file-001-storyboard.md` | pending owner binding after the line-ending fix |
| `docs/visual/anomaly-message-interface.md` | pending owner binding after the line-ending fix |
| `episodes/file-001/assets.json` | inventory updated in this handoff commit; must be included in any future final-QC binding |

Output registry entries (all local bytes verified when present):

| Asset ID | SHA-256 |
|---|---|
| `scene-01-global-message-keyframe-v1` | `458ef117b65193af357edaf7f55ad0585eb2893fa79ad74de71b5b073c15d001` |
| `scene-01-global-message-keyframe-v2` | `620b8e40b14573c2084d7fc22739bccd769e18012094dadb761b3fcf52b39b7c` |
| `scene-01-global-message-keyframe-v3` | `817607fb83d4ed0c3797e429abffc9b9c14f4437cd568513f98feb606f1f334c` |
| `scene-01-global-message-clip-v1` | `c73c897015280ec8ef3cc65597507facdc624c06e88e09f1623527827944f4e1` |
| `scene-01-global-message-clip-v3` | `0b5d1078e3067fa245b138c34059e344ae1b5f0c8a048231479dfa5c645d4038` |
| `scene-03-reaction-keyframe-v1` | `6804e2a7f10e8da4ebcb94438a259e665fede49af789a7107aaa86e1eb5236d3` |
| `scene-03-reaction-keyframe-v2` | `1240388ec45a79be8e330208f28a1fe72eca31e7a8b2492f28d5bae5fcc71ce1` |
| `scene-03-reaction-keyframe-v3` | `f10f6b5e4da61df88e0e9d7a83ccfcb2f49ac146d9d2e2170a34a7d59c581603` |
| `scene-03-reaction-clip-v1` | `db694627f1730535f6c6bd21fbfe10cd16607e51026b6ac9c553514364cdf349` |
| `scene-03-reaction-clip-v2` | `140fc7e89fff8ee539175637bafcc5992f67cc1078ce8c7a260114889a6bc5c2` |
| `scene-03-reaction-clip-v3` | `615e9261e4d4007cad78a71b82b2f32b42d10e47931c98226c4aa26c68ec08e9` |
| `scene-04-normal-moon-keyframe-v1` | `abf60e5f8482b515e7bcc723fc91e6deb8e6bdcdafd3c34e495feb42f0c1675c` |
| `scene-04-normal-moon-clip-v1` | `d574cba0674a2006637b0187b495a3bb09bb1a5e65f66c565ac6c7748576d720` |
| `scene-05-stream-grid-keyframe-v1` | `cd7721d9d2260fd570f5584174559ee8849e28b907ceaaf371f2a98afd3f95cd` |
| `scene-05-stream-grid-clip-v1` | `affca80d1121745ef3e4c7df955da5852fefdc13e54b8b4287396dc3da284f97` |
| `scene-06-moon-reveal-keyframe-v1` | `494d522e1d85ab4ae45bb2c357d41ff708f2a9978a6131dea0ae15f3ca7cfba6` |
| `scene-06-moon-reveal-clip-v1` | `b6640900b7e1a60311d7c016d65d27bc6b4160d9297d7f46c44c357954c4a2a1` |
| `scene-07-consequence-keyframe-v2` | `9514fba561c92a7f8c2081679486bdb3ccf352bf5d86fe0237f157d03b72bed2` |
| `scene-07-outside-keyframe-v1` | `8b1db1916a552e876efb96bfc5345dfd0ba378cf811d20c472ced653eae4afe2` |
| `scene-07-consequence-clip-v2` | `57161b2ddda16f1c9a5b8fc5358a400fcaa7906c16182737a2511de6a3872de9` |
| `narration-full-v1` | `f00f1a142896eb48d61f603ec662fc7833622a31c6cef5150ce6436ba0d138f9` |
| `narration-scene-01-v1` | `8dd43ce51b60e35d2757231731d5f3f9b449798b47de4279df60731539773645` |
| `narration-scene-03-v1` | `0982f47ee9518136cbc2486231bdaa4b9960321bcd819dd79feb5adea83606f5` |
| `narration-scene-04-v1` | `22ee5295dfb085be3a5d0308986e8db5b441dcf46df293c3529a5697d125ee27` |
| `narration-scene-05-v1` | `6d3737efe68cacba0ef512f8f973a9988583519047b934894f191189811dd236` |
| `narration-scene-06-v1` | `629f0d7df429c145bf05dd0c04f1ea13919c81d15582a3082e7e5c7ca01e9f97` |
| `narration-scene-07-v1` | `20a8e411330d2c11dd995e15441046eb35e5ea2980279963cc386a40fc26af19` |
| `sfx-archive-stamp-v1` | `de41383fd719bcd96f87c15009dbb85bfc7e8b290a8f8bc7716332e0715fd662` |
| `sfx-first-notification-v1` | `8e381a1c5aa1e68e098fd76518f5595968447469e4dafcba777d287a13b92338` |
| `sfx-low-drone-v1` | `3e116fe19f49a7f651f06893b91e2efd89f224ce6749b4e1df95c08867900d54` |
| `sfx-moon-impact-v1` | `c567aebd9dcc0a64430be338d2036a6ab097fbaa557d0addb268c6127844e166` |
| `sfx-second-message-tone-v1` | `ef078d8418f455cef15634d4b3206bfc59274069b2c52c73a9a14d62633af242` |
| `file-001-mix-v1` | `19ebb1df191da1d2131af0a7f0826a31429a7f497e956b06d896acae0c7a1150` |
| `picture-lock-v1` | `59d192f380ed9e0e8ef56658e798b21eb901dd7e4937d895987f49a955332fcb` |
| `file-001-short-v1` | `c909999bc727af6b6bd3cc0ba70430c36e9f0299e15d17c5f0f2a53f4259f3d2` |

## Status and blockers

- Base is `claude/integrate-v3`, not the old local `main`. The manifest remains v3, `status: script`, and every operational gate remains false.
- Approval hashing now LF-normalizes `.md`, `.json`, and `.svg`; media stays byte-exact. Regression tests prove CRLF and LF text hash identically.
- Three entries retain documented Runway provenance and recorded review references: normal-Moon keyframe, Moon-reveal keyframe, and Moon-reveal clip. All other inventory entries are `selected: false`.
- Provider history is absent from both the repository and `output/`. For the remaining 16 items, `provider`, `model`, `job_id`, `prompt_version`, and `generated_at` are deliberately `null`; no IDs or timestamps were inferred. Recover these fields from the owner/provider account before any selection or composition.
- Conservative raw-clip coverage: scene-01 **1/3** (`shot-01` only), scene-03 **1/3** (`shot-01` only), scene-05 **1/6** (`shot-01` only), scene-07 **1/2** (`shot-01` only). The scene-07 `shot-02` keyframe is not a required generated clip. Required clips are missing for all other listed shots.
- `file-001-picture-lock.mp4` exists locally but is an unapproved review artifact, not a master: SHA-256 `59d192f380ed9e0e8ef56658e798b21eb901dd7e4937d895987f49a955332fcb`; 33.000 s; H.264, 1080×1920, yuv420p, 30 fps; no audio stream. Its inputs were scene-01 v3, scene-03 v3, scene-04 normal-Moon, scene-05 stream-grid, scene-06 Moon-reveal, and scene-07 consequence v2. The composer now refuses until `final_script`, `storyboard`, and `visual_interface` are owner-approved.
- `voice_id` `JBFqnCBsd6RMkjVDRZzb` and preset `neutral-storyteller-v1` were introduced by commit `58deb97`; the commit/history contains no owner approval, selection rationale, or provider voice metadata establishing that it is neutral/not The Archivist. `output/file-001/audio/` now contains narration candidates and a mix, but none has provider provenance or a cost record. Their existence means generation may already have incurred cost; the amount cannot be established from this workspace. Treat the voice and every narration candidate as unapproved; do not generate further audio. The uncommitted `synthesize_narration` addition in `pipeline/providers/voice/elevenlabs.py` was present in the working tree and is excluded from this handoff commit.
- Pending human/technical checks: real-phone audibility of the 82 Hz component; final mixed loudness (−14 LUFS ±1 and ≤ −1 dBTP); caption safe area outside the bottom 20%. None can be completed from the silent review artifact.
