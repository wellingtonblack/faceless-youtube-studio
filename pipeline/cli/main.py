"""Safe command-line boundary for the studio automation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from pipeline.manifest_validator import validate_manifest_file
from pipeline.compose import compose_file_001_picture_lock
from pipeline.providers.voice import ElevenLabsClient, ElevenLabsError, plan_voice_generation
from pipeline.providers.youtube import (
    YouTubeOAuthError,
    YouTubeUploadError,
    authorize_local,
    private_upload_plan,
    upload_private_video,
    verify_refresh_token,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "episode" and args.episode_command == "validate":
        return _validate_episode(args)
    if args.command == "voice":
        return _plan_voice(args)
    if args.command == "provider" and args.provider == "elevenlabs" and args.provider_command == "verify":
        return _verify_elevenlabs()
    if args.command == "provider" and args.provider == "youtube" and args.provider_command == "authorize":
        return _authorize_youtube()
    if args.command == "provider" and args.provider == "youtube" and args.provider_command == "verify":
        return _verify_youtube()
    if args.command == "compose":
        return _compose_picture_lock(args)
    if args.command in {"clips", "qc", "build"}:
        parser.error(f"'{args.command}' is reserved but not implemented yet")
    if args.command == "upload":
        return _upload_private(args)
    parser.error("choose a command")
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studio", description="The Impossible Files production CLI")
    commands = parser.add_subparsers(dest="command")

    episode = commands.add_parser("episode", help="episode manifest operations")
    episode_commands = episode.add_subparsers(dest="episode_command")
    validate = episode_commands.add_parser("validate", help="validate an episode manifest")
    validate.add_argument("episode", help="episode ID (for example file-001) or manifest path")
    validate.add_argument("--json", action="store_true", help="emit a machine-readable result")

    voice = commands.add_parser("voice", help="preflight approved narration generation (dry-run only)")
    voice.add_argument("episode", help="episode ID (for example file-001) or manifest path")
    voice.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="show the safe generation plan without creating files or calling a provider (default)",
    )

    provider = commands.add_parser("provider", help="safe provider connection checks")
    provider_commands = provider.add_subparsers(dest="provider")
    elevenlabs = provider_commands.add_parser("elevenlabs", help="ElevenLabs metadata operations")
    elevenlabs_commands = elevenlabs.add_subparsers(dest="provider_command")
    elevenlabs_commands.add_parser(
        "verify",
        help="verify the configured key by listing voices; never generates audio",
    )
    youtube = provider_commands.add_parser("youtube", help="YouTube OAuth authorization and token verification")
    youtube_commands = youtube.add_subparsers(dest="provider_command")
    youtube_commands.add_parser("authorize", help="open local OAuth consent and save a refresh token to ignored .env")
    youtube_commands.add_parser("verify", help="verify the refresh token without accessing YouTube resources")

    for name in ("clips", "qc", "build"):
        stage = commands.add_parser(name, help=f"reserved for future {name} automation")
        stage.add_argument("episode")
    compose = commands.add_parser("compose", help="render the silent FILE #001 picture lock")
    compose.add_argument("episode")
    compose.add_argument("--ffmpeg", help="explicit FFmpeg executable path")
    upload = commands.add_parser("upload", help="upload an approved final MP4 to YouTube as private")
    upload.add_argument("episode")
    upload.add_argument("--privacy", choices=("private",), default="private")
    upload.add_argument("--description", required=True, help="video description; must say that the video is fiction")
    upload.add_argument("--tag", action="append", default=[], help="tag to send; repeat for additional tags")
    upload.add_argument("--category-id", default="24", help="numeric YouTube category ID (default: 24, Entertainment)")
    upload.add_argument("--execute", action="store_true", help="perform the private upload; omit for a safe dry run")
    return parser


def _validate_episode(args: argparse.Namespace) -> int:
    candidate = Path(args.episode)
    manifest_path = candidate if candidate.suffix == ".json" else REPOSITORY_ROOT / "episodes" / args.episode / "manifest.json"
    if not manifest_path.is_absolute():
        manifest_path = (REPOSITORY_ROOT / manifest_path).resolve()
    result = validate_manifest_file(manifest_path, REPOSITORY_ROOT / "schemas" / "episode.schema.json")
    if args.json:
        print(json.dumps({
            "valid": result.valid,
            "manifest": str(result.manifest_path.relative_to(REPOSITORY_ROOT)),
            "issues": [{"path": issue.path, "message": issue.message} for issue in result.issues],
        }, indent=2))
    elif result.valid:
        print(f"VALID {result.manifest_path.relative_to(REPOSITORY_ROOT)}")
    else:
        print(f"INVALID {result.manifest_path}")
        for issue in result.issues:
            print(f"  {issue.path}: {issue.message}")
    return 0 if result.valid else 1


def _plan_voice(args: argparse.Namespace) -> int:
    """Print a provider-free dry-run plan after the human approval gate."""
    candidate = Path(args.episode)
    manifest_path = candidate if candidate.suffix == ".json" else REPOSITORY_ROOT / "episodes" / args.episode / "manifest.json"
    if not manifest_path.is_absolute():
        manifest_path = (REPOSITORY_ROOT / manifest_path).resolve()

    plan = plan_voice_generation(
        manifest_path,
        REPOSITORY_ROOT / "schemas" / "episode.schema.json",
        REPOSITORY_ROOT,
    )
    if not plan.allowed:
        print(f"VOICE REFUSED: {plan.reason}")
        return 1

    assert plan.episode_id is not None
    assert plan.output_path is not None
    print(f"VOICE DRY-RUN: {plan.episode_id}")
    print(f"Planned output: {plan.output_path.relative_to(REPOSITORY_ROOT)}")
    print("No provider call, credential read, or file creation was performed.")
    return 0


def _verify_elevenlabs() -> int:
    """Confirm the local key can perform the minimal read-only voices request."""
    try:
        voices = ElevenLabsClient.from_local_environment(REPOSITORY_ROOT).list_voices()
    except ElevenLabsError as error:
        print(f"ELEVENLABS REFUSED: {error}")
        return 1

    print("ELEVENLABS VERIFIED")
    print(f"Accessible voices: {len(voices)}")
    print("No audio was generated and no output files were created.")
    return 0


def _authorize_youtube() -> int:
    try:
        authorize_local(REPOSITORY_ROOT)
    except YouTubeOAuthError as error:
        print(f"YOUTUBE OAUTH REFUSED: {error}")
        return 1
    print("YOUTUBE OAUTH AUTHORIZED")
    print("Refresh token saved only to the ignored local .env file.")
    print("No video was uploaded, changed, or published.")
    return 0


def _verify_youtube() -> int:
    try:
        verify_refresh_token(REPOSITORY_ROOT)
    except YouTubeOAuthError as error:
        print(f"YOUTUBE OAUTH REFUSED: {error}")
        return 1
    print("YOUTUBE OAUTH VERIFIED")
    print("The refresh token obtained an access token; no YouTube resource was accessed or changed.")
    return 0


def _upload_private(args: argparse.Namespace) -> int:
    try:
        plan = private_upload_plan(
            REPOSITORY_ROOT,
            args.episode,
            description=args.description,
            tags=tuple(args.tag),
            category_id=args.category_id,
        )
    except YouTubeUploadError as error:
        print(f"YOUTUBE UPLOAD REFUSED: {error}")
        return 1
    print(f"YOUTUBE PRIVATE UPLOAD PLAN: {plan.episode_id}")
    print(f"Video: {plan.video_path.relative_to(REPOSITORY_ROOT)}")
    print(f"Title: {plan.title}")
    print("Privacy: private; subscriber notifications: disabled")
    if not args.execute:
        print("Dry run only. Re-run with --execute to upload this exact reviewed MP4 privately.")
        return 0
    try:
        video_id = upload_private_video(REPOSITORY_ROOT, plan)
    except YouTubeUploadError as error:
        print(f"YOUTUBE UPLOAD REFUSED: {error}")
        return 1
    print(f"YOUTUBE PRIVATE UPLOAD COMPLETE: {video_id}")
    print("The manifest and frozen publishing metadata were updated. No public publishing occurred.")
    return 0


def _compose_picture_lock(args: argparse.Namespace) -> int:
    if args.episode != "file-001":
        raise ValueError("only file-001 has a defined picture-lock composition")
    result = validate_manifest_file(
        REPOSITORY_ROOT / "episodes" / args.episode / "manifest.json",
        REPOSITORY_ROOT / "schemas" / "episode.schema.json",
    )
    if not result.valid:
        print("COMPOSE REFUSED: episode manifest is invalid")
        return 1
    try:
        output = compose_file_001_picture_lock(REPOSITORY_ROOT, args.ffmpeg)
    except PermissionError as error:
        print(f"COMPOSE REFUSED: {error}")
        return 1
    print(f"PICTURE LOCK: {output.relative_to(REPOSITORY_ROOT)}")
    return 0
