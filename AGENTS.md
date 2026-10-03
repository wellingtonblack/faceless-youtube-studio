# AGENTS.md — Shared Agent Instructions

This repository is the source of truth for **The Impossible Files**, a faceless, English-language YouTube media project built around cinematic mystery, anomalies, speculative fiction, and serialized lore.

These instructions apply to Codex and any other coding agent working in this repository.

## Read before doing work
Before modifying production code, prompts, episode data, or channel rules, read:
1. `MASTER_RULES.md`
2. `docs/brand-bible.md`
3. `docs/story-bible.md`
4. `docs/visual-bible.md`
5. `docs/automation-architecture.md`
6. `docs/security.md`
7. the relevant episode manifest under `episodes/`

If a task conflicts with `MASTER_RULES.md`, stop and flag the conflict instead of silently changing the project direction.

## Project priorities
1. Originality and monetization safety.
2. Consistent characters, lore, visual language, voice and naming.
3. Reproducible production pipeline.
4. Human approval before public publishing.
5. Traceable decisions and version control.

## Agent roles
- **ChatGPT**: strategy, creative direction, scripts, visual direction, analytics interpretation, system-level decisions.
- **Claude / Claude Code**: long-context review, lore continuity, documentation review, prompt review, implementation support.
- **Codex**: engineering, APIs, CLI, automation, FFmpeg, validation, tests, packaging and deployment tooling.
- **Human owner**: credentials, billing, final creative approval, platform/account actions and final publication authorization.

Agents may collaborate through Git commits, issues, manifests and documented handoffs. Do not assume another agent has seen an external chat.

## Engineering conventions
- Prefer TypeScript or Python for automation; document the choice per module.
- Every external provider must be wrapped behind an adapter under `pipeline/providers/`.
- Do not hard-code provider-specific logic throughout the application.
- Use deterministic filenames and episode IDs.
- All generated artifacts must be associated with an episode manifest.
- Scripts must support dry-run where practical.
- Public upload must never be the default behavior.

## Publishing safety
The default YouTube upload state is `private`.
Never implement automatic public publishing.

Public publishing requires **both** `approvals.public_publish.approved = true` in the episode manifest **and** an explicit `--confirm-public` flag on the publish command. No environment variable or configuration file can replace either condition. (Decision 2026-10-03, see `docs/decision-log.md`.)

Environment behavior:
- `AUTO_UPLOAD=true` may upload privately.
- `AUTO_PUBLISH` must be `false` or empty; any other value is a configuration error.

## Secrets
Never commit API keys, OAuth client secrets, access tokens, refresh tokens, cookies or local credential files.
Use `.env` locally or secret stores in CI.
If a secret is found in tracked content, treat it as compromised and report it immediately.

## Episode workflow
Canonical lifecycle:
`idea -> approved -> script -> storyboard -> assets -> voice -> clips -> edit -> qc -> upload_private -> approved_for_publish -> published -> measured`

Agents must update the episode manifest when changing lifecycle status. The manifest is the only place lifecycle status is stored.
Human approval gates are recorded in the manifest's `approvals` object. Agents record approvals given by the human owner and never self-approve.

## File ownership
- Strategic rules: `MASTER_RULES.md`, `docs/`
- Characters/lore: `characters/`, `docs/story-bible.md`
- Episode state: `episodes/`
- Reusable prompts: `prompts/`
- Automation code: `pipeline/`
- Schemas/config: `schemas/`, `config/`
- Generated local output: `output/` (not committed unless explicitly approved)

## Git practices
- Make focused commits.
- Use descriptive commit messages.
- Do not rewrite history on `main`.
- For material architecture changes, prefer a branch/PR or document the rationale in `docs/decision-log.md`.

## Quality bar
Do not optimize only for automation speed. The project should not become mass-produced generic AI content. Automation exists to increase consistency and throughput while keeping scripts, visuals, editing and storytelling original.
