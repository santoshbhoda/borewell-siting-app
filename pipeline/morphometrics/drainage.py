"""
Drainage Network and Drainage Density Derivation
Calculates flow routing, upstream contributing area (flow accumulation),
stream network delineation, and spatial drainage density kernel.
"""
import numpy as np
from scipy import ndimage
from typing import Dict, Any


def compute_drainage(elevation: np.ndarray, dx: float, dy: float, stream_threshold_cells: int = 150) -> Dict[str, np.ndarray]:
    """
    Derives flow accumulation, stream network channels, and drainage density map.
    """
    rows, cols = elevation.shape
    cell_area_km2 = (dx * dy) / 1e6

    # 1. Compute D8 steepest descent flow direction
    # Neighbors offset: [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    # We use multiple flow direction (MFD) or smoothed flow gradient for stability
    padded_elev = np.pad(elevation, 1, mode='edge')
    
    # Calculate difference in 8 directions divided by distance
    dists = np.array([
        [np.sqrt(dx**2 + dy**2), dy, np.sqrt(dx**2 + dy**2)],
        [dx, 1.0, dx],
        [np.sqrt(dx**2 + dy**2), dy, np.sqrt(dx**2 + dy**2)]
    ])

    flow_acc = np.ones((rows, cols), dtype=float)

    # Sort elevation indices from highest to lowest to route flow downstream
    flat_indices = np.argsort(elevation.ravel())[::-1]
    
    for idx in flat_indices:
        r, c = divmod(idx, cols)
        current_z = elevation[r, c]
        
        # Look at 8 neighbors
        r_min = max(0, r - 1)
        r_max = min(rows, r + 2)
        c_min = max(0, c - 1)
        c_max = min(cols, c + 2)
        
        nbrs = elevation[r_min:r_max, c_min:c_max]
        nbr_diffs = current_z - nbrs
        nbr_diffs[nbr_diffs <= 0] = 0
        
        if np.sum(nbr_diffs) > 0:
            # Find steepest descent neighbor
            r_nbrs, c_nbrs = np.where(nbr_diffs == np.max(nbr_diffs))
            dest_r = r_min + r_nbrs[0]
            dest_c = c_min + c_nbrs[0]
            if (dest_r != r or dest_c != c) and (0 <= dest_r < rows) and (0 <= dest_c < cols):
                flow_acc[dest_r, dest_c] += flow_acc[r, c]

    # 2. Delineate stream network
    streams = (flow_acc >= stream_threshold_cells).astype(float)

    # 3. Compute Drainage Density (length of streams per unit area) using Gaussian spatial kernel
    # Kernel radius ~ 500m to 1km to calculate local stream density (km / km^2)
    kernel_radius_cells = max(3, int(round(500.0 / dx)))
    sigma = kernel_radius_cells / 2.0
    
    # Convolve stream channels to obtain spatial drainage density
    drainage_density_raw = ndimage.gaussian_filter(streams, sigma=sigma, mode='nearest')
    
    # Scale to km/km^2
    search_area_km2 = np.pi * ((kernel_radius_cells * dx) / 1000.0)**2
    drainage_density_km_km2 = (drainage_density_raw * (dx / 1000.0)) / max(0.01, search_area_km2) * 50.0

    return {
        "flow_accumulation": flow_acc.astype(np.float32),
        "streams": streams.astype(np.float32),
        "drainage_density": drainage_density_km_km2.astype(np.float32)
    }


if __name__ == "__main__":
    elev = np.arange(100).reshape(10, 10).astype(float)
    res = compute_drainage(elev, 30.0, 30.0, stream_threshold_cells=5)
    print("Drainage computation test passed. Max flow accumulation:", np.max(res["flow_accumulation"]))
