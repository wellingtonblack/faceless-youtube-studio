"""Approval-gated private uploads to the YouTube Data API.

Public visibility deliberately has no implementation in this module. An upload
can only be executed by an explicit CLI flag after the exact final-QC artifacts
have passed manifest validation.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pipeline.manifest_validator import validate_manifest_file
from pipeline.providers.voice.elevenlabs import load_local_env_value
from pipeline.providers.youtube.oauth import YouTubeOAuthError, access_token_from_refresh_token


_RESUMABLE_INSERT_ENDPOINT = "https://www.googleapis.com/upload/youtube/v3/videos"


class YouTubeUploadError(RuntimeError):
    """A safe-to-display refusal or failure from the YouTube upload adapter."""


@dataclass(frozen=True)
class PrivateUploadPlan:
    episode_id: str
    video_path: Path
    title: str
    description: str
    tags: tuple[str, ...]
    category_id: str
    made_for_kids: bool
    contains_synthetic_media: bool


def private_upload_plan(
    repository_root: Path,
    episode: str,
    *,
    description: str,
    tags: tuple[str, ...] = (),
    category_id: str = "24",
) -> PrivateUploadPlan:
    """Validate the reviewed local episode before any credential or API use."""
    _reject_public_publish_configuration(repository_root)
    manifest_path = repository_root / "episodes" / episode / "manifest.json"
    result = validate_manifest_file(manifest_path, repository_root / "schemas" / "episode.schema.json")
    if not result.valid:
        details = "; ".join(f"{issue.path}: {issue.message}" for issue in result.issues[:3])
        raise YouTubeUploadError(f"episode manifest is not ready for upload ({details})")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise YouTubeUploadError("episode manifest could not be read") from error
    if manifest.get("status") != "qc":
        raise YouTubeUploadError("private upload requires episode status 'qc'")
    approvals = manifest.get("approvals", {})
    if not isinstance(approvals, dict) or approvals.get("final_qc", {}).get("approved") is not True:
        raise YouTubeUploadError("private upload requires human final_qc approval")
    publishing = manifest.get("publishing", {})
    if not isinstance(publishing, dict):
        raise YouTubeUploadError("episode publishing settings are missing")
    if publishing.get("youtube_video_id"):
        raise YouTubeUploadError("episode already records a YouTube video ID; refusing duplicate upload")
    if publishing.get("youtube_privacy") != "private":
        raise YouTubeUploadError("private upload requires manifest youtube_privacy to be 'private'")
    if not description.strip() or "fiction" not in description.casefold():
        raise YouTubeUploadError("description must explicitly state that the video is fiction")
    if not category_id.isdigit():
        raise YouTubeUploadError("category ID must be numeric")
    video_path = repository_root / "output" / episode / "final" / f"{episode}-{manifest.get('format', 'short')}.mp4"
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise YouTubeUploadError("reviewed final MP4 is missing or empty")
    title = manifest.get("title")
    if not isinstance(title, str) or not title.strip():
        raise YouTubeUploadError("episode title is missing")
    return PrivateUploadPlan(
        episode_id=episode, video_path=video_path, title=title, description=description.strip(),
        tags=tuple(tag.strip() for tag in tags if tag.strip()), category_id=category_id,
        made_for_kids=bool(publishing.get("selfDeclaredMadeForKids")),
        contains_synthetic_media=bool(publishing.get("containsSyntheticMedia")),
    )


def upload_private_video(repository_root: Path, plan: PrivateUploadPlan) -> str:
    """Upload one reviewed MP4 privately and atomically record the returned ID."""
    try:
        access_token = access_token_from_refresh_token(repository_root)
        video_id = _resumable_upload(access_token, plan)
    except YouTubeOAuthError as error:
        raise YouTubeUploadError(str(error)) from error
    _record_private_upload(repository_root, plan, video_id)
    return video_id


def _resumable_upload(access_token: str, plan: PrivateUploadPlan) -> str:
    metadata: dict[str, Any] = {
        "snippet": {"title": plan.title, "description": plan.description, "categoryId": plan.category_id},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": plan.made_for_kids,
                   "containsSyntheticMedia": plan.contains_synthetic_media},
    }
    if plan.tags:
        metadata["snippet"]["tags"] = list(plan.tags)
    query = urlencode({"uploadType": "resumable", "part": "snippet,status", "notifySubscribers": "false"})
    start = Request(
        f"{_RESUMABLE_INSERT_ENDPOINT}?{query}", data=json.dumps(metadata).encode("utf-8"),
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=utf-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(plan.video_path.stat().st_size)},
        method="POST",
    )
    try:
        with urlopen(start, timeout=30) as response:
            location = response.headers.get("Location")
        if not location:
            raise YouTubeUploadError("YouTube did not return a resumable upload URL")
        # The project currently produces short MP4s. A future long-form workflow
        # can add chunked resume state without changing this provider boundary.
        media = plan.video_path.read_bytes()
        transfer = Request(location, data=media, headers={"Authorization": f"Bearer {access_token}",
                           "Content-Type": "video/mp4", "Content-Length": str(len(media))}, method="PUT")
        with urlopen(transfer, timeout=300) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise YouTubeUploadError(f"YouTube rejected the private upload (HTTP {error.code})") from error
    except (URLError, TimeoutError, OSError) as error:
        raise YouTubeUploadError("could not complete the private upload to YouTube") from error
    except json.JSONDecodeError as error:
        raise YouTubeUploadError("YouTube returned an invalid upload response") from error
    video_id = payload.get("id") if isinstance(payload, dict) else None
    if not isinstance(video_id, str) or not video_id:
        raise YouTubeUploadError("YouTube upload response did not include a video ID")
    return video_id


def _record_private_upload(repository_root: Path, plan: PrivateUploadPlan, video_id: str) -> None:
    manifest_path = repository_root / "episodes" / plan.episode_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    publishing = manifest["publishing"]
    if manifest.get("status") != "qc" or publishing.get("youtube_video_id"):
        raise YouTubeUploadError("local episode state changed during upload; video ID was not recorded")
    manifest["status"] = "upload_private"
    publishing.update({"youtube_privacy": "private", "youtube_video_id": video_id, "published_at": None})
    _atomic_write_json(manifest_path, manifest)
    _atomic_write_json(repository_root / "episodes" / plan.episode_id / "publishing-metadata.json", {
        "title": plan.title, "description": plan.description, "tags": list(plan.tags), "categoryId": plan.category_id,
        "youtube_video_id": video_id, "selfDeclaredMadeForKids": plan.made_for_kids,
        "containsSyntheticMedia": plan.contains_synthetic_media,
    })


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _reject_public_publish_configuration(repository_root: Path) -> None:
    configured = load_local_env_value(repository_root / ".env", "AUTO_PUBLISH")
    if configured not in (None, "", "false"):
        raise YouTubeUploadError("AUTO_PUBLISH must be empty or exactly 'false'")
