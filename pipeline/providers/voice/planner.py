"""Provider-neutral preflight for episode narration.

This module deliberately does not import provider SDKs, read environment
variables, or make network requests. A future provider adapter may consume a
successful ``VoicePlan`` only after its own credential and execution review.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipeline.manifest_validator import validate_manifest_file


@dataclass(frozen=True)
class VoicePlan:
    """The safe result of checking whether narration may be generated."""

    allowed: bool
    episode_id: str | None
    output_path: Path | None
    reason: str | None


def plan_voice_generation(
    manifest_path: Path,
    schema_path: Path,
    repository_root: Path,
) -> VoicePlan:
    """Validate and preflight narration generation without any side effects.

    A human's recorded final-script approval is a non-negotiable gate. The
    resulting plan contains no provider configuration or credential material.
    """
    validation = validate_manifest_file(manifest_path, schema_path)
    if not validation.valid:
        return VoicePlan(False, None, None, "episode manifest is invalid; run episode validation first")

    try:
        manifest: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # The validator has already diagnosed this case; keep this boundary
        # defensive if it is called while the file changes on disk.
        return VoicePlan(False, None, None, "episode manifest could not be read safely")

    if not isinstance(manifest, dict):
        return VoicePlan(False, None, None, "episode manifest must be an object")

    final_script = manifest.get("approvals", {}).get("final_script", {})
    if not isinstance(final_script, dict) or final_script.get("approved") is not True:
        return VoicePlan(
            False,
            manifest.get("episode_id") if isinstance(manifest.get("episode_id"), str) else None,
            None,
            "voice generation requires approvals.final_script.approved=true recorded by the human owner",
        )

    episode_id = manifest.get("episode_id")
    if not isinstance(episode_id, str):
        return VoicePlan(False, None, None, "episode manifest has no valid episode ID")

    return VoicePlan(
        True,
        episode_id,
        repository_root / "output" / episode_id / "audio" / "narration.mp3",
        None,
    )
