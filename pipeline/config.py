"""
Configuration for Groundwater Potential Siting Pipeline
Hydrogeological parameters calibrated for Hard-Rock Peninsular Gneissic Complex (Yadadri / Musi Basin).
"""
from typing import Dict, Any, List

# Regional Hydrogeology Profile: Hard Rock Granites & Gneisses (Telangana / Musi Basin)
HYDRO_PROFILE = {
    "name": "Telangana Hard-Rock Peninsular Gneissic Terrain",
    "rock_type": "Granite, Granodiorite & Gneiss with secondary fracture porosity",
    "target_aquifer": "Weathered mantle (0-15m) and fractured bedrock zones (15-60m)",
    "average_annual_rainfall_mm": 810.0,
    "regulatory_framework": "Telangana WALTA (Water, Land and Trees Act, 2002)"
}

# Thematic Layers and their AHP Weights (summing to 1.0 / 100%)
# In hard rock, Lithology & Lineaments dominate secondary porosity, followed by Slope & Drainage.
AHP_LAYER_NAMES = [
    "geology",          # Lithology & Rock Type
    "lineament_density",# Fracture / Lineament Density
    "slope",            # Topographic Slope (%)
    "drainage_density", # Drainage / Stream Density
    "twi",              # Topographic Wetness Index
    "lulc",             # Land Use / Land Cover
    "soil",             # Soil Infiltration Capacity
    "rainfall"          # Gridded Precipitation
]

# Pairwise Comparison Matrix (Saaty Scale 1 to 9)
# Format: Matrix[i][j] indicates importance of layer i relative to layer j
# 1 = Equal, 3 = Moderate, 5 = Strong, 7 = Very Strong, 9 = Extreme
AHP_PAIRWISE_MATRIX = [
    # Geol   Lineam  Slope   Drain   TWI     LULC    Soil    Rain
    [ 1.0,   1.25,   2.0,    2.5,    3.0,    3.5,    4.0,    5.0 ], # Geology
    [ 0.8,   1.0,    1.5,    2.0,    2.5,    3.0,    3.5,    4.0 ], # Lineaments
    [ 0.5,   0.67,   1.0,    1.5,    2.0,    2.5,    3.0,    3.5 ], # Slope
    [ 0.4,   0.5,    0.67,   1.0,    1.5,    2.0,    2.5,    3.0 ], # Drainage
    [ 0.33,  0.4,    0.5,    0.67,   1.0,    1.5,    2.0,    2.5 ], # TWI
    [ 0.29,  0.33,   0.4,    0.5,    0.67,   1.0,    1.5,    2.0 ], # LULC
    [ 0.25,  0.29,   0.33,   0.4,    0.5,    0.67,   1.0,    1.5 ], # Soil
    [ 0.2,   0.25,   0.29,   0.33,   0.4,    0.5,    0.67,   1.0 ]  # Rainfall
]

# Standard Reclassification Scales (Rank 1: Very Poor, Rank 5: Excellent)
RECLASS_RULES = {
    "slope_pct": [
        {"max": 3.0, "rank": 5, "desc": "Nearly Level (0-3%) - High Infiltration"},
        {"max": 8.0, "rank": 4, "desc": "Gentle Slope (3-8%) - Moderate Infiltration"},
        {"max": 15.0, "rank": 3, "desc": "Moderate Slope (8-15%) - Moderate Runoff"},
        {"max": 25.0, "rank": 2, "desc": "Steep (15-25%) - High Runoff"},
        {"max": 999.0, "rank": 1, "desc": "Very Steep (>25%) - Very High Runoff"}
    ],
    "lineament_density": [
        {"min_percentile": 80, "rank": 5, "desc": "Very High Fracture Density (Excellent Porosity)"},
        {"min_percentile": 60, "rank": 4, "desc": "High Fracture Density"},
        {"min_percentile": 40, "rank": 3, "desc": "Moderate Fracture Density"},
        {"min_percentile": 20, "rank": 2, "desc": "Low Fracture Density"},
        {"min_percentile": 0,  "rank": 1, "desc": "Nil / Sparse Lineaments (Poor Porosity)"}
    ],
    "drainage_density": [
        {"min_percentile": 80, "rank": 1, "desc": "Very High Drainage Density (Rapid Surface Runoff)"},
        {"min_percentile": 60, "rank": 2, "desc": "High Drainage Density"},
        {"min_percentile": 40, "rank": 3, "desc": "Moderate Drainage Density"},
        {"min_percentile": 20, "rank": 4, "desc": "Low Drainage Density (Good Infiltration)"},
        {"min_percentile": 0,  "rank": 5, "desc": "Very Low Drainage Density (Excellent Infiltration)"}
    ],
    "twi": [
        {"min_percentile": 80, "rank": 5, "desc": "Very High Wetness Index (Valley / Convergence Zone)"},
        {"min_percentile": 60, "rank": 4, "desc": "High Wetness Index"},
        {"min_percentile": 40, "rank": 3, "desc": "Moderate Wetness Index"},
        {"min_percentile": 20, "rank": 2, "desc": "Low Wetness Index"},
        {"min_percentile": 0,  "rank": 1, "desc": "Very Low Wetness Index (Ridge / Crest)"}
    ],
    "geology": {
        "Valley Fill / Alluvium": 5,
        "Highly Weathered Granite": 4,
        "Moderately Fractured Gneiss": 3,
        "Massive Granite / Residual Hill": 2,
        "Dolerite Dyke / Quartz Ridge": 1
    },
    "lulc": {
        "Water Body / Village Tank (Cheruvu)": 5,
        "Irrigated Agricultural Cropland": 4,
        "Plantation / Orchard": 3,
        "Fallow / Shrubland": 2,
        "Barren Rocky / Built-up": 1
    },
    "soil": {
        "Valley Loam / Silt Loam": 5,
        "Sandy Loam (Chalka)": 4,
        "Gravelly Sandy Loam": 3,
        "Clay Loam / Regur": 2,
        "Rocky / Lithosol": 1
    },
    "rainfall": {
        "High (>850mm)": 5,
        "Moderate-High (800-850mm)": 4,
        "Moderate (750-800mm)": 3,
        "Low-Moderate (700-750mm)": 2,
        "Low (<700mm)": 1
    }
}

# Potential Categories for Final GWPI Score (0-100)
GWPI_CATEGORIES = [
    {"min": 80, "max": 100, "label": "Very High Potential", "color": "#006837"},
    {"min": 65, "max": 80,  "label": "High Potential",      "color": "#31a354"},
    {"min": 50, "max": 65,  "label": "Moderate Potential",  "color": "#78c679"},
    {"min": 35, "max": 50,  "label": "Low Potential",       "color": "#fe9929"},
    {"min": 0,  "max": 35,  "label": "Very Poor Potential", "color": "#d73027"}
]

# Siting Constraints (WALTA & Engineering Buffer Rules)
SITING_CONSTRAINTS = {
    "min_distance_between_borewells_m": 150.0, # WALTA recommended spacing in hard-rock
    "min_distance_from_boundary_m": 10.0,      # Buffer from plot boundary
    "max_candidate_points": 3                  # Top candidate points
}
