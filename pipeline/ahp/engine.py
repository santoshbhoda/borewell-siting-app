"""
AHP Groundwater Potential Index (GWPI) Scoring Engine
Executes Multi-Criteria Evaluation (MCE) via Weighted Linear Combination (WLC)
over all standardized thematic and morphometric layers.
"""
import numpy as np
from typing import Dict, Any, List
from pipeline.config import RECLASS_RULES, GWPI_CATEGORIES


def reclassify_slope(slope_pct: np.ndarray) -> np.ndarray:
    """
    Reclassifies slope percentage into 1-5 rank scale.
    0-3%: 5 (Nearly level - high infiltration)
    3-8%: 4 (Gentle)
    8-15%: 3 (Moderate)
    15-25%: 2 (Steep)
    >25%: 1 (Very steep - rapid runoff)
    """
    rank = np.ones_like(slope_pct, dtype=np.float32)
    rank[slope_pct <= 25.0] = 2.0
    rank[slope_pct <= 15.0] = 3.0
    rank[slope_pct <= 8.0]  = 4.0
    rank[slope_pct <= 3.0]  = 5.0
    return rank


def reclassify_percentiles(data: np.ndarray, invert: bool = False) -> np.ndarray:
    """
    Reclassifies a continuous raster into 1-5 ranks using quantiles/percentiles (20%, 40%, 60%, 80%).
    """
    p20 = np.percentile(data, 20)
    p40 = np.percentile(data, 40)
    p60 = np.percentile(data, 60)
    p80 = np.percentile(data, 80)

    rank = np.ones_like(data, dtype=np.float32)
    rank[data >= p20] = 2.0
    rank[data >= p40] = 3.0
    rank[data >= p60] = 4.0
    rank[data >= p80] = 5.0

    if invert:
        # For drainage density (high drainage density = high runoff = low groundwater storage)
        rank = 6.0 - rank

    return rank


class AHPEngine:
    def __init__(self, ahp_weights: Dict[str, float]):
        self.weights = ahp_weights

    def compute_gwpi(self, layers: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Executes weighted linear combination: GWPI = sum(W_i * R_i).
        Returns normalized 0-100 score, rank 1-5 raster, and classified zones.
        """
        # 1. Standardize all layers to 1-5 rank scale
        ranks = {}
        ranks["geology"] = np.clip(layers["geology_rank"], 1.0, 5.0)
        ranks["lineament_density"] = reclassify_percentiles(layers["lineament_density"], invert=False)
        ranks["slope"] = reclassify_slope(layers["slope_pct"])
        ranks["drainage_density"] = reclassify_percentiles(layers["drainage_density"], invert=True)
        ranks["twi"] = reclassify_percentiles(layers["twi"], invert=False)
        ranks["lulc"] = np.clip(layers["lulc_rank"], 1.0, 5.0)
        ranks["soil"] = np.clip(layers["soil_rank"], 1.0, 5.0)
        ranks["rainfall"] = np.clip(layers["rainfall_rank"], 1.0, 5.0)

        # 2. Compute Weighted Linear Combination
        raw_gwpi = np.zeros_like(ranks["geology"], dtype=np.float32)
        weight_sum = 0.0

        layer_contributions = {}
        for layer_name, weight in self.weights.items():
            if layer_name in ranks:
                layer_rank = ranks[layer_name]
                contrib = float(weight) * layer_rank
                raw_gwpi += contrib
                layer_contributions[layer_name] = contrib
                weight_sum += float(weight)

        if weight_sum > 0:
            raw_gwpi /= weight_sum

        # 3. Rescale raw GWPI (1.0 to 5.0) into standardized 0 to 100 score
        gwpi_100 = ((raw_gwpi - 1.0) / 4.0) * 100.0
        gwpi_100 = np.clip(gwpi_100, 0.0, 100.0)

        # 4. Generate discrete category index (0 to 4)
        category_grid = np.zeros_like(gwpi_100, dtype=np.int32)
        for idx, cat in enumerate(GWPI_CATEGORIES):
            mask = (gwpi_100 >= cat["min"]) & (gwpi_100 <= cat["max"])
            category_grid[mask] = idx

        return {
            "gwpi_raw": raw_gwpi.astype(np.float32),
            "gwpi_100": gwpi_100.astype(np.float32),
            "ranks": ranks,
            "category_grid": category_grid,
            "layer_contributions": layer_contributions,
            "min_score": float(np.min(gwpi_100)),
            "max_score": float(np.max(gwpi_100)),
            "mean_score": float(np.mean(gwpi_100)),
            "std_score": float(np.std(gwpi_100))
        }


if __name__ == "__main__":
    print("AHP Engine module ready.")
