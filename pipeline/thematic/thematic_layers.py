"""
Thematic Layers Generation and Hydrogeological Calibration
Constructs Geology, Land Use / Land Cover (LULC), Soil, and Rainfall layers
calibrated to the Yadadri-Bhuvanagiri / Musi Basin hydrogeology.
"""
import numpy as np
from typing import Dict, Any


def generate_thematic_layers(dem_data: Dict[str, Any], slope_pct: np.ndarray, drainage: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Generates hydrogeological thematic layers aligned with the DEM spatial grid.
    """
    rows, cols = dem_data["rows"], dem_data["cols"]
    elevation = dem_data["elevation"]
    flow_acc = drainage["flow_accumulation"]
    streams = drainage["streams"]

    # 1. Lithology / Geology layer
    # Valley bottoms with high flow accumulation = Valley fill / Alluvial deposits (Rank 5)
    # Pediplain with moderate slope = Weathered Granite / Saprolite (Rank 4)
    # Undulating zones = Moderately Fractured Gneiss (Rank 3)
    # High elevation peaks = Massive Granite Dome (Rank 2)
    # Linear ridge zones = Quartz Reef / Dolerite Dyke (Rank 1)
    geology_rank = np.full((rows, cols), 3.0, dtype=np.float32) # Default Fractured Gneiss
    
    # Weathered granite pediplains (gentle slope < 5% and moderate elevation)
    pediplain_mask = (slope_pct < 6.0) & (elevation < 380.0)
    geology_rank[pediplain_mask] = 4.0
    
    # Valley fill alluvium along major stream corridors
    valley_fill_mask = (flow_acc > 120.0) & (slope_pct < 3.0)
    geology_rank[valley_fill_mask] = 5.0
    
    # Massive granite hilltops (> 420m elevation and slope > 15%)
    massive_granite_mask = (elevation > 420.0) | (slope_pct > 18.0)
    geology_rank[massive_granite_mask] = 2.0

    # 2. Land Use / Land Cover (LULC) layer
    # Water tanks (Cheruvus) in depressions (Rank 5)
    # Agricultural cropland across pediplains (Rank 4)
    # Fallow / Shrubland on higher slopes (Rank 2)
    # Rocky barren on steep hillocks (Rank 1)
    lulc_rank = np.full((rows, cols), 4.0, dtype=np.float32) # Default Cropland
    
    # Village tanks / Cheruvu water retention zones in depressions
    tank_mask = (flow_acc > 500.0) & (slope_pct < 1.5)
    lulc_rank[tank_mask] = 5.0
    
    # Fallow / Shrubland
    shrub_mask = (slope_pct >= 6.0) & (slope_pct < 15.0)
    lulc_rank[shrub_mask] = 2.0
    
    # Barren / Rocky outcrops
    rocky_mask = slope_pct >= 15.0
    lulc_rank[rocky_mask] = 1.0

    # 3. Soil Texture / Infiltration Layer
    # Sandy Loam (Red Chalka) across central agricultural fields (Rank 4)
    # Deep Valley Loam near streams (Rank 5)
    # Gravelly Sandy Loam on upper pediplains (Rank 3)
    # Rocky Lithosol on crests (Rank 1)
    soil_rank = np.full((rows, cols), 4.0, dtype=np.float32) # Default Sandy Loam (Chalka)
    
    valley_soil_mask = (flow_acc > 100.0) & (slope_pct < 2.5)
    soil_rank[valley_soil_mask] = 5.0
    
    gravelly_mask = (slope_pct >= 5.0) & (slope_pct < 12.0)
    soil_rank[gravelly_mask] = 3.0
    
    lithosol_mask = slope_pct >= 12.0
    soil_rank[lithosol_mask] = 1.0

    # 4. Rainfall / Recharge Layer
    # Regional orographic/monsoonal gradient (~790mm to 830mm across catchment)
    # Reclassified to 1-5 rank (Yadadri average ~810mm -> Rank 3 to 4)
    x_coords = np.linspace(0, 1, cols)
    y_coords = np.linspace(0, 1, rows)
    xx, yy = np.meshgrid(x_coords, y_coords)
    
    # Slight increase towards SW/W monsoon entry
    rainfall_mm = 800.0 + (1.0 - xx) * 25.0 + (1.0 - yy) * 15.0
    
    # Reclassify to 1-5 scale
    rainfall_rank = np.clip(1.0 + (rainfall_mm - 750.0) / (850.0 - 750.0) * 4.0, 1.0, 5.0).astype(np.float32)

    return {
        "geology_rank": geology_rank,
        "lulc_rank": lulc_rank,
        "soil_rank": soil_rank,
        "rainfall_rank": rainfall_rank,
        "rainfall_mm": rainfall_mm.astype(np.float32)
    }


if __name__ == "__main__":
    print("Thematic layers module ready.")
