"""
FastAPI REST Application & Webhooks for Sepsis-3 Resuscitation Sentinel: Dynamic Lactate Clearance & Bundle Compliance Agent.
"""
from typing import Dict, Any, Optional
from .models import ClinicalCasePayload
from .agents import SepsisCoordinator

coordinator = SepsisCoordinator()

def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
        from fastapi import HTTPException
        from agents.base import assert_no_phi, SecurityException

        app = FastAPI(
            title="Sepsis-3 Resuscitation Sentinel: Dynamic Lactate Clearance & Bundle Compliance Agent",
            description="Historical threshold and keyword demonstration. Does not implement actual bundle timing, lactate clearance, or validated clinical alerts.",
            version="2.0.0-PRO",
        )

        class AuditRequest(BaseModel):
            case_id: str = "CASE-2026-001"
            patient_synthetic_id: str = "SYNTH-PT-881"
            primary_metric: float = Field(default=24.5, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.0, allow_inf_nan=False)
            status_flag: str = "DISCORDANT"
            is_stat: bool = True
            clinical_notes: str = ""
            biomarkers: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "sepsis-resuscitation-agent", "domain": "Critical Care", "version": "2.0.0-PRO"}

        @app.post("/api/audit")
        def api_audit(req: AuditRequest):
            try:
                assert_no_phi(req.model_dump())
            except SecurityException:
                raise HTTPException(status_code=422, detail="Input contains a sensitive identifier")
            payload = ClinicalCasePayload(
                case_id=req.case_id,
                patient_synthetic_id=req.patient_synthetic_id,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_flag=req.status_flag,
                is_stat=req.is_stat,
                clinical_notes=req.clinical_notes,
                biomarkers=req.biomarkers,
            )
            return coordinator.process_case(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
