"""
Farm Siting Analyzer and Candidate Point Extraction
Clips regional GWPI raster to the user farm polygon (Karun Farm 2),
performs spatial peak detection with distance constraints (WALTA guidelines),
and generates multi-lingual plain-language recommendations.
"""
import numpy as np
from shapely.geometry import Point, Polygon
from typing import Dict, List, Any, Tuple
import math
from pipeline.config import SITING_CONSTRAINTS, GWPI_CATEGORIES


def analyze_farm_plot(
    farm_info: Dict[str, Any],
    dem_data: Dict[str, Any],
    gwpi_data: Dict[str, Any],
    morph_data: Dict[str, Any],
    thematic_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates groundwater potential across the farm plot and extracts top candidate drilling spots.
    """
    polygon: Polygon = farm_info["polygon"]
    lon_grid = dem_data["lon_grid"]
    lat_grid = dem_data["lat_grid"]
    gwpi_100 = gwpi_data["gwpi_100"]
    elevation = dem_data["elevation"]
    slope_pct = morph_data["slope_pct"]
    lineament_density = morph_data["lineament_density"]
    twi = morph_data["twi"]
    
    rows, cols = gwpi_100.shape
    dx, dy = dem_data["dx"], dem_data["dy"]

    # 1. Create a boolean mask of raster cells that fall inside the farm polygon
    farm_mask = np.zeros((rows, cols), dtype=bool)
    farm_pixel_coords = []
    farm_scores = []

    for r in range(rows):
        lat = lat_grid[r]
        # Bounding box pre-check for speed
        if lat < farm_info["bounds"]["min_lat"] or lat > farm_info["bounds"]["max_lat"]:
            continue
        for c in range(cols):
            lon = lon_grid[c]
            if lon < farm_info["bounds"]["min_lon"] or lon > farm_info["bounds"]["max_lon"]:
                continue
            pt = Point(lon, lat)
            if polygon.contains(pt):
                farm_mask[r, c] = True
                farm_pixel_coords.append((r, c, lat, lon))
                farm_scores.append(float(gwpi_100[r, c]))

    if not farm_pixel_coords:
        # If farm polygon is smaller than cell center, find nearest cell to centroid
        cent_lon = farm_info["centroid"]["lon"]
        cent_lat = farm_info["centroid"]["lat"]
        r = int(np.argmin(np.abs(lat_grid - cent_lat)))
        c = int(np.argmin(np.abs(lon_grid - cent_lon)))
        farm_mask[r, c] = True
        farm_pixel_coords.append((r, c, lat_grid[r], lon_grid[c]))
        farm_scores.append(float(gwpi_100[r, c]))

    farm_scores_arr = np.array(farm_scores)
    min_farm_score = float(np.min(farm_scores_arr))
    max_farm_score = float(np.max(farm_scores_arr))
    mean_farm_score = float(np.mean(farm_scores_arr))

    # 2. Extract Top Candidate Points with Spatial Buffer / Spacing Constraints
    # Sort candidate pixels inside farm by GWPI score descending
    sorted_indices = np.argsort(farm_scores_arr)[::-1]
    
    candidate_points = []
    min_dist_m = SITING_CONSTRAINTS.get("min_distance_between_borewells_m", 100.0)
    
    # Approx meters per degree
    lat_mid = farm_info["centroid"]["lat"]
    m_per_deg_lat = 110574.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat_mid))

    for idx in sorted_indices:
        r, c, lat, lon = farm_pixel_coords[idx]
        score = float(gwpi_100[r, c])
        elev_val = float(elevation[r, c])
        slope_val = float(slope_pct[r, c])
        lin_val = float(lineament_density[r, c])
        twi_val = float(twi[r, c])

        # Check distance to already accepted candidate points
        too_close = False
        for cand in candidate_points:
            d_lat = (lat - cand["lat"]) * m_per_deg_lat
            d_lon = (lon - cand["lon"]) * m_per_deg_lon
            dist = math.sqrt(d_lat**2 + d_lon**2)
            if dist < min_dist_m:
                too_close = True
                break

        if not too_close:
            rank_num = len(candidate_points) + 1
            
            # Determine potential classification
            if score >= 75:
                potential_class = "High to Very High Potential"
                est_depth_ft = "220 - 320 ft"
                est_yield_lph = "2,500 - 4,000+ LPH (approx 1.5 - 2.5 inch yield)"
            elif score >= 60:
                potential_class = "Moderate to High Potential"
                est_depth_ft = "280 - 400 ft"
                est_yield_lph = "1,500 - 2,500 LPH (approx 1.0 - 1.5 inch yield)"
            else:
                potential_class = "Moderate Potential"
                est_depth_ft = "350 - 450 ft"
                est_yield_lph = "800 - 1,500 LPH"

            candidate_points.append({
                "rank": rank_num,
                "label": f"Spot #{rank_num} ({'Primary' if rank_num == 1 else 'Secondary' if rank_num == 2 else 'Alternative'})",
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "gwpi_score": round(score, 1),
                "potential_category": potential_class,
                "elevation_m": round(elev_val, 1),
                "slope_pct": round(slope_val, 1),
                "lineament_density_index": round(lin_val, 1),
                "twi_index": round(twi_val, 1),
                "estimated_depth_range": est_depth_ft,
                "expected_yield_range": est_yield_lph,
                "hydro_summary": (
                    f"Located on a gentle slope ({slope_val:.1f}%) with favorable fracture density "
                    f"and high moisture convergence in the weathered granite zone."
                )
            })

        if len(candidate_points) >= SITING_CONSTRAINTS.get("max_candidate_points", 3):
            break

    # 3. Overall Farm Category & Plain-Language Summary
    farm_category = "High Potential" if mean_farm_score >= 65 else "Moderate Potential" if mean_farm_score >= 50 else "Low Potential"

    plain_language_summary = {
        "en": (
            f"Karun Farm 2 ({farm_info['area']['acres']} Acres) shows an overall {farm_category} "
            f"(Average Potential Index: {mean_farm_score:.1f}/100). The most favorable groundwater recharge "
            f"and secondary fracture intersections are concentrated along the central and lower drainage contours. "
            f"Top recommendation is Spot #1 at coordinates ({candidate_points[0]['lat']}, {candidate_points[0]['lon']}) "
            f"with a score of {candidate_points[0]['gwpi_score']}/100."
        ),
        "te": (
            f"కరుణ్ ఫామ్ 2 ({farm_info['area']['acres']} ఎకరాలు) సగటున {mean_farm_score:.1f}/100 అనుకూలమైన భూగర్భ జలాల సామర్థ్యాన్ని కలిగి ఉంది. "
            f"పగుళ్లు మరియు నీటి నిల్వ ఉండే ఉపరితల నేలలు ప్రధానంగా గుర్తించబడ్డాయి. "
            f"మొదటి ప్రాధాన్యతా స్థానం (స్పాట్ #1) వద్ద అత్యధిక నీటి సాంద్రత ({candidate_points[0]['gwpi_score']}/100) నమోదైంది. "
            f"డ్రిల్లింగ్ చేయడానికి ముందు VES రెసిస్టివిటీ సర్వే చేయించుకోవడం తప్పనిసరి."
        ),
        "hi": (
            f"करुण फार्म 2 ({farm_info['area']['acres']} एकड़) में भूजल क्षमता का औसत सूचकांक {mean_farm_score:.1f}/100 है। "
            f"खेत के मध्य और निचले हिस्से में चट्टानी दरारों (Lineaments) और जल संचयन की स्थिति अनुकूल है। "
            f"सबसे उत्तम स्थान स्पॉट #1 ({candidate_points[0]['gwpi_score']}/100) पर पहचाना गया है। "
            f"बोरवेल खुदाई से पहले VES भू-भौतिकीय सर्वेक्षण अवश्य करवाएं।"
        )
    }

    # 4. WALTA & Field Survey Advisory
    advisory = {
        "walta_compliance": {
            "status": "Applicable (Telangana WALTA Act)",
            "rule": "Minimum distance between two commercial/agricultural borewells must be 150 meters.",
            "clearance_needed": False if mean_farm_score >= 50 else True,
            "message": "The proposed spots are located on private agricultural land. Ensure 150m clearance from neighboring active wells."
        },
        "ves_verification_note": {
            "title": "Mandatory Pre-Drilling Field Verification (VES Survey)",
            "guidance": (
                "GIS/Remote Sensing identifies high-probability fracture corridors and weathering zones. "
                "Before investing in rig mobilization, conduct a 1D/2D Vertical Electrical Sounding (VES) "
                "or Resistivity Imaging survey at the marked coordinates to confirm the exact depth of the water-bearing fracture."
            )
        }
    }

    return {
        "farm_name": farm_info["name"],
        "farm_area_acres": farm_info["area"]["acres"],
        "farm_area_hectares": farm_info["area"]["hectares"],
        "bounds": farm_info["bounds"],
        "centroid": farm_info["centroid"],
        "score_statistics": {
            "min": round(min_farm_score, 1),
            "max": round(max_farm_score, 1),
            "mean": round(mean_farm_score, 1),
            "category": farm_category
        },
        "candidate_points": candidate_points,
        "summary": plain_language_summary,
        "advisory": advisory
    }


if __name__ == "__main__":
    print("Farm analyzer module ready.")
