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



def test_audit_signatures_detect_mutation():
    trail = AuditTrail(secret_key="test-signature-key")
    trail.log("worker", "test", "FIRST", {"sample": "synthetic"})
    trail.log("worker", "test", "SECOND", {"sample": "synthetic"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "injected"
    assert trail.verify_integrity(), "Caller must not be able to edit audit log through API"
    trail.logs[0]["actor"] = "injected"
    assert not trail.verify_integrity(), "Signing every field must detect tampering"


def test_nested_phi_and_nonfinite_values_rejected():
    from pydantic import ValidationError
    from agents.base import assert_no_phi
    with pytest.raises(SecurityException):
        assert_no_phi({"metadata": [{"notes": "MRN: 1234567"}]})
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="X", primary_metric=float("nan"))


def test_csv_boolean_parsing():
    from cli import _parse_csv_bool
    from sepsis_resuscitation_agent.cli import _parse_csv_bool as clinical_parse
    for parser in (_parse_csv_bool, clinical_parse):
        assert parser("false") is False
        assert parser(" TRUE ") is True
        assert parser("0") is False
        with pytest.raises(ValueError):
            parser("sometimes")


def test_csv_batch_false_flag(tmp_path, monkeypatch):
    import csv
    import cli
    monkeypatch.chdir(tmp_path)
    with open("in.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id","target_identifier","primary_metric","secondary_metric","is_critical_flag"])
        writer.writeheader()
        writer.writerow({"task_id":"T","target_identifier":"SYNTH","primary_metric":2,"secondary_metric":2,"is_critical_flag":"false"})
    assert cli.main(["batch","-i","in.csv","-o","out.csv"]) == 0
    with open("out.csv", newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["overall_urgency"] == "ROUTINE"
    assert cli.main(["batch","-i","in.csv","-o","in.csv"]) == 1


def test_api_phi_rejection():
    from fastapi.testclient import TestClient
    from agents.api import app
    with TestClient(app) as client:
        response = client.post("/api/audit", json={
            "task_id":"T", "target_identifier":"SYNTH",
            "primary_metric":1, "attributes":{"notes":["MRN: 1234567"]}
        })
        assert response.status_code == 422
        assert "1234567" not in response.text



def test_api_contract_synthetic_payload():
    from fastapi.testclient import TestClient
    from agents.api import app
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["clinical_validation"] is False
        response = client.post("/api/audit", json={
            "task_id": "DEMO-API", "target_identifier": "SYNTH-API",
            "primary_metric": 28, "secondary_metric": 3,
            "status_descriptor": "NOMINAL", "is_critical_flag": False
        })
        assert response.status_code == 200
        assert response.json()["task_id"] == "DEMO-API"
        assert isinstance(client.get("/metrics").json()["dossiers_processed_total"], int)
        assert "audit_trail" in client.get("/api/audit/logs").json()
        assert "No model inference" in client.post("/api/chat", json={"query":"system status"}).json()["response"]



def test_concurrent_audit_logging_keeps_valid_chain():
    from concurrent.futures import ThreadPoolExecutor
    trail = AuditTrail(secret_key="test-concurrent-key")
    def make_entry(i):
        return trail.log("worker", "test", "EVALUATE", {"index": i})
    with ThreadPoolExecutor(max_workers=8) as executor:
        entries = list(executor.map(make_entry, range(100)))
    assert len(entries) == 100
    assert len(trail.get_trail()) == 100
    assert trail.verify_integrity()
