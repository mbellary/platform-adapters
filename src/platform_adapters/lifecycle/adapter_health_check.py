"""Adapter health checking service."""

from __future__ import annotations

from platform_adapters.contracts import HealthCheckable, HealthStatus
from platform_adapters.errors import AdapterHealthError


class AdapterHealthCheck:
    """Runs health checks and enforces healthy/degraded status rules."""

    @staticmethod
    def run(adapter: HealthCheckable) -> None:
        report = adapter.check_health()
        if report.status == HealthStatus.UNHEALTHY:
            raise AdapterHealthError(f"Adapter reported unhealthy status: {report.details}")
