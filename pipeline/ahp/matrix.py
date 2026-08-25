"""
Saaty's Analytic Hierarchy Process (AHP) Pairwise Comparison Matrix Solver
Computes normalized criteria weights, principal eigenvalue (lambda_max),
Consistency Index (CI), and Consistency Ratio (CR).
"""
import numpy as np
from typing import Dict, List, Tuple, Any

# Saaty's Random Consistency Index (RI) table for matrix sizes 1 to 15
RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.54, 13: 1.56, 14: 1.57, 15: 1.59
}


class AHPMatrixSolver:
    def __init__(self, layer_names: List[str], pairwise_matrix: List[List[float]]):
        self.layer_names = layer_names
        self.matrix = np.array(pairwise_matrix, dtype=float)
        self.n = len(layer_names)
        
        if self.matrix.shape != (self.n, self.n):
            raise ValueError(f"Matrix shape {self.matrix.shape} does not match number of layers {self.n}")

    def solve(self) -> Dict[str, Any]:
        """
        Calculates criteria weights and validates consistency ratio.
        Uses the geometric mean (logarithmic least squares) and exact eigenvector methods.
        """
        n = self.n
        
        # 1. Geometric Mean approximation for normalized weights
        geom_means = np.prod(self.matrix, axis=1) ** (1.0 / n)
        weights_geom = geom_means / np.sum(geom_means)

        # 2. Principal Eigenvector method
        eigvals, eigvecs = np.linalg.eig(self.matrix)
        max_idx = np.argmax(np.real(eigvals))
        lambda_max = float(np.real(eigvals[max_idx]))
        principal_eigvec = np.real(eigvecs[:, max_idx])
        weights = principal_eigvec / np.sum(principal_eigvec)

        # 3. Consistency Index (CI)
        if n > 1:
            ci = (lambda_max - n) / (n - 1)
        else:
            ci = 0.0

        # 4. Consistency Ratio (CR)
        ri = RANDOM_INDEX.get(n, 1.49)
        cr = (ci / ri) if ri > 0 else 0.0

        is_consistent = cr < 0.10

        weights_dict = {name: float(round(w, 4)) for name, w in zip(self.layer_names, weights)}

        return {
            "num_criteria": n,
            "weights": weights_dict,
            "weights_array": weights,
            "lambda_max": round(lambda_max, 4),
            "consistency_index_ci": round(ci, 4),
            "random_index_ri": ri,
            "consistency_ratio_cr": round(cr, 4),
            "is_consistent": is_consistent,
            "interpretation": (
                f"Consistency Ratio CR = {cr:.4f} is {'acceptable (< 0.10)' if is_consistent else 'inconsistent (>= 0.10)'}"
            )
        }


if __name__ == "__main__":
    from pipeline.config import AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX
    solver = AHPMatrixSolver(AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX)
    result = solver.solve()
    print("=== AHP Weight Solver Results ===")
    print(f"Criteria: {result['num_criteria']}")
    print(f"Lambda Max: {result['lambda_max']}")
    print(f"CI: {result['consistency_index_ci']}")
    print(f"CR: {result['consistency_ratio_cr']} ({'Valid' if result['is_consistent'] else 'Invalid'})")
    print("\nLayer Weights:")
    for layer, weight in result["weights"].items():
        print(f"  - {layer:20s}: {weight*100:6.2f}%")
