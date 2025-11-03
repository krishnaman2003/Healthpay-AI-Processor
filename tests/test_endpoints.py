"""
Test suite for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Superclaims Backend"
    assert data["status"] == "healthy"

def test_health_check():
    """Test the detailed health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data

def test_process_claim_no_files():
    """Test endpoint with no files uploaded"""
    response = client.post("/process-claim")
    assert response.status_code == 422  # Validation error

def test_process_claim_invalid_file_type():
    """Test endpoint with non-PDF file"""
    files = {"files": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/process-claim", files=files)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]

@pytest.mark.asyncio
async def test_process_claim_with_pdf(tmp_path):
    """Test endpoint with valid PDF files"""
    # This would require actual PDF files or mocking
    # For now, this is a placeholder for integration tests
    pass

# Additional test cases would go here:
# - Test with valid PDFs
# - Test with corrupted PDFs
# - Test with multiple files
# - Test agent processing logic
# - Test validation rules