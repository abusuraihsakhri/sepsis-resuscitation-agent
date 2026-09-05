"""
Automated Pytest Test Suite for Sepsis Resuscitation Agent.
Domain: Privacy-Preserving Federated Healthcare & FHE
Standard: HIPAA Safe Harbor §164.514 / Google SecAgg Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main, _validate_safe_path


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_path_traversal_protection():
    """Test that path traversal attempts are blocked."""
    # Attempt path traversal with ../
    with pytest.raises(ValueError, match="Path traversal detected"):
        _validate_safe_path("../etc/passwd")

    # Attempt absolute path outside working directory
    with pytest.raises(ValueError, match="Path traversal detected"):
        _validate_safe_path("/etc/passwd")


def test_hmac_key_generation_without_env():
    """Test that AuditTrail generates a secure key when no env var is set."""
    import os
    # Save and clear any existing env var
    original_key = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            # Should have generated a warning about missing key
            assert len(w) == 1
            assert "AUDIT_SECRET_KEY not set" in str(w[0].message)
            # Key should be set (64 hex chars = 32 bytes)
            assert len(trail.secret_key) == 64
    finally:
        # Restore original env var if it existed
        if original_key is not None:
            os.environ["AUDIT_SECRET_KEY"] = original_key


def test_batch_processing_with_sample_csv():
    """Test batch CLI command with sample CSV data."""
    import tempfile
    import os

    # Create a temporary CSV file in the working directory (not system temp)
    # because path traversal protection requires paths to be within working directory
    temp_input = os.path.join(os.getcwd(), '_test_batch_input.csv')
    temp_output = os.path.join(os.getcwd(), '_test_batch_output.csv')

    try:
        with open(temp_input, 'w', newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n")
            f.write("T1,KEY-01,12.0,4.0,NOMINAL,false\n")
            f.write("T2,KEY-02,35.0,15.0,DISCORDANT_ANOMALY,true\n")

        # Run batch command
        result = main(["batch", "-i", temp_input, "-o", temp_output])
        assert result == 0
        assert os.path.exists(temp_output)
    finally:
        # Cleanup
        if os.path.exists(temp_input):
            os.unlink(temp_input)
        if os.path.exists(temp_output):
            os.unlink(temp_output)
