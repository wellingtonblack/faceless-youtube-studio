"""Explicit, approval-gated publication of a previously private YouTube video.

The only caller is the CLI ``publish`` command, which requires both a pinned
human approval in the manifest and the literal ``--confirm-public`` flag. This
module never uploads media and cannot be reached through the private-upload
path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pipeline.manifest_validator import validate_manifest_file
from pipeline.providers.youtube.oauth import YouTubeOAuthError, access_token_from_refresh_token
from pipeline.providers.youtube.upload import _atomic_write_json, _reject_public_publish_configuration


_VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"


class YouTubePublishError(RuntimeError):
    """A safe-to-display refusal or failure from the public-publish adapter."""


@dataclass(frozen=True)
class PublicPublishPlan:
    """The exact existing private video and disclosure flags to make public."""

    episode_id: str
    video_id: str
    title: str
    made_for_kids: bool
    contains_synthetic_media: bool


def public_publish_plan(repository_root: Path, episode: str) -> PublicPublishPlan:
    """Validate every public-publish gate before reading OAuth credentials."""
    try:
        _reject_public_publish_configuration(repository_root)
    except RuntimeError as error:
        raise YouTubePublishError(str(error)) from error
    manifest_path = repository_root / "episodes" / episode / "manifest.json"
    result = validate_manifest_file(manifest_path, repository_root / "schemas" / "episode.schema.json")
    if not result.valid:
        details = "; ".join(f"{issue.path}: {issue.message}" for issue in result.issues[:3])
        raise YouTubePublishError(f"episode manifest is not ready for public publication ({details})")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise YouTubePublishError("episode manifest could not be read") from error
    if manifest.get("status") != "approved_for_publish":
        raise YouTubePublishError("public publication requires episode status 'approved_for_publish'")
    approvals = manifest.get("approvals")
    if not isinstance(approvals, dict):
        raise YouTubePublishError("episode approvals are missing")
    if approvals.get("final_qc", {}).get("approved") is not True:
        raise YouTubePublishError("public publication requires human final_qc approval")
    if approvals.get("public_publish", {}).get("approved") is not True:
        raise YouTubePublishError("public publication requires explicit human public_publish approval")
    publishing = manifest.get("publishing")
    if not isinstance(publishing, dict):
        raise YouTubePublishError("episode publishing settings are missing")
    video_id = publishing.get("youtube_video_id")
    if not isinstance(video_id, str) or not video_id.strip():
        raise YouTubePublishError("public publication requires an existing private YouTube video ID")
    if publishing.get("youtube_privacy") != "private":
        raise YouTubePublishError("public publication requires the recorded video to still be private")
    title = manifest.get("title")
    if not isinstance(title, str) or not title.strip():
        raise YouTubePublishError("episode title is missing")
    return PublicPublishPlan(
        episode_id=episode,
        video_id=video_id,
        title=title,
        made_for_kids=bool(publishing.get("selfDeclaredMadeForKids")),
        contains_synthetic_media=bool(publishing.get("containsSyntheticMedia")),
    )


def publish_public_video(repository_root: Path, plan: PublicPublishPlan) -> None:
    """Set an already uploaded reviewed video public and record only a verified result."""
    try:
        access_token = access_token_from_refresh_token(repository_root)
        _set_public_visibility(access_token, plan)
    except YouTubeOAuthError as error:
        raise YouTubePublishError(str(error)) from error
    _record_public_publication(repository_root, plan)


def _set_public_visibility(access_token: str, plan: PublicPublishPlan) -> None:
    payload = {
        "id": plan.video_id,
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": plan.made_for_kids,
            "containsSyntheticMedia": plan.contains_synthetic_media,
        },
    }
    request = Request(
        f"{_VIDEOS_ENDPOINT}?{urlencode({'part': 'status'})}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=utf-8"},
        method="PUT",
    )
    try:
        with urlopen(request, timeout=30) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 403:
            raise YouTubePublishError(
                "YouTube rejected public publication (HTTP 403); the API project may require audit approval"
            ) from error
        raise YouTubePublishError(f"YouTube rejected public publication (HTTP {error.code})") from error
    except (URLError, TimeoutError, OSError) as error:
        raise YouTubePublishError("could not update the YouTube video visibility") from error
    except json.JSONDecodeError as error:
        raise YouTubePublishError("YouTube returned an invalid publication response") from error
    status = response_payload.get("status") if isinstance(response_payload, dict) else None
    if (
        not isinstance(response_payload, dict)
        or response_payload.get("id") != plan.video_id
        or not isinstance(status, dict)
        or status.get("privacyStatus") != "public"
    ):
        raise YouTubePublishError("YouTube did not confirm that the intended video is public")


def _record_public_publication(repository_root: Path, plan: PublicPublishPlan) -> None:
    manifest_path = repository_root / "episodes" / plan.episode_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    publishing = manifest.get("publishing")
    if (
        manifest.get("status") != "approved_for_publish"
        or not isinstance(publishing, dict)
        or publishing.get("youtube_privacy") != "private"
        or publishing.get("youtube_video_id") != plan.video_id
    ):
        raise YouTubePublishError("local episode state changed during publication; public result was not recorded")
    manifest["status"] = "published"
    publishing.update({
        "youtube_privacy": "public",
        "published_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    })
    _atomic_write_json(manifest_path, manifest)
