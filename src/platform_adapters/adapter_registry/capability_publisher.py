"""Capability index views for fast adapter discovery."""

from __future__ import annotations

from collections import defaultdict

from platform_adapters.adapter_registry.adapter_registry import AdapterRegistry
from platform_adapters.contracts import CapabilityManifest


class CapabilityPublisher:
    """Builds deterministic capability/provider indexes over an adapter registry."""

    def __init__(self, registry: AdapterRegistry) -> None:
        self._registry = registry

    def build_indexes(self) -> dict[str, dict[str, tuple[CapabilityManifest, ...]]]:
        by_provider: dict[str, list[CapabilityManifest]] = defaultdict(list)
        by_capability: dict[str, list[CapabilityManifest]] = defaultdict(list)

        for manifest in self._registry.list_all():
            by_provider[manifest.provider.lower()].append(manifest)
            for capability in manifest.capabilities:
                by_capability[capability.lower()].append(manifest)

        def _freeze(
            index: dict[str, list[CapabilityManifest]],
        ) -> dict[str, tuple[CapabilityManifest, ...]]:
            return {
                key: tuple(sorted(value, key=lambda item: item.adapter_id))
                for key, value in sorted(index.items())
            }

        return {
            "provider": _freeze(by_provider),
            "capability": _freeze(by_capability),
        }
