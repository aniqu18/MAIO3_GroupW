import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test that the health endpoint returns 200"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_valid_input():
    """Test prediction with valid input"""
    payload = {
        "features": [0.05, 0.05, 0.02, 0.01, -0.03, -0.04, -0.04, -0.02, 0.01, 0.02]
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert isinstance(data["risk_score"], float)

def test_predict_missing_features():
    """Test that missing features returns 422"""
    payload = {}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 422  # FastAPI validation error
    data = response.json()
    assert "detail" in data