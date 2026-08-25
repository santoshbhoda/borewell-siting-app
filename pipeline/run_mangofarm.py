"""
Dedicated Pipeline Runner & Report Generator for MangoFarm.kml (Karun Farmland 1)
Executes AHP hydrogeological analysis, peak extraction with >=150m spacing,
cartographic visual generation, and ReportLab 2-page publication PDF generation.
"""
import os
import sys
import shutil
import json

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline.kml_parser import parse_kml, get_study_catchment_bbox
from pipeline.config import AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX
from pipeline.ahp.matrix import AHPMatrixSolver
from pipeline.ingestion.dem_fetcher import DEMFetcher
from pipeline.morphometrics.slope_aspect import compute_slope_aspect
from pipeline.morphometrics.drainage import compute_drainage
from pipeline.morphometrics.lineaments import compute_lineaments
from pipeline.morphometrics.twi import compute_twi
from pipeline.thematic.thematic_layers import generate_thematic_layers
from pipeline.ahp.engine import AHPEngine
from pipeline.analysis.farm_analyzer import analyze_farm_plot
from pipeline.export.exporter import export_geojson_report, generate_map_visualizations
from pipeline.export.pdf_report_generator import generate_pdf_report
from backend.database import SessionLocal
from backend.models import LandPlot, CandidateSpot


def run_mangofarm_pipeline():
    kml_path = os.path.join(ROOT_DIR, "MangoFarm.kml")
    output_dir = os.path.join(ROOT_DIR, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    print("================================================================================")
    print("      BSMA GeoAI — Groundwater Potential Siting: Mango Farm (Karun Farmland 1)   ")
    print("================================================================================")

    # 1. Parse KML
    farm_info = parse_kml(kml_path)
    farm_info["name"] = "Mango Farm (Karun Farmland 1)"
    print(f"Parcel Name: {farm_info['name']}")
    print(f"Area: {farm_info['area']['acres']} Acres ({farm_info['area']['hectares']} ha)")
    print(f"Centroid: {farm_info['centroid']['lat']:.5f}°N, {farm_info['centroid']['lon']:.5f}°E")

    catchment_bbox = get_study_catchment_bbox(farm_info["bounds"], buffer_km=6.0)

    # 2. AHP Weights
    ahp_solver = AHPMatrixSolver(AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX)
    ahp_weights = ahp_solver.solve()

    # 3. DEM & Derivatives
    dem_fetcher = DEMFetcher(catchment_bbox, grid_resolution_m=30.0)
    dem_data = dem_fetcher.get_dem()
    slope_data = compute_slope_aspect(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    drainage_data = compute_drainage(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    lineament_data = compute_lineaments(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    twi_data = compute_twi(drainage_data["flow_accumulation"], slope_data["slope_deg"], dem_data["dx"])
    thematic_data = generate_thematic_layers(dem_data, slope_data["slope_pct"], drainage_data)

    # 4. GWPI Computation
    all_layers = {
        "geology_rank": thematic_data["geology_rank"],
        "lineament_density": lineament_data["lineament_density"],
        "slope_pct": slope_data["slope_pct"],
        "drainage_density": drainage_data["drainage_density"],
        "twi": twi_data["twi"],
        "lulc_rank": thematic_data["lulc_rank"],
        "soil_rank": thematic_data["soil_rank"],
        "rainfall_rank": thematic_data["rainfall_rank"]
    }
    ahp_engine = AHPEngine(ahp_weights["weights"])
    gwpi_data = ahp_engine.compute_gwpi(all_layers)

    # 5. Farm Siting & Peak Extraction
    morph_data = {
        "slope_pct": slope_data["slope_pct"],
        "lineament_density": lineament_data["lineament_density"],
        "twi": twi_data["twi"]
    }
    farm_analysis = analyze_farm_plot(farm_info, dem_data, gwpi_data, morph_data, thematic_data)

    print("\n" + "="*80)
    print(f"  MANGO FARM SITING SUMMARY: {farm_analysis['farm_name']}")
    print(f"  Area: {farm_analysis['farm_area_acres']} Acres | Centroid: {farm_analysis['centroid']['lat']:.5f}°N, {farm_analysis['centroid']['lon']:.5f}°E")
    print(f"  Overall Score: {farm_analysis['score_statistics']['mean']}/100 ({farm_analysis['score_statistics']['category']})")
    print("="*80)
    for pt in farm_analysis["candidate_points"]:
        print(f"  {pt['label']} | Coordinates: {pt['lat']:.5f}°N, {pt['lon']:.5f}°E")
        print(f"    • Score: {pt['gwpi_score']}/100 ({pt['potential_category']})")
        print(f"    • Est. Depth: {pt['estimated_depth_range']} | Yield: {pt['expected_yield_range']}")
        print(f"    • Elevation: {pt['elevation_m']}m MSL | Slope: {pt['slope_pct']}%")
        print(f"    • Rationale: {pt['hydro_summary']}\n")

    # 6. Export GeoJSON & Maps
    geojson_path = os.path.join(output_dir, "mangofarm_siting_report.geojson")
    export_geojson_report(farm_analysis, ahp_weights, geojson_path, farm_info)

    map_paths = generate_map_visualizations(dem_data, gwpi_data, farm_info, farm_analysis, output_dir)
    mangofarm_plan = os.path.join(output_dir, "mangofarm_siting_plan.png")
    shutil.copy(map_paths['farm_map'], mangofarm_plan)

    # 7. Generate Publication-Grade 2-Page PDF Report
    pdf_out = os.path.join(ROOT_DIR, "Borewell_Siting_Full_Report_MangoFarm.pdf")
    generate_pdf_report(geojson_path, mangofarm_plan, map_paths['regional_map'], pdf_out)

    # 8. Seed/Save to Database
    db = SessionLocal()
    try:
        plot_record = LandPlot(
            plot_name=farm_analysis["farm_name"],
            state="Telangana",
            district="Yadadri-Bhuvanagiri",
            mandal="Bhuvanagiri",
            village="Rayagiri",
            survey_number="140/B",
            area_acres=farm_analysis["farm_area_acres"],
            area_hectares=farm_analysis["farm_area_hectares"],
            centroid_lat=farm_analysis["centroid"]["lat"],
            centroid_lon=farm_analysis["centroid"]["lon"],
            boundary_geojson=farm_info["polygon"].__geo_interface__,
            mean_gwpi_score=farm_analysis["score_statistics"]["mean"],
            potential_category=farm_analysis["score_statistics"]["category"]
        )
        db.add(plot_record)
        db.flush()

        for pt in farm_analysis["candidate_points"]:
            spot = CandidateSpot(
                plot_id=plot_record.id,
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
        db.commit()
        print(f"Mango Farm successfully persisted in PostGIS database with ID: {plot_record.id}")
    finally:
        db.close()

    # Also copy to artifact directory if available
    art_dir = r"C:\Users\Santosh Kumar Bhoda\.gemini\antigravity\brain\3ab857a8-e833-4b4a-a1ff-059e1bb29110"
    if os.path.exists(art_dir):
        shutil.copy(mangofarm_plan, os.path.join(art_dir, "mangofarm_siting_plan.png"))
        shutil.copy(geojson_path, os.path.join(art_dir, "mangofarm_siting_report.geojson"))

    print(f"\n[DONE] Mango Farm Full PDF Report generated at: {pdf_out}")
    return farm_analysis


if __name__ == "__main__":
    run_mangofarm_pipeline()
