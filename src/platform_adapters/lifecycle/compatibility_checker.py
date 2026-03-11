"""Adapter/runtime compatibility checks."""

from __future__ import annotations

from platform_adapters.contracts import CapabilityManifest
from platform_adapters.errors import CompatibilityError


def _parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise CompatibilityError(f"Invalid semantic version: {version}")
    major, minor, patch = (int(part) for part in parts)
    return major, minor, patch


class CompatibilityChecker:
    """Checks adapter version compatibility against runtime SDK version."""

    def __init__(self, sdk_version: str) -> None:
        self.sdk_version = sdk_version
        self._sdk_major, self._sdk_minor, _ = _parse_version(sdk_version)

    def ensure_compatible(self, manifest: CapabilityManifest) -> None:
        adapter_major, adapter_minor, _ = _parse_version(manifest.version)
        if adapter_major != self._sdk_major:
            raise CompatibilityError(
                f"Major version mismatch: sdk={self.sdk_version}, adapter={manifest.version}"
            )
        if adapter_minor > self._sdk_minor:
            raise CompatibilityError(
                "Adapter minor version is newer than runtime SDK and is not supported: "
                f"sdk={self.sdk_version}, adapter={manifest.version}"
            )
