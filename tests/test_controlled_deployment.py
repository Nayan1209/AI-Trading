from src.controlled_deployment import ControlledDeploymentGate, DeploymentEvidence


def evidence(**overrides: object) -> DeploymentEvidence:
    values: dict[str, object] = {
        "runtime_ready": True,
        "paper_verification_passed": True,
        "operator_approved": True,
        "rollback_plan_ready": True,
        "kill_switch_ready": True,
        "execution_lock_enabled": True,
    }
    values.update(overrides)
    return DeploymentEvidence(**values)


def test_complete_deployment_evidence_is_approved() -> None:
    result = ControlledDeploymentGate().evaluate(evidence())
    assert result.approved is True
    assert result.reasons == ()


def test_runtime_must_be_ready() -> None:
    result = ControlledDeploymentGate().evaluate(evidence(runtime_ready=False))
    assert result.approved is False
    assert "EXEC-002 runtime readiness is required" in result.reasons


def test_paper_verification_and_operator_approval_are_required() -> None:
    result = ControlledDeploymentGate().evaluate(
        evidence(paper_verification_passed=False, operator_approved=False)
    )
    assert result.approved is False
    assert "paper verification must pass" in result.reasons
    assert "explicit operator approval is required" in result.reasons


def test_rollback_and_kill_switch_are_required() -> None:
    result = ControlledDeploymentGate().evaluate(
        evidence(rollback_plan_ready=False, kill_switch_ready=False)
    )
    assert result.approved is False
    assert "rollback plan must be ready" in result.reasons
    assert "independent kill switch must be ready" in result.reasons


def test_execution_lock_must_remain_enabled() -> None:
    result = ControlledDeploymentGate().evaluate(
        evidence(execution_lock_enabled=False)
    )
    assert result.approved is False
    assert "execution lock must remain enabled until controlled handoff" in result.reasons


def test_invalid_evidence_type_is_rejected() -> None:
    try:
        ControlledDeploymentGate().evaluate(object())  # type: ignore[arg-type]
    except TypeError as exc:
        assert str(exc) == "evidence must be DeploymentEvidence"
    else:
        raise AssertionError("expected TypeError")
