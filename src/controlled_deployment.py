"""Deterministic controlled-deployment authorization gate for EXEC-003."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentEvidence:
    """Caller-supplied operational evidence for controlled deployment."""

    runtime_ready: bool
    paper_verification_passed: bool
    operator_approved: bool
    rollback_plan_ready: bool
    kill_switch_ready: bool
    execution_lock_enabled: bool


@dataclass(frozen=True)
class DeploymentAuthorization:
    """Immutable result of the EXEC-003 authorization gate."""

    approved: bool
    reasons: tuple[str, ...]


class ControlledDeploymentGate:
    """Validate deployment evidence without enabling or submitting live orders."""

    def evaluate(self, evidence: DeploymentEvidence) -> DeploymentAuthorization:
        if not isinstance(evidence, DeploymentEvidence):
            raise TypeError("evidence must be DeploymentEvidence")

        reasons: list[str] = []
        checks = (
            (evidence.runtime_ready, "EXEC-002 runtime readiness is required"),
            (evidence.paper_verification_passed, "paper verification must pass"),
            (evidence.operator_approved, "explicit operator approval is required"),
            (evidence.rollback_plan_ready, "rollback plan must be ready"),
            (evidence.kill_switch_ready, "independent kill switch must be ready"),
            (
                evidence.execution_lock_enabled,
                "execution lock must remain enabled until controlled handoff",
            ),
        )
        for passed, reason in checks:
            if not passed:
                reasons.append(reason)

        return DeploymentAuthorization(approved=not reasons, reasons=tuple(reasons))
