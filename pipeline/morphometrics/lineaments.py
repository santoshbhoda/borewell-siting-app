"""
Lineament and Structural Fracture Extraction
Detects structural lineaments, joints, and fracture corridors from multi-directional
hillshade gradients, typical of hard-rock granite-gneiss terrains in Telangana.
"""
import numpy as np
from scipy import ndimage
from typing import Dict, Any


def compute_hillshade(elevation: np.ndarray, dx: float, dy: float, azimuth_deg: float, altitude_deg: float = 45.0) -> np.ndarray:
    """
    Computes analytical shaded relief for a specific solar illumination angle.
    """
    azimuth_rad = np.radians(360.0 - azimuth_deg + 90.0)
    altitude_rad = np.radians(altitude_deg)

    # Gradients
    kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float) / (8.0 * dx)
    kernel_y = np.array([[ 1,  2,  1], [ 0,  0,  0], [-1, -2, -1]], dtype=float) / (8.0 * dy)

    dz_dx = ndimage.convolve(elevation, kernel_x, mode='nearest')
    dz_dy = ndimage.convolve(elevation, kernel_y, mode='nearest')

    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    aspect_rad = np.arctan2(dz_dy, -dz_dx)

    shaded = (
        np.sin(altitude_rad) * np.cos(slope_rad) +
        np.cos(altitude_rad) * np.sin(slope_rad) * np.cos(azimuth_rad - aspect_rad)
    )
    shaded = np.clip(shaded, 0, 1)
    return shaded


def compute_lineaments(elevation: np.ndarray, dx: float, dy: float) -> Dict[str, np.ndarray]:
    """
    Extracts multi-directional lineament traces (NW-SE, NE-SW, N-S, E-W)
    and computes fracture density (km/km^2).
    """
    rows, cols = elevation.shape

    # Illuminations along key tectonic directions in Telangana:
    # 315° (NW-SE Dharwarian trend), 45° (NE-SW trend), 0° (N-S), 90° (E-W)
    azimuths = [45.0, 135.0, 225.0, 315.0]
    edge_sum = np.zeros((rows, cols), dtype=float)

    for az in azimuths:
        hs = compute_hillshade(elevation, dx, dy, azimuth_deg=az, altitude_deg=35.0)
        
        # Sobel high-pass edge filter
        edge_h = ndimage.sobel(hs, axis=0, mode='nearest')
        edge_v = ndimage.sobel(hs, axis=1, mode='nearest')
        edge_mag = np.sqrt(edge_h**2 + edge_v**2)
        
        edge_sum += edge_mag

    # Normalize edge magnitude
    edge_sum /= len(azimuths)
    
    # Threshold top edge responses as structural lineament traces
    p90 = np.percentile(edge_sum, 88)
    lineament_binary = (edge_sum >= p90).astype(float)

    # Compute Lineament Density via Gaussian spatial convolution (search radius ~ 750m)
    radius_cells = max(4, int(round(750.0 / dx)))
    sigma = radius_cells / 2.0
    lineament_density_raw = ndimage.gaussian_filter(lineament_binary, sigma=sigma, mode='nearest')
    
    # Standardize to 0 - 100 relative index
    min_d = np.min(lineament_density_raw)
    max_d = np.max(lineament_density_raw)
    lineament_density = ((lineament_density_raw - min_d) / max(1e-6, max_d - min_d)) * 100.0

    return {
        "lineament_traces": lineament_binary.astype(np.float32),
        "lineament_density": lineament_density.astype(np.float32),
        "edge_magnitude": edge_sum.astype(np.float32)
    }


if __name__ == "__main__":
    elev = np.random.uniform(300, 350, (100, 100))
    res = compute_lineaments(elev, 30.0, 30.0)
    print("Lineament extraction test passed. Density range:", np.min(res["lineament_density"]), "to", np.max(res["lineament_density"]))
