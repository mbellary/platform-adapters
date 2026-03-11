"""Adapter validation services."""

from __future__ import annotations

from platform_adapters.contracts import CapabilityManifest
from platform_adapters.errors import AdapterValidationError


class AdapterValidator:
    """Validates semantic manifest constraints beyond schema checks."""

    @staticmethod
    def validate(manifest: CapabilityManifest) -> None:
        if len(manifest.capabilities) != len(set(manifest.capabilities)):
            raise AdapterValidationError(
                f"Duplicate capabilities found for adapter '{manifest.adapter_id}'"
            )
        if manifest.adapter_id.lower() != manifest.adapter_id:
            raise AdapterValidationError("Adapter id must be lowercase for canonical registry keys")
