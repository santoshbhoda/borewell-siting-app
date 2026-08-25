"""
End-to-End Orchestrator for Groundwater Potential Data ETL Pipeline & Siting Engine
Executes complete data pipeline from KML ingestion to AHP scoring and map generation.
"""
import os
import sys
import shutil
import json
import numpy as np

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
from pipeline.export.exporter import export_geojson_report, export_geotiff, generate_map_visualizations, export_client_grid


def run_pipeline(kml_path: str, output_dir: str = None, artifact_dir: str = None) -> dict:
    print("================================================================================")
    print("      BSMA GeoAI — Groundwater Potential ETL Pipeline & AHP Siting Engine       ")
    print("================================================================================")

    if output_dir is None:
        output_dir = os.path.join(ROOT_DIR, "data", "output")
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # STEP 1: Parse KML & Define Study Catchment
    # -------------------------------------------------------------------------
    print(f"\n[1/7] Ingesting Farm KML: {os.path.basename(kml_path)}...")
    farm_info = parse_kml(kml_path)
    print(f"      Farm: {farm_info['name']}")
    print(f"      Area: {farm_info['area']['acres']} Acres ({farm_info['area']['hectares']} ha)")
    print(f"      Centroid: ({farm_info['centroid']['lat']:.5f}°N, {farm_info['centroid']['lon']:.5f}°E)")
    
    catchment_bbox = get_study_catchment_bbox(farm_info["bounds"], buffer_km=6.0)
    print(f"      Study Catchment BBox (6km buffer): {catchment_bbox}")

    # -------------------------------------------------------------------------
    # STEP 2: Solve AHP Multi-Criteria Weights
    # -------------------------------------------------------------------------
    print("\n[2/7] Computing AHP Multi-Criteria Pairwise Matrix & Consistency Ratio...")
    ahp_solver = AHPMatrixSolver(AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX)
    ahp_weights = ahp_solver.solve()
    print(f"      Lambda Max: {ahp_weights['lambda_max']}, CI: {ahp_weights['consistency_index_ci']}")
    print(f"      Consistency Ratio (CR): {ahp_weights['consistency_ratio_cr']} -> {'PASSED (< 0.10)' if ahp_weights['is_consistent'] else 'FAILED'}")
    print("      Calibrated Criteria Weights:")
    for layer, w in ahp_weights["weights"].items():
        print(f"        • {layer:20s}: {w*100:5.2f}%")

    # -------------------------------------------------------------------------
    # STEP 3: DEM Acquisition & Spatial Grid Setup
    # -------------------------------------------------------------------------
    print("\n[3/7] Generating High-Resolution Catchment DEM Surface (30m resolution)...")
    dem_fetcher = DEMFetcher(catchment_bbox, grid_resolution_m=30.0)
    dem_data = dem_fetcher.get_dem()
    print(f"      Grid Dimensions: {dem_data['rows']} rows x {dem_data['cols']} cols ({dem_data['rows']*dem_data['cols']} grid cells)")
    print(f"      Elevation: {dem_data['min_elevation']:.1f}m to {dem_data['max_elevation']:.1f}m (Mean: {dem_data['mean_elevation']:.1f}m)")

    # -------------------------------------------------------------------------
    # STEP 4: Morphometric Derivatives Extraction
    # -------------------------------------------------------------------------
    print("\n[4/7] Extracting Morphometric & Hydro-Structural Features...")
    
    # A. Slope & Aspect
    slope_data = compute_slope_aspect(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    print(f"      • Slope: Mean={np.mean(slope_data['slope_pct']):.2f}%, Max={np.max(slope_data['slope_pct']):.2f}%")

    # B. Drainage Network & Density
    drainage_data = compute_drainage(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    print(f"      • Drainage: Max Flow Acc={np.max(drainage_data['flow_accumulation']):.0f} cells")

    # C. Multi-directional Lineament & Fracture Density
    lineament_data = compute_lineaments(dem_data["elevation"], dem_data["dx"], dem_data["dy"])
    print(f"      • Structural Lineaments: Multi-directional edge filters applied (NW-SE, NE-SW trends)")

    # D. Topographic Wetness Index (TWI)
    twi_data = compute_twi(drainage_data["flow_accumulation"], slope_data["slope_deg"], dem_data["dx"])
    print(f"      • TWI: Mean={twi_data['mean_twi']:.2f}, Max={twi_data['max_twi']:.2f}")

    # -------------------------------------------------------------------------
    # STEP 5: Thematic Hydrogeological Layers
    # -------------------------------------------------------------------------
    print("\n[5/7] Harmonizing Thematic Layers (Geology, LULC, Soil, Rainfall)...")
    thematic_data = generate_thematic_layers(dem_data, slope_data["slope_pct"], drainage_data)
    print("      • Geology/Lithology: Peninsular Gneissic Complex, saprolite weathered mantle & valley fill")
    print("      • LULC: Agricultural pediplains & tank cascade depressions")
    print("      • Soil: Red Chalka sandy loam & valley alluvium")
    print(f"      • Rainfall: Gridded catchment precipitation (~{np.mean(thematic_data['rainfall_mm']):.1f} mm/year)")

    # -------------------------------------------------------------------------
    # STEP 6: Execute AHP Weighted Linear Combination (GWPI)
    # -------------------------------------------------------------------------
    print("\n[6/7] Computing Groundwater Potential Index (GWPI)...")
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
    print(f"      • Regional GWPI: Min={gwpi_data['min_score']:.1f}, Max={gwpi_data['max_score']:.1f}, Mean={gwpi_data['mean_score']:.1f}")

    # -------------------------------------------------------------------------
    # STEP 7: Farm Siting Analysis & Candidate Spots
    # -------------------------------------------------------------------------
    print("\n[7/7] Siting Optimization for Karun Farm 2 & Generating Reports...")
    morph_data = {
        "slope_pct": slope_data["slope_pct"],
        "lineament_density": lineament_data["lineament_density"],
        "twi": twi_data["twi"]
    }

    farm_analysis = analyze_farm_plot(farm_info, dem_data, gwpi_data, morph_data, thematic_data)
    
    print("\n" + "="*80)
    print(f"  FARM SITING SUMMARY: {farm_analysis['farm_name']} ({farm_analysis['farm_area_acres']} Acres)")
    print("="*80)
    print(f"  Overall Rating: {farm_analysis['score_statistics']['mean']}/100 ({farm_analysis['score_statistics']['category']})")
    print("\n  TOP CANDIDATE DRILLING LOCATIONS:")
    for pt in farm_analysis["candidate_points"]:
        print(f"  ------------------------------------------------------------------")
        print(f"  {pt['label']} | Coordinates: {pt['lat']}°N, {pt['lon']}°E")
        print(f"    • GWPI Score         : {pt['gwpi_score']} / 100 ({pt['potential_category']})")
        print(f"    • Elevation / Slope  : {pt['elevation_m']} m | {pt['slope_pct']}% slope")
        print(f"    • Estimated Depth    : {pt['estimated_depth_range']}")
        print(f"    • Expected Yield     : {pt['expected_yield_range']}")
        print(f"    • Geological Rationale: {pt['hydro_summary']}")

    # -------------------------------------------------------------------------
    # EXPORTS & VISUALIZATIONS
    # -------------------------------------------------------------------------
    geotiff_path = os.path.join(output_dir, "gwpi_catchment_30m.tif")
    geojson_path = os.path.join(output_dir, "farm_siting_report.geojson")
    client_grid_path = os.path.join(output_dir, "gwpi_grid.json")
    web_data_dir = os.path.join(ROOT_DIR, "web", "data")
    os.makedirs(web_data_dir, exist_ok=True)
    
    export_geotiff(gwpi_data["gwpi_100"], catchment_bbox, geotiff_path)
    export_geojson_report(farm_analysis, ahp_weights, geojson_path, farm_info)
    export_client_grid(dem_data, gwpi_data, morph_data, client_grid_path)
    export_client_grid(dem_data, gwpi_data, morph_data, os.path.join(web_data_dir, "gwpi_grid.json"))
    shutil.copy(geojson_path, os.path.join(web_data_dir, "farm_siting_report.geojson"))
    
    map_paths = generate_map_visualizations(dem_data, gwpi_data, farm_info, farm_analysis, output_dir)
    shutil.copy(map_paths['regional_map'], os.path.join(web_data_dir, "catchment_gwpi_map.png"))
    shutil.copy(map_paths['farm_map'], os.path.join(web_data_dir, "farm_siting_plan.png"))

    print("\n  Exported Files:")
    print(f"    • GeoTIFF Raster : {geotiff_path}")
    print(f"    • GeoJSON Report : {geojson_path}")
    print(f"    • Client Grid    : {client_grid_path}")
    print(f"    • Regional Map   : {map_paths['regional_map']}")
    print(f"    • Farm Siting Plan: {map_paths['farm_map']}")

    # Copy maps to artifact directory if provided
    if artifact_dir and os.path.exists(artifact_dir):
        shutil.copy(map_paths['regional_map'], os.path.join(artifact_dir, "catchment_gwpi_map.png"))
        shutil.copy(map_paths['farm_map'], os.path.join(artifact_dir, "farm_siting_plan.png"))
        shutil.copy(geojson_path, os.path.join(artifact_dir, "farm_siting_report.geojson"))

    print("\n Pipeline execution completed successfully!")
    return {
        "farm_analysis": farm_analysis,
        "ahp_weights": ahp_weights,
        "map_paths": map_paths,
        "geotiff_path": geotiff_path,
        "geojson_path": geojson_path
    }


if __name__ == "__main__":
    kml_file = os.path.join(ROOT_DIR, "Farm.kml")
    art_dir = r"C:\Users\Santosh Kumar Bhoda\.gemini\antigravity\brain\3ab857a8-e833-4b4a-a1ff-059e1bb29110"
    run_pipeline(kml_file, artifact_dir=art_dir)
