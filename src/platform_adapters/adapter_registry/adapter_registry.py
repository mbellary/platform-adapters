"""In-memory adapter registry implementation."""

from __future__ import annotations

from collections.abc import Callable

from platform_adapters.contracts import CapabilityManifest
from platform_adapters.errors import AdapterNotFoundError, AdapterRegistrationError


class AdapterRegistry:
    """Deterministic adapter registry with capability/provider indexing."""

    def __init__(self) -> None:
        self._entries: dict[str, CapabilityManifest] = {}

    def register(self, manifest: CapabilityManifest) -> None:
        if manifest.adapter_id in self._entries:
            raise AdapterRegistrationError(f"Adapter id already registered: {manifest.adapter_id}")
        self._entries[manifest.adapter_id] = manifest

    def get(self, adapter_id: str) -> CapabilityManifest:
        try:
            return self._entries[adapter_id]
        except KeyError as exc:
            raise AdapterNotFoundError(f"Adapter not found: {adapter_id}") from exc

    def list_all(self) -> list[CapabilityManifest]:
        return [self._entries[key] for key in sorted(self._entries)]

    def filter(self, predicate: Callable[[CapabilityManifest], bool]) -> list[CapabilityManifest]:
        return [item for item in self.list_all() if predicate(item)]

    def by_provider(self, provider: str) -> list[CapabilityManifest]:
        value = provider.strip().lower()
        return self.filter(lambda m: m.provider.lower() == value)

    def by_capability(self, capability: str) -> list[CapabilityManifest]:
        value = capability.strip().lower()
        return self.filter(lambda m: value in {c.lower() for c in m.capabilities})
