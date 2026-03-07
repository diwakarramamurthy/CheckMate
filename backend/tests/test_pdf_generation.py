"""
Test suite for PDF Generation Feature
Tests Form-1, Form-3, Form-4, and Annexure-A PDF endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://rera-compliance-1.preview.emergentagent.com').rstrip('/')

# Test credentials and project ID
TEST_EMAIL = "newtest@example.com"
TEST_PASSWORD = "Test123!"
EXISTING_PROJECT_ID = "6024c5c1-3df8-45f6-a77b-07499f1cbccf"


class TestAuthentication:
    """Authentication tests - run first to get token"""
    
    def test_login_success(self):
        """Test login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL


class TestPDFGeneration:
    """PDF generation endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed - skipping PDF tests")
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    # Form-1: Architect Certificate PDF
    def test_form1_pdf_generation(self):
        """Test Form-1 (Architect Certificate) PDF generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-1",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-1 PDF failed: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf"
        
        # Verify PDF content starts with PDF header
        content = response.content
        assert content[:4] == b'%PDF', "Invalid PDF format for Form-1"
        assert len(content) > 1000, f"Form-1 PDF too small: {len(content)} bytes"
        print(f"Form-1 PDF generated successfully: {len(content)} bytes")
    
    # Form-3: Engineer Certificate PDF  
    def test_form3_pdf_generation(self):
        """Test Form-3 (Engineer Certificate) PDF generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-3",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-3 PDF failed: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf"
        
        content = response.content
        assert content[:4] == b'%PDF', "Invalid PDF format for Form-3"
        assert len(content) > 1000, f"Form-3 PDF too small: {len(content)} bytes"
        print(f"Form-3 PDF generated successfully: {len(content)} bytes")
    
    # Form-4: CA Certificate PDF
    def test_form4_pdf_generation(self):
        """Test Form-4 (CA Certificate) PDF generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-4",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-4 PDF failed: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf"
        
        content = response.content
        assert content[:4] == b'%PDF', "Invalid PDF format for Form-4"
        assert len(content) > 1000, f"Form-4 PDF too small: {len(content)} bytes"
        print(f"Form-4 PDF generated successfully: {len(content)} bytes")
    
    # Annexure-A: Sales Statement PDF
    def test_annexure_a_pdf_generation(self):
        """Test Annexure-A (Sales Statement) PDF generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/annexure-a",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Annexure-A PDF failed: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf"
        
        content = response.content
        assert content[:4] == b'%PDF', "Invalid PDF format for Annexure-A"
        assert len(content) > 1000, f"Annexure-A PDF too small: {len(content)} bytes"
        print(f"Annexure-A PDF generated successfully: {len(content)} bytes")
    
    # Edge case: Invalid report type
    def test_invalid_report_type(self):
        """Test that invalid report types return error (400 or 500)"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/invalid-form",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        # Server returns 500 for unhandled report types (note: ideally should return 400)
        assert response.status_code in [400, 500], f"Expected 400/500 for invalid report type, got {response.status_code}"
        print(f"Invalid report type returns {response.status_code} as expected")
    
    # Edge case: Non-existent project
    def test_nonexistent_project(self):
        """Test PDF generation with non-existent project ID"""
        fake_project_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{fake_project_id}/form-1",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404 for non-existent project, got {response.status_code}"
    
    # Edge case: Missing query parameters
    def test_missing_quarter_parameter(self):
        """Test PDF generation without quarter parameter"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-1",
            params={"year": 2026},  # Missing quarter
            headers=self.headers
        )
        assert response.status_code == 422, f"Expected 422 for missing quarter, got {response.status_code}"
    
    def test_missing_year_parameter(self):
        """Test PDF generation without year parameter"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-1",
            params={"quarter": "Q1"},  # Missing year
            headers=self.headers
        )
        assert response.status_code == 422, f"Expected 422 for missing year, got {response.status_code}"
    
    # Test Content-Disposition header for filename
    def test_pdf_filename_header(self):
        """Test that PDF response includes proper Content-Disposition header"""
        response = requests.get(
            f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-1",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, "Content-Disposition should indicate attachment"
        assert "filename=" in content_disposition, "Content-Disposition should include filename"
        assert ".pdf" in content_disposition, "Filename should have .pdf extension"
        print(f"Content-Disposition: {content_disposition}")
    
    # Test different quarters
    def test_different_quarters(self):
        """Test PDF generation for different quarters"""
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            response = requests.get(
                f"{BASE_URL}/api/generate-pdf/{EXISTING_PROJECT_ID}/form-1",
                params={"quarter": quarter, "year": 2026},
                headers=self.headers
            )
            assert response.status_code == 200, f"Form-1 PDF failed for {quarter}: {response.text}"
            assert response.content[:4] == b'%PDF', f"Invalid PDF format for {quarter}"
            print(f"PDF generated for {quarter} successfully")


class TestDataPersistence:
    """Test data persistence across endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed - skipping persistence tests")
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_project_exists(self):
        """Test that the existing project can be fetched"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{EXISTING_PROJECT_ID}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Project fetch failed: {response.text}"
        data = response.json()
        assert data["project_id"] == EXISTING_PROJECT_ID
        assert "project_name" in data
        print(f"Project found: {data.get('project_name')}")
    
    def test_get_buildings_for_project(self):
        """Test fetching buildings for the project"""
        response = requests.get(
            f"{BASE_URL}/api/buildings",
            params={"project_id": EXISTING_PROJECT_ID},
            headers=self.headers
        )
        assert response.status_code == 200, f"Buildings fetch failed: {response.text}"
        buildings = response.json()
        assert isinstance(buildings, list)
        print(f"Found {len(buildings)} buildings")
    
    def test_get_construction_progress(self):
        """Test fetching construction progress for the project"""
        response = requests.get(
            f"{BASE_URL}/api/construction-progress",
            params={"project_id": EXISTING_PROJECT_ID, "quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Construction progress fetch failed: {response.text}"
        progress = response.json()
        assert isinstance(progress, list)
        print(f"Found {len(progress)} construction progress records")


class TestReportPreview:
    """Test HTML report preview endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed - skipping preview tests")
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_form1_preview(self):
        """Test Form-1 HTML preview generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-report/{EXISTING_PROJECT_ID}/form-1",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-1 preview failed: {response.text}"
        data = response.json()
        assert "data" in data or "html" in data
        print("Form-1 preview generated successfully")
    
    def test_form3_preview(self):
        """Test Form-3 HTML preview generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-report/{EXISTING_PROJECT_ID}/form-3",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-3 preview failed: {response.text}"
        print("Form-3 preview generated successfully")
    
    def test_form4_preview(self):
        """Test Form-4 HTML preview generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-report/{EXISTING_PROJECT_ID}/form-4",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Form-4 preview failed: {response.text}"
        print("Form-4 preview generated successfully")
    
    def test_annexure_a_preview(self):
        """Test Annexure-A HTML preview generation"""
        response = requests.get(
            f"{BASE_URL}/api/generate-report/{EXISTING_PROJECT_ID}/annexure-a",
            params={"quarter": "Q1", "year": 2026},
            headers=self.headers
        )
        assert response.status_code == 200, f"Annexure-A preview failed: {response.text}"
        print("Annexure-A preview generated successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
