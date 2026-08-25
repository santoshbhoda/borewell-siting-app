"""
Feedback Router: Ground-Truth Drilling Outcome Ingestion (ML Data Flywheel)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import LandPlot, DrillingOutcome
from backend.schemas import FeedbackSubmissionRequest, FeedbackResponse

router = APIRouter(prefix="/plots", tags=["Ground-Truth Feedback Loop"])


@router.post("/{plot_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_drilling_feedback(
    plot_id: str,
    payload: FeedbackSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    Submits real-world post-drilling outcome data (depth, water strike, measured discharge yield).
    Feeds the ground-truth flywheel for Phase 2 Supervised ML model retraining.
    """
    db_plot = db.query(LandPlot).filter(LandPlot.id == plot_id).first()
    if not db_plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    outcome = DrillingOutcome(
        plot_id=plot_id,
        candidate_spot_id=payload.candidate_spot_id,
        drilled_lat=payload.drilled_lat,
        drilled_lon=payload.drilled_lon,
        actual_drilling_depth_ft=payload.actual_drilling_depth_ft,
        water_strike_depth_ft=payload.water_strike_depth_ft,
        casing_depth_ft=payload.casing_depth_ft,
        measured_yield_lph=payload.measured_yield_lph,
        yield_category=payload.yield_category,
        ves_conducted=payload.ves_conducted,
        contractor_name=payload.contractor_name,
        feedback_notes=payload.feedback_notes
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return FeedbackResponse(
        id=outcome.id,
        plot_id=outcome.plot_id,
        status="Recorded",
        message="Ground-truth drilling outcome recorded successfully. Added to ML training feature store.",
        created_at=outcome.created_at
    )
