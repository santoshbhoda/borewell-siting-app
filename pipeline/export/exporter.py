"""
Export and Map Visualization Module
Generates GeoTIFF, GeoJSON, analytical report JSON, and publication-quality map visualizations.
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, Any
import tifffile
from shapely.geometry import mapping


def export_geojson_report(farm_analysis: Dict[str, Any], ahp_weights: Dict[str, Any], output_path: str, farm_info: Dict[str, Any] = None) -> None:
    """
    Exports comprehensive Farm Siting Report and GeoJSON features.
    """
    features = []

    # 1. Farm Boundary Polygon Feature
    if farm_info and "coordinates" in farm_info:
        polygon_coords = [[list(pt) for pt in farm_info["coordinates"]]]
    else:
        b = farm_analysis["bounds"]
        polygon_coords = [[
            [b["min_lon"], b["min_lat"]],
            [b["max_lon"], b["min_lat"]],
            [b["max_lon"], b["max_lat"]],
            [b["min_lon"], b["max_lat"]],
            [b["min_lon"], b["min_lat"]]
        ]]

    features.append({
        "type": "Feature",
        "properties": {
            "feature_type": "Farm Boundary",
            "name": farm_analysis["farm_name"],
            "area_acres": farm_analysis["farm_area_acres"],
            "area_hectares": farm_analysis["farm_area_hectares"],
            "mean_gwpi_score": farm_analysis["score_statistics"]["mean"],
            "category": farm_analysis["score_statistics"]["category"]
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": polygon_coords
        }
    })

    # 2. Candidate Siting Point Features
    for pt in farm_analysis["candidate_points"]:
        features.append({
            "type": "Feature",
            "properties": {
                "feature_type": "Borewell Candidate Spot",
                "rank": pt["rank"],
                "label": pt["label"],
                "gwpi_score": pt["gwpi_score"],
                "potential_category": pt["potential_category"],
                "elevation_m": pt["elevation_m"],
                "slope_pct": pt["slope_pct"],
                "estimated_depth_range": pt["estimated_depth_range"],
                "expected_yield_range": pt["expected_yield_range"],
                "hydro_summary": pt["hydro_summary"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [pt["lon"], pt["lat"]]
            }
        })

    report = {
        "type": "FeatureCollection",
        "metadata": {
            "application": "BSMA GeoAI Borewell & Groundwater Siting Engine",
            "pilot_region": "Yadadri-Bhuvanagiri / Jangaon Belt, Musi Basin, Telangana",
            "hydrogeology": "Hard-Rock Peninsular Gneissic Terrain",
            "model": "Saaty AHP Multi-Criteria Decision Analysis",
            "ahp_weights": ahp_weights["weights"],
            "ahp_consistency_ratio": ahp_weights["consistency_ratio_cr"]
        },
        "farm_analysis": farm_analysis,
        "features": features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def export_geotiff(gwpi_raster: np.ndarray, bbox: Dict[str, float], output_path: str) -> None:
    """
    Exports GWPI raster to GeoTIFF format.
    """
    tifffile.imwrite(
        output_path,
        gwpi_raster.astype(np.float32),
        photometric='minisblack',
        description=f"GWPI 0-100 Groundwater Potential Index; BBox: {bbox}"
    )


def generate_map_visualizations(
    dem_data: Dict[str, Any],
    gwpi_data: Dict[str, Any],
    farm_info: Dict[str, Any],
    farm_analysis: Dict[str, Any],
    output_dir: str
) -> Dict[str, str]:
    """
    Generates high-resolution analytical map visualizations:
    1. Catchment Groundwater Potential Map (Regional View)
    2. High-Zoom Farm Parcel Siting Map with Top 3 Candidate Points
    """
    os.makedirs(output_dir, exist_ok=True)
    
    lon_grid = dem_data["lon_grid"]
    lat_grid = dem_data["lat_grid"]
    gwpi_100 = gwpi_data["gwpi_100"]
    elevation = dem_data["elevation"]
    extent = [lon_grid[0], lon_grid[-1], lat_grid[-1], lat_grid[0]]

    # Custom Groundwater Potential Colormap (Red -> Yellow -> Green -> Dark Green)
    colors = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837']
    cmap_gwpi = LinearSegmentedColormap.from_list('gwpi_cmap', colors, N=256)

    # -------------------------------------------------------------
    # MAP 1: Regional Catchment GWPI Overview
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 10), dpi=200)
    
    # Render GWPI Heatmap
    im = ax.imshow(gwpi_100, extent=extent, cmap=cmap_gwpi, vmin=0, vmax=100, origin='upper')
    
    # Overlay Farm Polygon
    poly_coords = np.array(farm_info["coordinates"])
    ax.plot(poly_coords[:, 0], poly_coords[:, 1], color='#e41a1c', linewidth=2.5, label='Karun Farm 2 Boundary')
    ax.fill(poly_coords[:, 0], poly_coords[:, 1], color='red', alpha=0.25)

    # Overlay Candidate Points
    for pt in farm_analysis["candidate_points"]:
        ax.scatter(pt["lon"], pt["lat"], s=160, c='yellow', edgecolors='black', linewidth=2, zorder=5)
        ax.annotate(
            f"Spot #{pt['rank']} ({pt['gwpi_score']})",
            (pt["lon"], pt["lat"]),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            color='black',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, edgecolor='black')
        )

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label('Groundwater Potential Index (GWPI: 0 - 100)', fontsize=11, fontweight='bold')

    ax.set_title(
        'Groundwater Potential & Fracture Siting Model (AHP Multi-Criteria)\n'
        'Catchment Area: Yadadri-Bhuvanagiri / Musi Sub-Basin, Telangana',
        fontsize=13,
        fontweight='bold',
        pad=15
    )
    ax.set_xlabel('Longitude (°E)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=10, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='upper right', framealpha=0.9)

    regional_map_path = os.path.join(output_dir, "catchment_gwpi_map.png")
    plt.tight_layout()
    plt.savefig(regional_map_path)
    plt.close()

    # -------------------------------------------------------------
    # MAP 2: High-Resolution Farm Plot Siting Plan
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=200, gridspec_kw={'width_ratios': [1.2, 1]})

    # Focus on Farm Extent with a 200m buffer
    f_bounds = farm_info["bounds"]
    lon_buf = (f_bounds["max_lon"] - f_bounds["min_lon"]) * 0.4
    lat_buf = (f_bounds["max_lat"] - f_bounds["min_lat"]) * 0.4
    
    sub_extent = [
        f_bounds["min_lon"] - lon_buf,
        f_bounds["max_lon"] + lon_buf,
        f_bounds["min_lat"] - lat_buf,
        f_bounds["max_lat"] + lat_buf
    ]

    im_farm = ax1.imshow(gwpi_100, extent=extent, cmap=cmap_gwpi, vmin=0, vmax=100, origin='upper')
    ax1.set_xlim(sub_extent[0], sub_extent[1])
    ax1.set_ylim(sub_extent[2], sub_extent[3])

    # Plot Farm Polygon
    ax1.plot(poly_coords[:, 0], poly_coords[:, 1], color='#990000', linewidth=3.5, label='Farm Boundary (14.8 Acres)')
    ax1.fill(poly_coords[:, 0], poly_coords[:, 1], color='#31a354', alpha=0.2)

    # Plot Candidate Points
    colors_rank = {1: '#00cc44', 2: '#ffbb00', 3: '#3399ff'}
    for pt in farm_analysis["candidate_points"]:
        col = colors_rank.get(pt["rank"], 'yellow')
        ax1.scatter(pt["lon"], pt["lat"], s=240, c=col, edgecolors='black', linewidth=2.5, zorder=6)
        ax1.annotate(
            f"Spot #{pt['rank']}\nGWPI: {pt['gwpi_score']}",
            (pt["lon"], pt["lat"]),
            xytext=(12, -15 if pt['rank']==2 else 12),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            color='black',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.92, edgecolor='black', lw=1.2)
        )

    ax1.set_title(f"{farm_info['name']} — Borewell Siting Recommendation", fontsize=12, fontweight='bold')
    ax1.set_xlabel('Longitude (°E)', fontsize=10)
    ax1.set_ylabel('Latitude (°N)', fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left')

    # Information Table / Card in Panel 2
    ax2.axis('off')
    
    table_text = [
        ["Property", "Details"],
        ["Farm Name", farm_info['name']],
        ["Total Land Area", f"{farm_info['area']['acres']} Acres ({farm_info['area']['hectares']} ha)"],
        ["Location / Basin", "Yadadri-Bhuvanagiri / Musi Basin (Telangana)"],
        ["Terrain / Lithology", "Weathered & Fractured Peninsular Gneiss"],
        ["Mean Potential Score", f"{farm_analysis['score_statistics']['mean']} / 100 ({farm_analysis['score_statistics']['category']})"],
        ["Top Recommended Spot", f"Spot #1 (Score: {farm_analysis['candidate_points'][0]['gwpi_score']})"],
        ["Spot #1 Coordinates", f"{farm_analysis['candidate_points'][0]['lat']}°N, {farm_analysis['candidate_points'][0]['lon']}°E"],
        ["Estimated Depth", farm_analysis['candidate_points'][0]['estimated_depth_range']],
        ["Expected Yield", farm_analysis['candidate_points'][0]['expected_yield_range']],
        ["WALTA Spacing Rule", "150m clearance from existing active wells"],
        ["Field Verification", "VES Resistivity Survey Recommended prior to drilling"]
    ]

    tab = ax2.table(
        cellText=table_text,
        colLabels=None,
        loc='center',
        cellLoc='left',
        colWidths=[0.38, 0.62]
    )
    tab.auto_set_font_size(False)
    tab.set_fontsize(10)
    tab.scale(1.1, 1.8)

    # Style Header & Cells
    for (row, col), cell in tab.get_celld().items():
        if row == 0:
            cell.set_text_props(fontweight='bold', color='white')
            cell.set_facecolor('#1a5276')
        elif row in [6, 7]:
            cell.set_facecolor('#e8f8f5')
            cell.set_text_props(fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#f8f9f9')
        cell.set_edgecolor('#bdc3c7')

    ax2.set_title("Hydrogeological Siting Summary", fontsize=12, fontweight='bold', pad=10)

    farm_map_path = os.path.join(output_dir, "farm_siting_plan.png")
    plt.tight_layout()
    plt.savefig(farm_map_path)
    plt.close()

    return {
        "regional_map": regional_map_path,
        "farm_map": farm_map_path
    }


def export_client_grid(
    dem_data: Dict[str, Any],
    gwpi_data: Dict[str, Any],
    morph_data: Dict[str, Any],
    output_path: str,
    stride: int = 2
) -> None:
    """
    Exports a lightweight quantized grid JSON for instantaneous in-browser spatial querying
    and peak candidate point extraction on custom user-drawn polygons.
    """
    # Downsample slightly by stride (e.g. stride 2 = 60m cell, very fast ~200KB JSON payload)
    lon_grid = dem_data["lon_grid"][::stride].tolist()
    lat_grid = dem_data["lat_grid"][::stride].tolist()
    
    gwpi_sub = gwpi_data["gwpi_100"][::stride, ::stride]
    elev_sub = dem_data["elevation"][::stride, ::stride]
    slope_sub = morph_data["slope_pct"][::stride, ::stride]
    lineam_sub = morph_data["lineament_density"][::stride, ::stride]

    payload = {
        "bbox": dem_data["bbox"],
        "rows": len(lat_grid),
        "cols": len(lon_grid),
        "dx": dem_data["dx"] * stride,
        "dy": dem_data["dy"] * stride,
        "lon_grid": [round(x, 6) for x in lon_grid],
        "lat_grid": [round(y, 6) for y in lat_grid],
        "gwpi": [[int(round(v)) for v in row] for row in gwpi_sub],
        "elevation": [[int(round(v)) for v in row] for row in elev_sub],
        "slope": [[round(float(v), 1) for v in row] for row in slope_sub],
        "lineament": [[round(float(v), 1) for v in row] for row in lineam_sub]
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


if __name__ == "__main__":
    print("Exporter module ready.")

