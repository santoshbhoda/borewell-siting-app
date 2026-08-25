"""
SQLAlchemy ORM Models for PostGIS / Relational Schema
Covers Users, Land Plots, Candidate Siting Spots, Ground-Truth Drilling Outcomes, and Service Providers.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    plots = relationship("LandPlot", back_populates="owner", cascade="all, delete-orphan")


class LandPlot(Base):
    __tablename__ = "land_plots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    plot_name = Column(String(150), nullable=False, default="Pilot Farm")
    state = Column(String(50), default="Telangana")
    district = Column(String(50), default="Yadadri-Bhuvanagiri")
    mandal = Column(String(50), nullable=True)
    village = Column(String(50), nullable=True)
    survey_number = Column(String(50), nullable=True)
    
    area_acres = Column(Float, nullable=False)
    area_hectares = Column(Float, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    
    # Boundary stored as GeoJSON polygon representation
    boundary_geojson = Column(JSON, nullable=False)
    
    mean_gwpi_score = Column(Float, nullable=False)
    potential_category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="plots")
    candidate_spots = relationship("CandidateSpot", back_populates="plot", cascade="all, delete-orphan")
    outcomes = relationship("DrillingOutcome", back_populates="plot", cascade="all, delete-orphan")


class CandidateSpot(Base):
    __tablename__ = "candidate_spots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id = Column(String(36), ForeignKey("land_plots.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False)
    label = Column(String(50), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    gwpi_score = Column(Float, nullable=False)
    potential_category = Column(String(50), nullable=False)
    elevation_m = Column(Float, nullable=False)
    slope_pct = Column(Float, nullable=False)
    estimated_depth_range = Column(String(50), nullable=False)
    expected_yield_range = Column(String(80), nullable=False)
    hydro_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plot = relationship("LandPlot", back_populates="candidate_spots")
    outcomes = relationship("DrillingOutcome", back_populates="candidate_spot")


class DrillingOutcome(Base):
    __tablename__ = "drilling_outcomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id = Column(String(36), ForeignKey("land_plots.id"), nullable=False)
    candidate_spot_id = Column(String(36), ForeignKey("candidate_spots.id"), nullable=True)
    
    drilled_lat = Column(Float, nullable=False)
    drilled_lon = Column(Float, nullable=False)
    actual_drilling_depth_ft = Column(Integer, nullable=False)
    water_strike_depth_ft = Column(Integer, nullable=True)
    casing_depth_ft = Column(Integer, nullable=True)
    measured_yield_lph = Column(Integer, nullable=True)
    yield_category = Column(String(30), nullable=False) # 'Dry', 'Low (<1")', 'Moderate (1-2")', 'High (>2")'
    ves_conducted = Column(Boolean, default=False)
    contractor_name = Column(String(120), nullable=True)
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plot = relationship("LandPlot", back_populates="outcomes")
    candidate_spot = relationship("CandidateSpot", back_populates="outcomes")


class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_name = Column(String(150), nullable=False)
    provider_type = Column(String(50), nullable=False) # 'VES_GEOPHYSICIST', 'DRILLING_CONTRACTOR', 'PUMP_INSTALLER'
    contact_phone = Column(String(20), nullable=False)
    whatsapp_number = Column(String(20), nullable=True)
    service_districts = Column(String(250), nullable=False) # e.g. "Yadadri-Bhuvanagiri, Nalgonda, Jangaon"
    equipment_specs = Column(String(250), nullable=True)
    rating = Column(Float, default=4.8)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
