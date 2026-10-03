from src.execution_runtime import (
    ProductionRuntimeGate,
    RuntimeEnvironment,
    RuntimeEvidence,
)


def evidence(**overrides: object) -> RuntimeEvidence:
    values: dict[str, object] = {
        "environment": RuntimeEnvironment.PRODUCTION,
        "registered_static_ip": "203.0.113.10",
        "observed_public_ip": "203.0.113.10",
        "execution_lock_enabled": True,
        "kill_switch_ready": True,
        "credential_reference_configured": True,
    }
    values.update(overrides)
    return RuntimeEvidence(**values)


def test_production_runtime_is_ready_only_with_matching_static_ip() -> None:
    result = ProductionRuntimeGate().evaluate(evidence())
    assert result.approved is True
    assert result.reasons == ()


def test_non_production_environment_is_rejected() -> None:
    result = ProductionRuntimeGate().evaluate(
        evidence(environment=RuntimeEnvironment.STAGING)
    )
    assert result.approved is False
    assert "production environment is required" in result.reasons


def test_static_ip_mismatch_is_rejected() -> None:
    result = ProductionRuntimeGate().evaluate(
        evidence(observed_public_ip="203.0.113.11")
    )
    assert result.approved is False
    assert "observed public IP does not match registered static IP" in result.reasons


def test_kill_switch_and_lock_are_required() -> None:
    result = ProductionRuntimeGate().evaluate(
        evidence(execution_lock_enabled=False, kill_switch_ready=False)
    )
    assert result.approved is False
    assert "execution lock must remain enabled until runtime approval" in result.reasons
    assert "independent kill switch must be ready" in result.reasons


def test_credential_reference_is_required_without_exposing_secret() -> None:
    result = ProductionRuntimeGate().evaluate(
        evidence(credential_reference_configured=False)
    )
    assert result.approved is False
    assert "credential reference must be configured" in result.reasons


def test_invalid_evidence_type_is_rejected() -> None:
    try:
        ProductionRuntimeGate().evaluate(object())  # type: ignore[arg-type]
    except TypeError as exc:
        assert str(exc) == "evidence must be RuntimeEvidence"
    else:
        raise AssertionError("expected TypeError")
