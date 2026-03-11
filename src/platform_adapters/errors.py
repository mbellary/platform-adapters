"""Error taxonomy and reliability semantics for the platform adapter runtime."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetryMetadata:
    """Retryability metadata for runtime policy decisions."""

    retryable: bool
    transient: bool


class AdapterRuntimeError(Exception):
    """Base runtime error carrying reliability semantics."""

    retryable: bool = False
    transient: bool = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    @property
    def reliability(self) -> RetryMetadata:
        return RetryMetadata(retryable=self.retryable, transient=self.transient)


class AdapterValidationError(AdapterRuntimeError):
    """Raised when adapter config/manifest validation fails."""


class CapabilitySchemaError(AdapterValidationError):
    """Raised for capability manifest schema violations."""


class AdapterRegistrationError(AdapterRuntimeError):
    """Raised when adapter registration/discovery operations fail."""


class AdapterNotFoundError(AdapterRegistrationError):
    """Raised when adapter lookup misses the registry."""


class CompatibilityError(AdapterRuntimeError):
    """Raised when runtime SDK and adapter versions are incompatible."""


class AdapterHealthError(AdapterRuntimeError):
    """Raised when adapter health checks fail."""

    retryable = True
    transient = True
