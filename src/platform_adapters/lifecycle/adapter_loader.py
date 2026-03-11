"""Adapter lifecycle boot service."""

from __future__ import annotations

from dataclasses import dataclass

from platform_adapters.adapter_registry.adapter_registry import AdapterRegistry
from platform_adapters.adapter_registry.registry_loader import load_manifest
from platform_adapters.contracts import CapabilityManifest, HealthCheckable
from platform_adapters.lifecycle.adapter_health_check import AdapterHealthCheck
from platform_adapters.lifecycle.adapter_validator import AdapterValidator
from platform_adapters.lifecycle.compatibility_checker import CompatibilityChecker


@dataclass(slots=True, frozen=True)
class AdapterBootRecord:
    """Immutable audit-like record for adapter boot operations."""

    adapter_id: str
    provider: str
    version: str
    domain: str


class AdapterLoader:
    """End-to-end loader for manifest validation, compatibility, and registration."""

    def __init__(self, *, registry: AdapterRegistry, sdk_version: str) -> None:
        self._registry = registry
        self._compatibility = CompatibilityChecker(sdk_version=sdk_version)

    def boot_from_manifest_file(
        self, *, manifest_path: str, adapter: HealthCheckable
    ) -> AdapterBootRecord:
        manifest = load_manifest(manifest_path)
        return self.boot(manifest=manifest, adapter=adapter)

    def boot(self, *, manifest: CapabilityManifest, adapter: HealthCheckable) -> AdapterBootRecord:
        AdapterValidator.validate(manifest)
        self._compatibility.ensure_compatible(manifest)
        AdapterHealthCheck.run(adapter)
        self._registry.register(manifest)
        return AdapterBootRecord(
            adapter_id=manifest.adapter_id,
            provider=manifest.provider,
            version=manifest.version,
            domain=manifest.domain,
        )
