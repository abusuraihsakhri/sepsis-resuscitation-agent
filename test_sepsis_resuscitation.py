import pytest
from sepsis_resuscitation import BundleClockTimerAgent, LactateKineticsAgent, VasopressorTitrationAgent, SepsisCoordinator, main


def test_sub_agents():
    a1 = BundleClockTimerAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = LactateKineticsAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = VasopressorTitrationAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_coordinator():
    coord = SepsisCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from sepsis_resuscitation import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is False
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION


def test_advisory_only_is_not_reported_as_normal():
    from sepsis_resuscitation import SepsisCoordinator
    dossier = SepsisCoordinator().audit_case({
        "case_id": "SYNTH-ADVISORY",
        "metric_primary": 1.0,
        "metric_secondary": 1.0,
        "critical_flag": False,
        "status_text": "DISCORDANT",
    })
    assert dossier["total_alerts"] == 1
    assert dossier["overall_status"] == "ADVISORY_ACTIVE"
