"""Deterministic production-runtime readiness gate for EXEC-002.

This module records and validates runtime prerequisites without performing any
network calls, credential access, broker submission, or public-IP discovery.
The caller must provide independently verified runtime evidence.
"""

from dataclasses import dataclass
from enum import StrEnum


class RuntimeEnvironment(StrEnum):
    """Execution environments recognized by the runtime gate."""

    DEVELOPMENT = "development"
    PAPER = "paper"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class RuntimeEvidence:
    """Caller-supplied evidence about the execution runtime."""

    environment: RuntimeEnvironment
    registered_static_ip: str | None
    observed_public_ip: str | None
    execution_lock_enabled: bool
    kill_switch_ready: bool
    credential_reference_configured: bool


@dataclass(frozen=True)
class RuntimeReadiness:
    """Immutable result of the EXEC-002 readiness gate."""

    approved: bool
    reasons: tuple[str, ...]


class ProductionRuntimeGate:
    """Validate production-runtime prerequisites without enabling execution."""

    def evaluate(self, evidence: RuntimeEvidence) -> RuntimeReadiness:
        if not isinstance(evidence, RuntimeEvidence):
            raise TypeError("evidence must be RuntimeEvidence")

        reasons: list[str] = []

        if evidence.environment is not RuntimeEnvironment.PRODUCTION:
            reasons.append("production environment is required")
        if not evidence.registered_static_ip:
            reasons.append("registered static IP is required")
        if not evidence.observed_public_ip:
            reasons.append("observed public IP is required")
        if (
            evidence.registered_static_ip
            and evidence.observed_public_ip
            and evidence.registered_static_ip != evidence.observed_public_ip
        ):
            reasons.append("observed public IP does not match registered static IP")
        if not evidence.execution_lock_enabled:
            reasons.append("execution lock must remain enabled until runtime approval")
        if not evidence.kill_switch_ready:
            reasons.append("independent kill switch must be ready")
        if not evidence.credential_reference_configured:
            reasons.append("credential reference must be configured")

        return RuntimeReadiness(approved=not reasons, reasons=tuple(reasons))
