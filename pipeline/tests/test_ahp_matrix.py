"""
Unit Tests for AHP Matrix, KML Parser, and Morphometrics
"""
import unittest
import os
import numpy as np

from pipeline.kml_parser import parse_kml, get_study_catchment_bbox
from pipeline.config import AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX
from pipeline.ahp.matrix import AHPMatrixSolver
from pipeline.morphometrics.slope_aspect import compute_slope_aspect
from pipeline.morphometrics.lineaments import compute_lineaments
from pipeline.morphometrics.twi import compute_twi
from pipeline.ahp.engine import AHPEngine


class TestBorewellETLPipeline(unittest.TestCase):

    def test_kml_parsing(self):
        kml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Farm.kml"))
        if os.path.exists(kml_path):
            info = parse_kml(kml_path)
            self.assertEqual(info["name"], "Karun Farm 2")
            self.assertGreater(info["area"]["acres"], 10.0)
            self.assertIn("centroid", info)

    def test_ahp_consistency_ratio(self):
        solver = AHPMatrixSolver(AHP_LAYER_NAMES, AHP_PAIRWISE_MATRIX)
        res = solver.solve()
        self.assertTrue(res["is_consistent"], f"CR {res['consistency_ratio_cr']} is >= 0.10")
        self.assertAlmostEqual(sum(res["weights"].values()), 1.0, places=2)
        self.assertLess(res["consistency_ratio_cr"], 0.05)

    def test_slope_computation(self):
        elev = np.ones((50, 50), dtype=float) * 350.0
        # Flat surface should yield ~0 slope
        res = compute_slope_aspect(elev, dx=30.0, dy=30.0)
        self.assertAlmostEqual(float(np.mean(res["slope_deg"])), 0.0, places=3)

    def test_twi_range(self):
        flow = np.ones((30, 30)) * 50.0
        slope = np.ones((30, 30)) * 4.0
        res = compute_twi(flow, slope, dx=30.0)
        self.assertGreater(res["mean_twi"], 0.0)
        self.assertFalse(np.isnan(res["mean_twi"]))


if __name__ == "__main__":
    unittest.main()
