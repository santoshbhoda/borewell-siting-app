"""
Database Seed & Initialization Script
Populates initial pilot farm (Karun Farm 2), initial verified providers, and sample outcomes.
"""
import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal, engine, Base
from backend.models import LandPlot, CandidateSpot, ServiceProvider, DrillingOutcome

Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(LandPlot).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding initial pilot data...")

        # 1. Seed Karun Farm 2
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        geojson_path = os.path.join(root, "data", "output", "farm_siting_report.geojson")
        
        with open(geojson_path, "r", encoding="utf-8") as f:
            farm_data = json.load(f)

        fa = farm_data["farm_analysis"]
        stats = fa["score_statistics"]

        pilot_plot = LandPlot(
            plot_name=fa["farm_name"],
            state="Telangana",
            district="Yadadri-Bhuvanagiri",
            mandal="Bhuvanagiri",
            village="Rayagiri",
            survey_number="142/A",
            area_acres=fa["farm_area_acres"],
            area_hectares=fa["farm_area_hectares"],
            centroid_lat=fa["centroid"]["lat"],
            centroid_lon=fa["centroid"]["lon"],
            boundary_geojson=farm_data["features"][0]["geometry"],
            mean_gwpi_score=stats["mean"],
            potential_category=stats["category"]
        )
        db.add(pilot_plot)
        db.flush()

        # Add candidate spots
        spot_objects = []
        for pt in fa["candidate_points"]:
            spot = CandidateSpot(
                plot_id=pilot_plot.id,
                rank=pt["rank"],
                label=pt["label"],
                lat=pt["lat"],
                lon=pt["lon"],
                gwpi_score=pt["gwpi_score"],
                potential_category=pt["potential_category"],
                elevation_m=pt["elevation_m"],
                slope_pct=pt["slope_pct"],
                estimated_depth_range=pt["estimated_depth_range"],
                expected_yield_range=pt["expected_yield_range"],
                hydro_summary=pt["hydro_summary"]
            )
            db.add(spot)
            spot_objects.append(spot)
        db.flush()

        # 2. Seed Sample Drilling Outcome for Spot #1
        sample_outcome = DrillingOutcome(
            plot_id=pilot_plot.id,
            candidate_spot_id=spot_objects[0].id,
            drilled_lat=spot_objects[0].lat,
            drilled_lon=spot_objects[0].lon,
            actual_drilling_depth_ft=340,
            water_strike_depth_ft=295,
            casing_depth_ft=55,
            measured_yield_lph=2200,
            yield_category="Moderate (1-2 inch)",
            ves_conducted=True,
            contractor_name="Sri Balaji Borewells (Bhuvanagiri)",
            feedback_notes="VES survey confirmed fracture at 90m (295 ft). Encountered steady 1.5-inch discharge."
        )
        db.add(sample_outcome)

        # 3. Seed Verified Service Providers in Yadadri / Jangaon
        providers = [
            ServiceProvider(
                business_name="Deccan Hydro-Geophysical Surveys",
                provider_type="VES_GEOPHYSICIST",
                contact_phone="+91-98480-12345",
                whatsapp_number="+91-98480-12345",
                service_districts="Yadadri-Bhuvanagiri, Nalgonda, Jangaon",
                equipment_specs="IGIS Digital Signal Resistivity Meter (DSR-4), Schlumberger Sounding up to AB/2=200m",
                rating=4.9,
                is_verified=True
            ),
            ServiceProvider(
                business_name="Sri Balaji High-Pressure Rig Services",
                provider_type="DRILLING_CONTRACTOR",
                contact_phone="+91-94401-67890",
                whatsapp_number="+91-94401-67890",
                service_districts="Yadadri-Bhuvanagiri, Medchal, Siddipet",
                equipment_specs="1100 CFM / 300 PSI Ashok Leyland High-Pressure Rig, 6.5\" DTH Hammer",
                rating=4.8,
                is_verified=True
            ),
            ServiceProvider(
                business_name="Telangana Solar & Submersible Pumps",
                provider_type="PUMP_INSTALLER",
                contact_phone="+91-99890-54321",
                whatsapp_number="+91-99890-54321",
                service_districts="Yadadri-Bhuvanagiri, Warangal, Jangaon",
                equipment_specs="CRI / Texmo 3HP–7.5HP 100% Copper Submersible Sets & Solar VFD Controllers",
                rating=4.7,
                is_verified=True
            )
        ]
        db.add_all(providers)

        db.commit()
        print("Database successfully seeded with pilot plot, outcomes, and providers.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
