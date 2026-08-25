"""
Pydantic Validation Schemas for FastAPI Endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Coordinate(BaseModel):
    lon: float
    lat: float


class PlotEvaluationRequest(BaseModel):
    plot_name: str = Field(default="Custom Farm Plot", description="Name of the farm parcel")
    coordinates: List[List[float]] = Field(..., description="Array of [lon, lat] coordinates forming a closed polygon")
    state: str = Field(default="Telangana")
    district: str = Field(default="Yadadri-Bhuvanagiri")
    mandal: Optional[str] = None
    village: Optional[str] = None
    survey_number: Optional[str] = None


class PinEvaluationRequest(BaseModel):
    lat: float = Field(..., description="Latitude of dropped pin")
    lon: float = Field(..., description="Longitude of dropped pin")
    radius_meters: float = Field(default=250.0, description="Evaluation radius around pin")
    plot_name: Optional[str] = Field(default="Pin Sited Farm")


class CandidateSpotSchema(BaseModel):
    rank: int
    label: str
    lat: float
    lon: float
    gwpi_score: float
    potential_category: str
    elevation_m: float
    slope_pct: float
    estimated_depth_range: str
    expected_yield_range: str
    hydro_summary: str


class PlotResponse(BaseModel):
    id: str
    plot_name: str
    state: str
    district: str
    mandal: Optional[str] = None
    village: Optional[str] = None
    survey_number: Optional[str] = None
    area_acres: float
    area_hectares: float
    centroid: Dict[str, float]
    mean_gwpi_score: float
    potential_category: str
    candidate_spots: List[CandidateSpotSchema]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSubmissionRequest(BaseModel):
    candidate_spot_id: Optional[str] = None
    drilled_lat: float
    drilled_lon: float
    actual_drilling_depth_ft: int = Field(..., description="Total depth drilled in feet")
    water_strike_depth_ft: Optional[int] = Field(None, description="Depth at which primary water fracture was struck")
    casing_depth_ft: Optional[int] = Field(None, description="Depth of casing pipe installed")
    measured_yield_lph: Optional[int] = Field(None, description="Discharge yield measured in LPH")
    yield_category: str = Field(..., description="'High (>2 inch)', 'Moderate (1-2 inch)', 'Low (<1 inch)', 'Dry'")
    ves_conducted: bool = Field(default=False, description="Whether a VES resistivity test was done prior to drilling")
    contractor_name: Optional[str] = None
    feedback_notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    plot_id: str
    status: str
    message: str
    created_at: datetime


class AnalyticsSummaryResponse(BaseModel):
    total_plots_evaluated: int
    total_acres_evaluated: float
    total_outcomes_reported: int
    success_rate_percentage: float
    average_drilling_depth_ft: float
    pilot_region: str


class ProviderResponse(BaseModel):
    id: str
    business_name: str
    provider_type: str
    contact_phone: str
    whatsapp_number: Optional[str] = None
    service_districts: str
    equipment_specs: Optional[str] = None
    rating: float
    is_verified: bool

    class Config:
        from_attributes = True
