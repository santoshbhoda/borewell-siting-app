"""
Integration and Unit Tests for FastAPI Endpoints
Tests Health, Spatial Evaluation, Feedback Submission, Analytics, and Providers.
"""
import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import LandPlot


class TestBackendAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        Base.metadata.create_all(bind=engine)

    def test_01_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_02_analytics_summary(self):
        response = self.client.get("/api/v1/analytics/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_plots_evaluated", data)
        self.assertIn("success_rate_percentage", data)
        self.assertGreaterEqual(data["total_plots_evaluated"], 1)

    def test_03_list_providers(self):
        response = self.client.get("/api/v1/providers")
        self.assertEqual(response.status_code, 200)
        providers = response.json()
        self.assertIsInstance(providers, list)
        self.assertGreaterEqual(len(providers), 1)
        self.assertEqual(providers[0]["is_verified"], True)

    def test_04_evaluate_polygon_plot(self):
        # Sample polygon around Karun Farm 2
        payload = {
            "plot_name": "Test Farm Parcel API",
            "state": "Telangana",
            "district": "Yadadri-Bhuvanagiri",
            "mandal": "Bhuvanagiri",
            "village": "Rayagiri",
            "coordinates": [
                [79.0864, 17.4335],
                [79.0895, 17.4344],
                [79.0897, 17.4318],
                [79.0866, 17.4315],
                [79.0864, 17.4335]
            ]
        }
        response = self.client.post("/api/v1/plots/evaluate", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["plot_name"], "Test Farm Parcel API")
        self.assertGreater(len(data["candidate_spots"]), 0)
        self.assertEqual(data["candidate_spots"][0]["rank"], 1)

        # Test retrieving the plot by ID
        plot_id = data["id"]
        get_res = self.client.get(f"/api/v1/plots/{plot_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], plot_id)

    def test_05_submit_drilling_feedback(self):
        db = SessionLocal()
        plot = db.query(LandPlot).first()
        db.close()
        self.assertIsNotNone(plot)

        feedback_payload = {
            "drilled_lat": plot.centroid_lat,
            "drilled_lon": plot.centroid_lon,
            "actual_drilling_depth_ft": 320,
            "water_strike_depth_ft": 280,
            "casing_depth_ft": 50,
            "measured_yield_lph": 2400,
            "yield_category": "Moderate (1-2 inch)",
            "ves_conducted": True,
            "contractor_name": "Sri Venkateshwara Rig Works",
            "feedback_notes": "Drilled at recommended Spot #1. Excellent water strike at 280 ft."
        }

        response = self.client.post(f"/api/v1/plots/{plot.id}/feedback", json=feedback_payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "Recorded")
        self.assertEqual(data["plot_id"], plot.id)


if __name__ == "__main__":
    unittest.main()
