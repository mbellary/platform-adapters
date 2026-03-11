"""Shared adapter contracts and protocol models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class HealthStatus(str, Enum):
    """Canonical health statuses for adapter components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(slots=True, frozen=True)
class HealthReport:
    """Structured health response emitted by adapters."""

    status: HealthStatus
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CapabilityManifest:
    """Canonical manifest schema used for registration and discovery."""

    schema_version: str
    adapter_id: str
    name: str
    provider: str
    version: str
    domain: str
    capabilities: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


class ArtifactStoreAdapter(Protocol):
    """Contract for artifact storage providers."""

    def put_artifact(self, *, key: str, payload: bytes) -> str: ...

    def get_artifact(self, *, key: str) -> bytes: ...


class ComputeAdapter(Protocol):
    """Contract for compute execution providers."""

    def run(self, *, job_spec: dict[str, Any]) -> dict[str, Any]: ...


class RegistryAdapter(Protocol):
    """Contract for model/artifact metadata registry providers."""

    def register(self, *, name: str, payload: dict[str, Any]) -> str: ...


class TelemetryAdapter(Protocol):
    """Contract for metrics/trace emission providers."""

    def emit(self, *, event_name: str, attributes: dict[str, Any]) -> None: ...


class HealthCheckable(Protocol):
    """Contract for adapters exposing health endpoints."""

    def check_health(self) -> HealthReport: ...
