"""Dependency-free validation for episode manifests.

The validator applies the repository JSON Schema and the publishing safeguards
that are intentionally stricter than the portable episode contract.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


LIFECYCLE = (
    "idea", "approved", "script", "storyboard", "assets", "voice", "clips",
    "edit", "qc", "upload_private", "approved_for_publish", "published", "measured",
)
SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|secret|token|password|private[_-]?key)", re.IGNORECASE)


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    manifest_path: Path
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


def validate_manifest_file(manifest_path: Path, schema_path: Path) -> ValidationResult:
    """Validate JSON at *manifest_path* against the supplied schema and policies."""
    issues: list[ValidationIssue] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ValidationResult(manifest_path, (ValidationIssue("$", "manifest file does not exist"),))
    except json.JSONDecodeError as error:
        return ValidationResult(manifest_path, (ValidationIssue("$", f"invalid JSON: {error.msg}"),))

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ValidationResult(manifest_path, (ValidationIssue("$", "episode schema file does not exist"),))
    except json.JSONDecodeError as error:
        return ValidationResult(schema_path, (ValidationIssue("$", f"invalid schema JSON: {error.msg}"),))

    _validate_schema(manifest, schema, "$", issues)
    _validate_studio_policies(manifest, manifest_path, issues)
    return ValidationResult(manifest_path, tuple(issues))


def _validate_schema(value: Any, schema: dict[str, Any], path: str, issues: list[ValidationIssue]) -> None:
    allowed_types = schema.get("type")
    if allowed_types is not None:
        types = allowed_types if isinstance(allowed_types, list) else [allowed_types]
        if not any(_matches_type(value, candidate) for candidate in types):
            issues.append(ValidationIssue(path, f"expected type {' or '.join(types)}"))
            return

    if "enum" in schema and value not in schema["enum"]:
        issues.append(ValidationIssue(path, f"must be one of: {', '.join(map(str, schema['enum']))}"))

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            issues.append(ValidationIssue(path, f"must contain at least {schema['minLength']} character(s)"))
        if "pattern" in schema and not re.search(schema["pattern"], value):
            issues.append(ValidationIssue(path, "does not match the required pattern"))
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                issues.append(ValidationIssue(path, "must be an ISO 8601 date-time"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(ValidationIssue(path, f"must be at least {schema['minimum']}"))

    if isinstance(value, list):
        if schema.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
            issues.append(ValidationIssue(path, "items must be unique"))
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                _validate_schema(item, item_schema, f"{path}[{index}]", issues)

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                issues.append(ValidationIssue(path, f"missing required property '{name}'"))
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in properties:
                    issues.append(ValidationIssue(f"{path}.{name}", "property is not allowed"))
        for name, item in value.items():
            if name in properties:
                _validate_schema(item, properties[name], f"{path}.{name}", issues)


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _validate_studio_policies(manifest: Any, manifest_path: Path, issues: list[ValidationIssue]) -> None:
    if not isinstance(manifest, dict):
        return

    episode_id = manifest.get("episode_id")
    file_number = manifest.get("file_number")
    if isinstance(episode_id, str) and isinstance(file_number, int):
        expected_id = f"file-{file_number:03d}"
        if episode_id != expected_id:
            issues.append(ValidationIssue("$.episode_id", f"must match file_number; expected '{expected_id}'"))
    if isinstance(episode_id, str) and manifest_path.parent.name != episode_id:
        issues.append(ValidationIssue("$.episode_id", "must match the manifest parent directory"))

    for field in ("script_path", "storyboard_path"):
        value = manifest.get(field)
        if isinstance(value, str) and (Path(value).is_absolute() or ".." in Path(value).parts):
            issues.append(ValidationIssue(f"$.{field}", "must be a safe repository-relative path"))

    _find_sensitive_keys(manifest, "$", issues)

    publishing = manifest.get("publishing")
    if not isinstance(publishing, dict):
        return
    privacy = publishing.get("youtube_privacy")
    approved = publishing.get("public_publish_approved")
    status = manifest.get("status")
    if privacy == "public" and approved is not True:
        issues.append(ValidationIssue("$.publishing.public_publish_approved", "must be true before public privacy is allowed"))
    if status == "published":
        if approved is not True:
            issues.append(ValidationIssue("$.publishing.public_publish_approved", "must be true for a published episode"))
        if privacy != "public":
            issues.append(ValidationIssue("$.publishing.youtube_privacy", "must be 'public' for a published episode"))


def _find_sensitive_keys(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = f"{path}.{key}"
            if SENSITIVE_KEY.search(key):
                issues.append(ValidationIssue(nested_path, "secrets must not be stored in episode manifests"))
            _find_sensitive_keys(nested, nested_path, issues)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _find_sensitive_keys(nested, f"{path}[{index}]", issues)
