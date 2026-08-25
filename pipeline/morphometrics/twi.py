"""
Topographic Wetness Index (TWI) Calculation
Formula: TWI = ln(a / tan(beta))
Where:
- a = Specific Catchment Area (upstream contributing area per unit contour length)
- beta = Slope angle in radians
"""
import numpy as np
from typing import Dict, Any


def compute_twi(flow_accumulation: np.ndarray, slope_deg: np.ndarray, dx: float) -> Dict[str, np.ndarray]:
    """
    Computes Topographic Wetness Index (TWI).
    """
    # Specific catchment area: contributing area in meters per contour width (dx)
    # flow_accumulation is in cell units, so area = flow_acc * dx * dy
    specific_catchment_area = np.maximum(1.0, flow_accumulation * dx)

    # Slope in radians, bounded by minimum threshold to prevent division by zero on flat terrain
    slope_rad = np.radians(np.maximum(0.1, slope_deg))
    tan_slope = np.tan(slope_rad)

    # TWI = ln(a / tan(beta))
    twi = np.log(specific_catchment_area / tan_slope)

    # Clean potential infs or NaNs
    twi = np.nan_to_num(twi, nan=0.0, posinf=20.0, neginf=0.0)
    twi = np.clip(twi, 0.0, 25.0)

    return {
        "twi": twi.astype(np.float32),
        "mean_twi": float(np.mean(twi)),
        "max_twi": float(np.max(twi))
    }


if __name__ == "__main__":
    flow = np.ones((50, 50)) * 10
    slope = np.ones((50, 50)) * 3.0
    res = compute_twi(flow, slope, dx=30.0)
    print("TWI calculation test passed. Mean TWI:", res["mean_twi"])
