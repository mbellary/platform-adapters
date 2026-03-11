"""Integration tests for capability registration and lifecycle boot flow."""

from pathlib import Path

from platform_adapters.adapter_registry.adapter_registry import AdapterRegistry
from platform_adapters.adapter_registry.capability_publisher import CapabilityPublisher
from platform_adapters.adapter_registry.registry_loader import load_manifest, validate_manifest
from platform_adapters.contracts import HealthReport, HealthStatus
from platform_adapters.errors import AdapterHealthError, CapabilitySchemaError, CompatibilityError
from platform_adapters.lifecycle.adapter_loader import AdapterLoader


class _HealthyAdapter:
    def check_health(self) -> HealthReport:
        return HealthReport(status=HealthStatus.HEALTHY, details={"latency_ms": 4})


class _UnhealthyAdapter:
    def check_health(self) -> HealthReport:
        return HealthReport(status=HealthStatus.UNHEALTHY, details={"reason": "dependency-down"})


def test_load_manifest_validates_schema() -> None:
    try:
        validate_manifest({"schema_version": "1.0"})
    except CapabilitySchemaError as exc:
        assert "Missing required manifest fields" in str(exc)
    else:
        raise AssertionError("Expected CapabilitySchemaError")


def test_boot_flow_registers_and_indexes_adapter(tmp_path: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "adapter_id": "aws-core",
        "name": "AWS Core",
        "provider": "aws",
        "version": "1.2.0",
        "domain": "cloud",
        "capabilities": ["compute", "registry"],
        "metadata": {"tier": "prod"},
    }
    path = tmp_path / "manifest.json"
    path.write_text(__import__("json").dumps(payload), encoding="utf-8")

    registry = AdapterRegistry()
    loader = AdapterLoader(registry=registry, sdk_version="1.3.0")
    record = loader.boot_from_manifest_file(manifest_path=str(path), adapter=_HealthyAdapter())

    assert record.adapter_id == "aws-core"
    assert load_manifest(path).adapter_id == "aws-core"

    indexes = CapabilityPublisher(registry).build_indexes()
    assert tuple(m.adapter_id for m in indexes["provider"]["aws"]) == ("aws-core",)
    assert tuple(m.adapter_id for m in indexes["capability"]["compute"]) == ("aws-core",)


def test_boot_flow_blocks_incompatible_or_unhealthy_adapters() -> None:
    manifest = validate_manifest(
        {
            "schema_version": "1.0",
            "adapter_id": "aws-edge",
            "name": "AWS Edge",
            "provider": "aws",
            "version": "2.0.0",
            "domain": "cloud",
            "capabilities": ["compute"],
        }
    )

    loader = AdapterLoader(registry=AdapterRegistry(), sdk_version="1.9.0")

    try:
        loader.boot(manifest=manifest, adapter=_HealthyAdapter())
    except CompatibilityError:
        pass
    else:
        raise AssertionError("Expected CompatibilityError")

    manifest_v1 = validate_manifest(
        {
            "schema_version": "1.0",
            "adapter_id": "aws-edge2",
            "name": "AWS Edge",
            "provider": "aws",
            "version": "1.0.0",
            "domain": "cloud",
            "capabilities": ["compute"],
        }
    )

    try:
        loader.boot(manifest=manifest_v1, adapter=_UnhealthyAdapter())
    except AdapterHealthError:
        pass
    else:
        raise AssertionError("Expected AdapterHealthError")
