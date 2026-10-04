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

    _validate_schema(manifest, schema, "$", issues, schema)
    _validate_studio_policies(manifest, manifest_path, issues)
    return ValidationResult(manifest_path, tuple(issues))


def _validate_schema(
    value: Any,
    schema: dict[str, Any],
    path: str,
    issues: list[ValidationIssue],
    root_schema: dict[str, Any],
) -> None:
    """Validate the JSON Schema keywords used by the canonical manifest schema.

    This is intentionally small rather than a replacement for a general JSON
    Schema library. It supports the draft 2020-12 features used in this local,
    versioned contract: local references, composition, and conditionals.
    """
    if "$ref" in schema:
        try:
            _validate_schema(value, _resolve_local_ref(schema["$ref"], root_schema), path, issues, root_schema)
        except ValueError as error:
            issues.append(ValidationIssue(path, str(error)))

    for sub_schema in schema.get("allOf", []):
        _validate_schema(value, sub_schema, path, issues, root_schema)

    condition = schema.get("if")
    if condition is not None and _matches_schema(value, condition, root_schema):
        then_schema = schema.get("then")
        if then_schema is not None:
            _validate_schema(value, then_schema, path, issues, root_schema)
    elif condition is not None and schema.get("else") is not None:
        _validate_schema(value, schema["else"], path, issues, root_schema)

    allowed_types = schema.get("type")
    if allowed_types is not None:
        types = allowed_types if isinstance(allowed_types, list) else [allowed_types]
        if not any(_matches_type(value, candidate) for candidate in types):
            issues.append(ValidationIssue(path, f"expected type {' or '.join(types)}"))
            return

    if "const" in schema and not _json_equal(value, schema["const"]):
        issues.append(ValidationIssue(path, f"must equal {schema['const']!r}"))
    if "enum" in schema and not any(_json_equal(value, option) for option in schema["enum"]):
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
                _validate_schema(item, item_schema, f"{path}[{index}]", issues, root_schema)

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                issues.append(ValidationIssue(path, f"missing required property '{name}'"))
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in properties:
                    issues.append(ValidationIssue(f"{path}.{name}", "property is not allowed"))
        if schema.get("unevaluatedProperties") is False:
            evaluated = _evaluated_property_names(schema, root_schema)
            for name in value:
                if name not in evaluated:
                    issues.append(ValidationIssue(f"{path}.{name}", "property is not allowed"))
        for name, item in value.items():
            if name in properties:
                _validate_schema(item, properties[name], f"{path}.{name}", issues, root_schema)


def _matches_schema(value: Any, schema: dict[str, Any], root_schema: dict[str, Any]) -> bool:
    """Evaluate a conditional schema without adding validation issues."""
    probe_issues: list[ValidationIssue] = []
    _validate_schema(value, schema, "$", probe_issues, root_schema)
    return not probe_issues


def _resolve_local_ref(reference: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported schema reference '{reference}'")
    value: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            raise ValueError(f"unresolvable schema reference '{reference}'")
        value = value[token]
    if not isinstance(value, dict):
        raise ValueError(f"schema reference '{reference}' does not point to an object")
    return value


def _evaluated_property_names(schema: dict[str, Any], root_schema: dict[str, Any]) -> set[str]:
    """Return object keys covered by properties or composed local references."""
    names = set(schema.get("properties", {}))
    if "$ref" in schema:
        names.update(_evaluated_property_names(_resolve_local_ref(schema["$ref"], root_schema), root_schema))
    for sub_schema in schema.get("allOf", []):
        names.update(_evaluated_property_names(sub_schema, root_schema))
    return names


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


def _json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's bool-is-an-int equivalence."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    return left == right


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
    approvals = manifest.get("approvals")
    public_publish = approvals.get("public_publish") if isinstance(approvals, dict) else None
    public_approved = public_publish.get("approved") if isinstance(public_publish, dict) else False
    status = manifest.get("status")
    if privacy in {"unlisted", "public"} and public_approved is not True:
        issues.append(ValidationIssue("$.approvals.public_publish.approved", "must be true before non-private privacy is allowed"))
    if status in {"published", "measured"}:
        if public_approved is not True:
            issues.append(ValidationIssue("$.approvals.public_publish.approved", "must be true for a published or measured episode"))
        if privacy != "public":
            issues.append(ValidationIssue("$.publishing.youtube_privacy", "must be 'public' for a published or measured episode"))


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
