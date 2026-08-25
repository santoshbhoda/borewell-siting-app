"""
Slope and Aspect Extraction from DEM
Implements Horn's 3x3 finite-difference gradient operator for slope (degrees and percent).
"""
import numpy as np
from scipy import ndimage
from typing import Dict, Any


def compute_slope_aspect(elevation: np.ndarray, dx: float, dy: float) -> Dict[str, np.ndarray]:
    """
    Computes slope (degrees, percent) and aspect from elevation grid using Horn's algorithm.
    """
    # Horn's kernel for dz/dx
    kernel_x = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=float) / (8.0 * dx)

    # Horn's kernel for dz/dy (North is row 0, so positive y is decreasing row index)
    kernel_y = np.array([
        [ 1,  2,  1],
        [ 0,  0,  0],
        [-1, -2, -1]
    ], dtype=float) / (8.0 * dy)

    dz_dx = ndimage.convolve(elevation, kernel_x, mode='nearest')
    dz_dy = ndimage.convolve(elevation, kernel_y, mode='nearest')

    # Gradient magnitude
    gradient = np.sqrt(dz_dx**2 + dz_dy**2)
    
    # Slope in radians, degrees, and percentage
    slope_rad = np.arctan(gradient)
    slope_deg = np.degrees(slope_rad)
    slope_pct = np.tan(slope_rad) * 100.0

    # Aspect in degrees (0 to 360 clockwise from North)
    aspect_rad = np.arctan2(dz_dy, -dz_dx)
    aspect_deg = 90.0 - np.degrees(aspect_rad)
    aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360.0, aspect_deg)

    return {
        "slope_deg": slope_deg.astype(np.float32),
        "slope_pct": slope_pct.astype(np.float32),
        "aspect_deg": aspect_deg.astype(np.float32),
        "dz_dx": dz_dx.astype(np.float32),
        "dz_dy": dz_dy.astype(np.float32)
    }


if __name__ == "__main__":
    test_elev = np.random.uniform(300, 400, (100, 100))
    res = compute_slope_aspect(test_elev, dx=30.0, dy=30.0)
    print("Slope calculation test:")
    print(f"Mean slope: {np.mean(res['slope_deg']):.2f} deg ({np.mean(res['slope_pct']):.2f}%)")
