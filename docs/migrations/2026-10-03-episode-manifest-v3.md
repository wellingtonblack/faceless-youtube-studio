# Episode manifest v3 — approval and handoff correction

2026-10-03. Supersedes v2 for active manifests; v2 migration remains historical.

- Require script/storyboard/interface/asset-registry paths.
- Add human `storyboard` and `visual_interface` gates before assets and downstream stages.
- Operational approval objects require an `artifacts` list; approved gates pin required
  reviewed files by SHA-256. Markdown, JSON and SVG artifact hashes normalize line
  endings to LF before hashing, so Windows and Linux verify the same reviewed text;
  binary artifacts remain byte-exact. Empty lists are allowed only for pending gates.
- Keep existing canon/lore approval records unchanged: this migration grants no new approval.
- Validate registry against `schemas/assets.schema.json`; require unique IDs/paths,
  canonical scenes, shot IDs for clips, license/source evidence for music/SFX,
  selection review references, dependency references and local checksums when present.
- Non-private visibility requires final QC as well as public authorization.
- Freeze public title/disclosures/video ID in a hash-bound metadata file.
- CI discovers all pipeline tests, including voice preflight and handoff regression tests.

FILE #001 remains in `script` with final script, storyboard, interface, QC and public
approval false. The registry is an inventory of locally present candidate media, not
evidence that production gates have been approved or that a build is ready.
The owner authorized these audit fixes, not final creative approval or publication.

Validation is not build execution. Provider calls, FFmpeg composition, automated QC,
YouTube upload/publish and scheduled analytics are still future modules.
See `docs/file-001-handoff.md` for bindings, acceptance and revision rules.
