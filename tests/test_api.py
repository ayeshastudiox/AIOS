import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app, UPLOAD_DIR

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield
    # Teardown: Clean up test files
    test_file = os.path.join(UPLOAD_DIR, "test_sample.csv")
    if os.path.exists(test_file):
        os.remove(test_file)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AIOS Backend is running smoothly!"}

def test_upload_invalid_file_extension():
    file_content = b"invalid content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_upload_valid_csv():
    csv_data = b"date,product_name,units_sold,unit_price,total_revenue\n2026-08-01,Product A,10,15.00,150.00"
    files = {"file": ("test_sample.csv", io.BytesIO(csv_data), "text/csv")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    assert response.json()["filename"] == "test_sample.csv"

def test_analytics_file_not_found():
    response = client.get("/api/analytics/non_existent.csv")
    assert response.status_code == 404

def test_analytics_success():
    # First upload a valid file
    csv_data = b"date,product_name,units_sold,unit_price,total_revenue\n2026-08-01,Product A,10,15.00,150.00"
    files = {"file": ("test_sample.csv", io.BytesIO(csv_data), "text/csv")}
    client.post("/api/upload", files=files)

    # Test analytics endpoint
    response = client.get("/api/analytics/test_sample.csv")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_revenue"] == 150.00
    assert data["total_units_sold"] == 10

def test_storage_status():
    response = client.get("/api/storage-status")
    assert response.status_code == 200
    assert "total_files" in response.json()