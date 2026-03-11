"""Configuration and capability manifest loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platform_adapters.contracts import CapabilityManifest
from platform_adapters.errors import CapabilitySchemaError

SUPPORTED_SCHEMA_VERSION = "1.0"
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "adapter_id",
    "name",
    "provider",
    "version",
    "domain",
    "capabilities",
}


def _validate_string_field(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CapabilitySchemaError(f"Field '{field}' must be a non-empty string")
    return value.strip()


def validate_manifest(data: dict[str, Any]) -> CapabilityManifest:
    """Validate raw manifest data and return canonical model."""

    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(data.keys()))
    if missing:
        raise CapabilitySchemaError(f"Missing required manifest fields: {', '.join(missing)}")

    schema_version = _validate_string_field(data, "schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise CapabilitySchemaError(
            "Unsupported schema version "
            f"'{schema_version}'. Supported version: {SUPPORTED_SCHEMA_VERSION}"
        )

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise CapabilitySchemaError("Field 'capabilities' must be a non-empty list")

    normalized_capabilities = tuple(
        sorted({str(item).strip() for item in capabilities if str(item).strip()})
    )
    if not normalized_capabilities:
        raise CapabilitySchemaError("At least one valid capability string must be provided")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise CapabilitySchemaError("Field 'metadata' must be an object/map when provided")

    return CapabilityManifest(
        schema_version=schema_version,
        adapter_id=_validate_string_field(data, "adapter_id"),
        name=_validate_string_field(data, "name"),
        provider=_validate_string_field(data, "provider"),
        version=_validate_string_field(data, "version"),
        domain=_validate_string_field(data, "domain"),
        capabilities=normalized_capabilities,
        metadata=metadata,
    )


def load_manifest(path: str | Path) -> CapabilityManifest:
    """Load and validate a capability manifest from disk.

    Only JSON is supported in this runtime dependency profile.
    """

    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix != ".json":
        raise CapabilitySchemaError(
            "Only JSON manifest files are supported by this build. "
            f"Got '{suffix or 'no-extension'}'"
        )

    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CapabilitySchemaError(f"Manifest file does not exist: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise CapabilitySchemaError(
            f"Invalid JSON in manifest file {file_path}: {exc.msg}"
        ) from exc

    if not isinstance(raw, dict):
        raise CapabilitySchemaError("Manifest root must be an object/map")

    return validate_manifest(raw)
