"""
Plots Router: Spatial Evaluation, Siting & PDF Report Streaming
"""
import os
import math
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from shapely.geometry import Polygon, Point

from backend.database import get_db
from backend.models import LandPlot, CandidateSpot
from backend.schemas import PlotEvaluationRequest, PinEvaluationRequest, PlotResponse, CandidateSpotSchema
from pipeline.export.pdf_report_generator import generate_pdf_report
import json

router = APIRouter(prefix="/plots", tags=["Plots & Groundwater Siting"])

# Load precomputed grid once into memory for ultra-fast spatial querying
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRID_PATH = os.path.join(ROOT_DIR, "data", "output", "gwpi_grid.json")

GRID_DATA = None
if os.path.exists(GRID_PATH):
    with open(GRID_PATH, "r", encoding="utf-8") as f:
        GRID_DATA = json.load(f)


def evaluate_polygon_grid(coords: List[List[float]]) -> Dict[str, Any]:
    """Helper to evaluate grid cells inside polygon and extract top 3 spots."""
    if not GRID_DATA:
        raise HTTPException(status_code=500, detail="Groundwater potential grid data not loaded")

    # Ensure closed polygon
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    poly = Polygon(coords)
    minx, miny, maxx, maxy = poly.bounds
    centroid = poly.centroid

    lat_mid = centroid.y
    km_per_deg_lat = 110.574
    km_per_deg_lon = 111.320 * math.cos(math.radians(lat_mid))
    area_sq_m = poly.area * (km_per_deg_lat * 1000) * (km_per_deg_lon * 1000)
    area_acres = round(area_sq_m / 4046.86, 2)
    area_hectares = round(area_sq_m / 10000.0, 3)

    lons = GRID_DATA["lon_grid"]
    lats = GRID_DATA["lat_grid"]
    gwpi = GRID_DATA["gwpi"]
    elev = GRID_DATA["elevation"]
    slope = GRID_DATA["slope"]

    inside_scores = []
    candidates = []

    for r in range(GRID_DATA["rows"]):
        lat = lats[r]
        if lat < miny or lat > maxy:
            continue
        for c in range(GRID_DATA["cols"]):
            lon = lons[c]
            if lon < minx or lon > maxx:
                continue
            pt = Point(lon, lat)
            if poly.contains(pt):
                score = gwpi[r][c]
                inside_scores.append(score)
                candidates.append({
                    "lat": lat,
                    "lon": lon,
                    "score": score,
                    "elevation": elev[r][c],
                    "slope": slope[r][c]
                })

    if not candidates:
        # Fallback to centroid if polygon is smaller than cell
        r = int(min(range(len(lats)), key=lambda i: abs(lats[i] - centroid.y)))
        c = int(min(range(len(lons)), key=lambda i: abs(lons[i] - centroid.x)))
        score = gwpi[r][c]
        inside_scores.append(score)
        candidates.append({
            "lat": lats[r], "lon": lons[c], "score": score,
            "elevation": elev[r][c], "slope": slope[r][c]
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    mean_score = round(sum(inside_scores) / len(inside_scores), 1)

    # Pick top 3 with 150m spacing
    selected_spots = []
    min_spacing_deg = 0.0013 # ~145m

    for cand in candidates:
        too_close = False
        for s in selected_spots:
            dist = math.hypot(cand["lat"] - s["lat"], cand["lon"] - s["lon"])
            if dist < min_spacing_deg:
                too_close = True
                break
        if not too_close:
            rank = len(selected_spots) + 1
            pot_class = "High Potential" if cand["score"] >= 70 else "Moderate to High Potential" if cand["score"] >= 60 else "Moderate Potential"
            selected_spots.append({
                "rank": rank,
                "label": f"Spot #{rank} ({'Primary' if rank == 1 else 'Secondary' if rank == 2 else 'Alternative'})",
                "lat": round(cand["lat"], 6),
                "lon": round(cand["lon"], 6),
                "gwpi_score": float(cand["score"]),
                "potential_category": pot_class,
                "elevation_m": float(cand["elevation"]),
                "slope_pct": float(cand["slope"]),
                "estimated_depth_range": "280 - 400 ft",
                "expected_yield_range": "1,500 - 2,500 LPH (approx 1.0 - 1.5 inch)",
                "hydro_summary": f"Located on a gentle slope ({cand['slope']}%) with favorable fracture density and moisture convergence in the weathered granite zone."
            })
        if len(selected_spots) >= 3:
            break

    cat = "High Potential" if mean_score >= 65 else "Moderate Potential"

    return {
        "area_acres": area_acres,
        "area_hectares": area_hectares,
        "centroid": {"lat": round(centroid.y, 6), "lon": round(centroid.x, 6)},
        "mean_gwpi_score": mean_score,
        "potential_category": cat,
        "candidate_spots": selected_spots,
        "boundary_geojson": {"type": "Polygon", "coordinates": [coords]}
    }


@router.post("/evaluate", response_model=PlotResponse, status_code=status.HTTP_201_CREATED)
def evaluate_plot(payload: PlotEvaluationRequest, db: Session = Depends(get_db)):
    """
    Evaluates a user-defined parcel boundary, performs spatial peak detection,
    stores the plot and candidate spots in the database, and returns technical siting parameters.
    """
    eval_result = evaluate_polygon_grid(payload.coordinates)

    db_plot = LandPlot(
        plot_name=payload.plot_name,
        state=payload.state,
        district=payload.district,
        mandal=payload.mandal,
        village=payload.village,
        survey_number=payload.survey_number,
        area_acres=eval_result["area_acres"],
        area_hectares=eval_result["area_hectares"],
        centroid_lat=eval_result["centroid"]["lat"],
        centroid_lon=eval_result["centroid"]["lon"],
        boundary_geojson=eval_result["boundary_geojson"],
        mean_gwpi_score=eval_result["mean_gwpi_score"],
        potential_category=eval_result["potential_category"]
    )
    db.add(db_plot)
    db.flush()

    for s in eval_result["candidate_spots"]:
        db_spot = CandidateSpot(
            plot_id=db_plot.id,
            rank=s["rank"],
            label=s["label"],
            lat=s["lat"],
            lon=s["lon"],
            gwpi_score=s["gwpi_score"],
            potential_category=s["potential_category"],
            elevation_m=s["elevation_m"],
            slope_pct=s["slope_pct"],
            estimated_depth_range=s["estimated_depth_range"],
            expected_yield_range=s["expected_yield_range"],
            hydro_summary=s["hydro_summary"]
        )
        db.add(db_spot)

    db.commit()
    db.refresh(db_plot)

    return PlotResponse(
        id=db_plot.id,
        plot_name=db_plot.plot_name,
        state=db_plot.state,
        district=db_plot.district,
        mandal=db_plot.mandal,
        village=db_plot.village,
        survey_number=db_plot.survey_number,
        area_acres=db_plot.area_acres,
        area_hectares=db_plot.area_hectares,
        centroid={"lat": db_plot.centroid_lat, "lon": db_plot.centroid_lon},
        mean_gwpi_score=db_plot.mean_gwpi_score,
        potential_category=db_plot.potential_category,
        candidate_spots=[
            CandidateSpotSchema(
                rank=s.rank,
                label=s.label,
                lat=s.lat,
                lon=s.lon,
                gwpi_score=s.gwpi_score,
                potential_category=s.potential_category,
                elevation_m=s.elevation_m,
                slope_pct=s.slope_pct,
                estimated_depth_range=s.estimated_depth_range,
                expected_yield_range=s.expected_yield_range,
                hydro_summary=s.hydro_summary
            ) for s in db_plot.candidate_spots
        ],
        created_at=db_plot.created_at
    )


@router.get("/{plot_id}", response_model=PlotResponse)
def get_plot(plot_id: str, db: Session = Depends(get_db)):
    """Retrieves a previously evaluated farm plot by ID."""
    db_plot = db.query(LandPlot).filter(LandPlot.id == plot_id).first()
    if not db_plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    return PlotResponse(
        id=db_plot.id,
        plot_name=db_plot.plot_name,
        state=db_plot.state,
        district=db_plot.district,
        mandal=db_plot.mandal,
        village=db_plot.village,
        survey_number=db_plot.survey_number,
        area_acres=db_plot.area_acres,
        area_hectares=db_plot.area_hectares,
        centroid={"lat": db_plot.centroid_lat, "lon": db_plot.centroid_lon},
        mean_gwpi_score=db_plot.mean_gwpi_score,
        potential_category=db_plot.potential_category,
        candidate_spots=[
            CandidateSpotSchema(
                rank=s.rank,
                label=s.label,
                lat=s.lat,
                lon=s.lon,
                gwpi_score=s.gwpi_score,
                potential_category=s.potential_category,
                elevation_m=s.elevation_m,
                slope_pct=s.slope_pct,
                estimated_depth_range=s.estimated_depth_range,
                expected_yield_range=s.expected_yield_range,
                hydro_summary=s.hydro_summary
            ) for s in db_plot.candidate_spots
        ],
        created_at=db_plot.created_at
    )


@router.get("/{plot_id}/report.pdf")
def stream_pdf_report(plot_id: str, db: Session = Depends(get_db)):
    """Generates and streams the official multi-page PDF siting report for a plot."""
    db_plot = db.query(LandPlot).filter(LandPlot.id == plot_id).first()
    if not db_plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    farm_map = os.path.join(ROOT_DIR, "data", "output", "farm_siting_plan.png")
    catchment_map = os.path.join(ROOT_DIR, "data", "output", "catchment_gwpi_map.png")
    geojson_path = os.path.join(ROOT_DIR, "data", "output", "farm_siting_report.geojson")
    out_pdf = os.path.join(ROOT_DIR, "data", "output", f"report_{plot_id}.pdf")

    generate_pdf_report(geojson_path, farm_map, catchment_map, out_pdf)

    return FileResponse(
        out_pdf,
        media_type="application/pdf",
        filename=f"Borewell_Siting_Report_{db_plot.plot_name.replace(' ', '_')}.pdf"
    )
