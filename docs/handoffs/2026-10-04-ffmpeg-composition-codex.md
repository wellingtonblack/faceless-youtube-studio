# Handoff — FFmpeg environment and composition guidance (to Codex)

Date: 2026-10-04
From: Claude Code (implementation review)
To: Codex (pipeline owner: `pipeline/compose/`, `pipeline/captions/`, `pipeline/qc/`)
Status: guidance. Nothing here changes canon or approved specs.

Everything below was verified on the owner's machine with real renders unless marked *verify*.

## 1. Local environment (owner's Windows machine)
- FFmpeg **9.0.2**, `full_build` from gyan.dev, installed by winget as `Gyan.FFmpeg`.
- `ffmpeg`/`ffprobe` are on the **user** PATH: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_…\ffmpeg-9.0.2-full_build\bin`. Shells opened before the install need restarting.
- Enabled and verified: `libx264`, `aac`, `libfreetype`, `libharfbuzz`, `libass`, `libmp3lame`; filters `drawtext`, `subtitles`, `overlay`, `scale`, `pad`, `drawbox`, `aevalsrc`, `ebur128`, `loudnorm`.
- **Not available:**
  - `libfontconfig`: fonts cannot be looked up by family name.
  - `librsvg`: FFmpeg cannot rasterize SVG.

## 2. Must-follow rules

### 2.1 On-screen text: use `textfile=`, never inline `text=`
Inline `text='DON'T LOOK'` rendered **`DONT LOOK`** with exit code 0: the apostrophe was silently consumed by filtergraph quoting. That would corrupt canonical text without any error.
- Write each text to a UTF-8 file and pass `drawtext=textfile=<path>`.
- Add a test that fails if the compose builder ever emits `text=`.
- `textfile=` was verified with `DON'T LOOK\nAT THE MOON.` (multi-line, `line_spacing`) and `FILE #001 — ARCHIVED` (em dash).

### 2.2 Fonts: vendored files, explicit paths, never system fonts
- There are no font files in the repo. The SVG mockups declare `IBM Plex Mono, Consolas, monospace`, so on Windows they render with **Consolas**, a Microsoft-licensed font. Treat the mockups as layout reference only; never use Consolas or other OS fonts in renders.
- Vendor the spec fonts with their licenses, e.g. `assets/fonts/`:
  - IBM Plex Mono Bold and Regular (SIL OFL 1.1);
  - Inter SemiBold (SIL OFL 1.1), for the archive overlay.
- `drawtext`: always `fontfile=<path>`. For `subtitles`, pass `fontsdir=<dir>` and name the font in `force_style`.
- Record each font file in `episodes/file-001/assets.json` with `sha256` and `license`.
- Before vendoring, confirm that the font-file location (and whether fonts may be committed) matches `.gitignore`/repo policy.

### 2.3 Filtergraph portability (PowerShell, Git Bash and CI)
- Windows drive colons must be escaped inside filter options (`C\:/...`). Prefer repository-relative forward-slash paths and run from the repo root.
- Do not build long filtergraphs through shell strings. Write the graph to a file and load it with **`-/filter_complex <file>`** (verified on 9.0.2). **`-filter_complex_script` no longer exists in 9.0.2** (`Unrecognized option`), so don't copy it from older examples.
- Inside a graph file, Windows drive colons still need escaping (`C\:/...`).
- When writing a single image (thumbnails, QC frames), add `-update 1`; 9.0.2 warns otherwise.
- Invoke FFmpeg via `subprocess` argument lists. Never use `shell=True`.

### 2.4 Interface rendering (scenes 02, 07, 08)
- No `librsvg`, so do not try to feed the SVG mockups to FFmpeg. Either:
  - draw the interface with `drawtext` + `drawbox` (verified); or
  - pre-render PNGs with a separate, documented tool.
- Red cursor: `drawbox=...:color=0xE0161E@1:t=fill`.
  - Message 1 blinks at 1 Hz with `enable='lt(mod(t\,1)\,0.5)'` (verified).
  - Message 2 has a solid cursor: no `enable`.
- **The cursor position must be computed from text metrics, not hard-coded.** A hard-coded box overlapped the final period in testing. Measuring the line in a pre-pass, for example with Pillow and the same font file, is the reliable route.
- Colors and layout come only from `docs/visual/anomaly-message-interface.md` (tokens `ami-*`). The archive overlay uses its own style: sans, letter-spaced, no red, no cursor.

### 2.5 Master output contract (Shorts)
- 1080×1920, **30 fps CFR**, H.264 High, `yuv420p`, BT.709 tags (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`), `-movflags +faststart`.
- Audio: AAC-LC, 48 kHz, stereo.
- Runway assets are recorded at `720:1280`, so they must be upscaled (`scale=1080:1920:flags=lanczos`). Log the upscale in the build manifest, and have QC/the owner review sharpness at full size.

### 2.6 Captions
- libass places subtitles at the bottom by default (confirmed). The spec keeps the **bottom ~20%** clear for Shorts UI.
- Set `force_style` (`Alignment`, `MarginV`, `FontName`, `FontSize`, `Outline`) to keep captions in the safe zone.

### 2.7 Loudness
- Target about **−14 LUFS integrated** and **≤ −1 dBTP** true peak for the final mix, using two-pass `loudnorm`. Verify with `ebur128=peak=true`.
- For reference, the raw second-message tone measured −12.0 LUFS, peak −1.9 dBFS, before mixing.

### 2.8 Second-message tone
The approved recipe (82 Hz + 392 Hz sines, ~0.8 s reverse swell, abrupt cut, ~1.2 s) is reproducible with `aevalsrc` + `afade`. Keep the exact parameters in code and record them in `assets.json` as an original asset.

**Flag for the owner, do not change silently:** phone speakers reproduce little below ~150 Hz. On most phones the 82 Hz bed will be nearly inaudible, and the tone will rest on the 392 Hz partial alone. Test on a real phone speaker. If the tone loses its effect, raise it as a spec question; it is an owner-approved spec.

### 2.9 QC (`pipeline/qc/`)
- `ffprobe` asserts: duration 28–35 s, 1080×1920, 30/1 fps, `h264` + `aac` present, `yuv420p`.
- `blackdetect`/`silencedetect` are useful, but FILE #001 has **intentional** black and silence: the scene-05 dropout, the scene-06 pre-impact silence, scene-08 silence and the scene-09 black sting. Use storyboard timings as allow-lists so QC doesn't flag them.

### 2.10 Reproducibility and CI
- Record `ffmpeg -version` (first line) and the full command/filter script in `output/<episode>/build-manifest.json`.
- Use the same FFmpeg version for all final renders of an episode.
- CI (`.github/workflows/validate.yml`, `ubuntu-latest`) **has no FFmpeg**. Compose tests must either:
  - skip with an explicit message when `ffmpeg` is missing; or
  - install it in CI. Note that apt provides an older major version; don't assert version-specific output.

## 3. Verified recipes (for reference)
```bash
# Interface message 1: text from file, blinking red cursor (position must be computed, see 2.4)
ffmpeg -f lavfi -i "color=c=0x0B0B0B:s=1080x1920:d=2:r=30" -vf \
 "drawtext=fontfile=<IBMPlexMono-Bold.ttf>:textfile=msg.txt:fontcolor=0xF4F4F4:fontsize=120:line_spacing=20:x=130:y=730,\
drawbox=x=<computed>:y=<computed>:w=70:h=120:color=0xE0161E@1:t=fill:enable='lt(mod(t\,1)\,0.5)'" \
 -c:v libx264 -pix_fmt yuv420p out.mp4

# Second-message tone (approved recipe)
ffmpeg -f lavfi -i "aevalsrc='0.5*sin(2*PI*82*t)+0.3*sin(2*PI*392*t)':s=48000:d=1.2" \
 -af "afade=t=in:d=0.8:curve=exp" tone.wav

# Loudness check
ffmpeg -i mix.wav -af ebur128=peak=true -f null -
```

## 4. Not for Codex (owner decisions)
- The 82 Hz audibility question in 2.8, if testing shows a problem.
- Confirming the season-1 slot 6 and slot 8 replacement titles.
