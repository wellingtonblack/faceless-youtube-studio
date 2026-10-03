"""Safe command-line boundary for the studio automation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from pipeline.manifest_validator import validate_manifest_file


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "episode" and args.episode_command == "validate":
        return _validate_episode(args)
    if args.command in {"voice", "clips", "compose", "qc", "build"}:
        parser.error(f"'{args.command}' is reserved but not implemented yet")
    if args.command == "upload":
        parser.error("upload is not implemented; future uploads will be private by default")
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

    for name in ("voice", "clips", "compose", "qc", "build"):
        stage = commands.add_parser(name, help=f"reserved for future {name} automation")
        stage.add_argument("episode")
    upload = commands.add_parser("upload", help="reserved for future private YouTube upload")
    upload.add_argument("episode")
    upload.add_argument("--privacy", choices=("private",), default="private")
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
