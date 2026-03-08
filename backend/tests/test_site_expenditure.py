"""
Test Suite for On Site Expenditure Feature
Tests the following:
1. POST/GET /api/site-expenditure - Estimated costs on Buildings & Infrastructure page
2. POST/GET /api/actual-site-expenditure - Actual costs on Construction Progress page
3. Data flow verification from pages to Project Costs page
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://real-estate-forms-2.preview.emergentagent.com').rstrip('/')
TEST_CREDENTIALS = {"email": "test@example.com", "password": "test123"}


@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token for test session"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_CREDENTIALS)
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def headers(auth_token):
    """Auth headers for API requests"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def project_id(headers):
    """Get existing project ID for testing"""
    response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) > 0, "No projects found for testing"
    return projects[0]["project_id"]


class TestEstimatedSiteExpenditure:
    """Test estimated site expenditure on Buildings & Infrastructure page"""
    
    def test_get_site_expenditure_returns_200(self, headers, project_id):
        """GET /api/site-expenditure/{project_id} returns 200"""
        response = requests.get(f"{BASE_URL}/api/site-expenditure/{project_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET site-expenditure returns 200")
    
    def test_get_site_expenditure_has_correct_fields(self, headers, project_id):
        """GET response contains all required cost fields"""
        response = requests.get(f"{BASE_URL}/api/site-expenditure/{project_id}", headers=headers)
        data = response.json()
        
        required_fields = ["site_development_cost", "salaries", "consultants_fee", 
                          "site_overheads", "services_cost", "machinery_cost"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print(f"✓ Response contains all required fields")
    
    def test_post_site_expenditure_creates_record(self, headers, project_id):
        """POST /api/site-expenditure creates or updates estimated costs"""
        test_data = {
            "site_development_cost": 100000,
            "salaries": 200000,
            "consultants_fee": 150000,
            "site_overheads": 50000,
            "services_cost": 75000,
            "machinery_cost": 125000
        }
        
        response = requests.post(
            f"{BASE_URL}/api/site-expenditure?project_id={project_id}",
            headers=headers,
            json=test_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["site_development_cost"] == 100000
        assert data["salaries"] == 200000
        assert data["total"] == 700000
        print(f"✓ POST site-expenditure creates record with total: {data['total']}")
    
    def test_post_site_expenditure_calculates_total(self, headers, project_id):
        """POST correctly calculates total from all fields"""
        test_data = {
            "site_development_cost": 10000,
            "salaries": 20000,
            "consultants_fee": 30000,
            "site_overheads": 40000,
            "services_cost": 50000,
            "machinery_cost": 60000
        }
        
        response = requests.post(
            f"{BASE_URL}/api/site-expenditure?project_id={project_id}",
            headers=headers,
            json=test_data
        )
        data = response.json()
        
        expected_total = 10000 + 20000 + 30000 + 40000 + 50000 + 60000
        assert data["total"] == expected_total, f"Expected total {expected_total}, got {data['total']}"
        print(f"✓ Total calculated correctly: {expected_total}")


class TestActualSiteExpenditure:
    """Test actual site expenditure on Construction Progress page"""
    
    def test_get_actual_expenditure_returns_200(self, headers, project_id):
        """GET /api/actual-site-expenditure returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/{project_id}?quarter=Q1&year=2025",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET actual-site-expenditure returns 200")
    
    def test_get_actual_expenditure_requires_quarter_and_year(self, headers, project_id):
        """GET returns 422 if quarter or year missing"""
        # Missing both
        response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/{project_id}",
            headers=headers
        )
        assert response.status_code == 422, "Should require quarter and year"
        
        # Missing year
        response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/{project_id}?quarter=Q1",
            headers=headers
        )
        assert response.status_code == 422, "Should require year"
        print(f"✓ Validation works: quarter and year are required")
    
    def test_post_actual_expenditure_creates_record(self, headers, project_id):
        """POST /api/actual-site-expenditure creates quarterly actual costs"""
        test_data = {
            "site_development_cost": 50000,
            "salaries": 150000,
            "consultants_fee": 75000,
            "site_overheads": 25000,
            "services_cost": 30000,
            "machinery_cost": 100000
        }
        
        response = requests.post(
            f"{BASE_URL}/api/actual-site-expenditure?project_id={project_id}&quarter=Q2&year=2025",
            headers=headers,
            json=test_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["quarter"] == "Q2"
        assert data["year"] == 2025
        assert data["site_development_cost"] == 50000
        print(f"✓ POST actual-site-expenditure creates record for Q2 2025")
    
    def test_actual_expenditure_calculates_total(self, headers, project_id):
        """POST correctly calculates total actual cost"""
        test_data = {
            "site_development_cost": 10000,
            "salaries": 20000,
            "consultants_fee": 30000,
            "site_overheads": 40000,
            "services_cost": 50000,
            "machinery_cost": 60000
        }
        
        response = requests.post(
            f"{BASE_URL}/api/actual-site-expenditure?project_id={project_id}&quarter=Q3&year=2025",
            headers=headers,
            json=test_data
        )
        data = response.json()
        
        expected_total = 210000  # sum of all fields
        assert data["total"] == expected_total, f"Expected total {expected_total}, got {data['total']}"
        print(f"✓ Actual total calculated correctly: {expected_total}")
    
    def test_actual_expenditure_persists_by_quarter(self, headers, project_id):
        """Verify data is stored separately per quarter"""
        # Save Q1 data
        q1_data = {"site_development_cost": 10000, "salaries": 0, "consultants_fee": 0, 
                   "site_overheads": 0, "services_cost": 0, "machinery_cost": 0}
        requests.post(
            f"{BASE_URL}/api/actual-site-expenditure?project_id={project_id}&quarter=Q1&year=2026",
            headers=headers, json=q1_data
        )
        
        # Save Q4 data with different value
        q4_data = {"site_development_cost": 90000, "salaries": 0, "consultants_fee": 0, 
                   "site_overheads": 0, "services_cost": 0, "machinery_cost": 0}
        requests.post(
            f"{BASE_URL}/api/actual-site-expenditure?project_id={project_id}&quarter=Q4&year=2026",
            headers=headers, json=q4_data
        )
        
        # Verify Q1 still has original value
        q1_response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/{project_id}?quarter=Q1&year=2026",
            headers=headers
        )
        assert q1_response.json()["site_development_cost"] == 10000
        
        # Verify Q4 has different value
        q4_response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/{project_id}?quarter=Q4&year=2026",
            headers=headers
        )
        assert q4_response.json()["site_development_cost"] == 90000
        print(f"✓ Data persists separately by quarter")


class TestDataFlowToProjectCosts:
    """Test that data flows correctly to Project Costs page"""
    
    def test_estimated_development_cost_includes_site_expenditure(self, headers, project_id):
        """GET estimated-development-cost includes site expenditure data"""
        # First set site expenditure
        site_exp = {
            "site_development_cost": 100000,
            "salaries": 200000,
            "consultants_fee": 150000,
            "site_overheads": 50000,
            "services_cost": 75000,
            "machinery_cost": 125000
        }
        requests.post(
            f"{BASE_URL}/api/site-expenditure?project_id={project_id}",
            headers=headers, json=site_exp
        )
        
        # Get estimated development cost
        response = requests.get(
            f"{BASE_URL}/api/estimated-development-cost/{project_id}",
            headers=headers
        )
        data = response.json()
        
        # Verify site expenditure fields are present
        assert data.get("site_development_cost") == 100000
        assert data.get("salaries") == 200000
        assert data.get("consultants_fee") == 150000
        print(f"✓ Site expenditure data flows to estimated development cost")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_actual_expenditure_nonexistent_project_returns_defaults(self, headers):
        """GET returns default values for non-existent project"""
        response = requests.get(
            f"{BASE_URL}/api/actual-site-expenditure/nonexistent-id?quarter=Q1&year=2025",
            headers=headers
        )
        # Should still return 200 with default values
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        print(f"✓ Returns defaults for non-existent project")
    
    def test_post_with_zero_values(self, headers, project_id):
        """POST with all zero values works correctly"""
        zero_data = {
            "site_development_cost": 0,
            "salaries": 0,
            "consultants_fee": 0,
            "site_overheads": 0,
            "services_cost": 0,
            "machinery_cost": 0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/actual-site-expenditure?project_id={project_id}&quarter=Q1&year=2024",
            headers=headers,
            json=zero_data
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0
        print(f"✓ Zero values handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
