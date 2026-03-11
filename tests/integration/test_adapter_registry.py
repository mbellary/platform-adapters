"""Integration tests for adapter registry operations."""

from platform_adapters.adapter_registry.adapter_registry import AdapterRegistry
from platform_adapters.adapter_registry.registry_loader import validate_manifest
from platform_adapters.errors import AdapterNotFoundError, AdapterRegistrationError


def _manifest(adapter_id: str, *, provider: str = "aws", capabilities: list[str] | None = None):
    return validate_manifest(
        {
            "schema_version": "1.0",
            "adapter_id": adapter_id,
            "name": f"{adapter_id}-name",
            "provider": provider,
            "version": "1.0.0",
            "domain": "cloud",
            "capabilities": capabilities or ["artifact_store"],
            "metadata": {"region": "us-east-1"},
        }
    )


def test_registry_register_get_and_deterministic_list() -> None:
    registry = AdapterRegistry()
    registry.register(_manifest("b-adapter"))
    registry.register(_manifest("a-adapter"))

    assert [item.adapter_id for item in registry.list_all()] == ["a-adapter", "b-adapter"]
    assert registry.get("a-adapter").provider == "aws"


def test_registry_filters_by_provider_and_capability() -> None:
    registry = AdapterRegistry()
    registry.register(_manifest("aws-a", provider="aws", capabilities=["compute", "registry"]))
    registry.register(_manifest("gcp-a", provider="gcp", capabilities=["compute"]))

    assert [m.adapter_id for m in registry.by_provider("aws")] == ["aws-a"]
    assert [m.adapter_id for m in registry.by_capability("compute")] == ["aws-a", "gcp-a"]


def test_registry_rejects_duplicates_and_missing_entries() -> None:
    registry = AdapterRegistry()
    manifest = _manifest("dup")
    registry.register(manifest)

    try:
        registry.register(manifest)
    except AdapterRegistrationError:
        pass
    else:
        raise AssertionError("Expected AdapterRegistrationError")

    try:
        registry.get("missing")
    except AdapterNotFoundError:
        pass
    else:
        raise AssertionError("Expected AdapterNotFoundError")
