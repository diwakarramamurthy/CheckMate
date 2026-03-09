"""
Land Cost Feature Tests
Tests for the new Land Cost page API endpoints and functionality.
Covers:
- GET /api/land-cost/{project_id} - Get land cost data
- POST /api/land-cost/{project_id} - Save land cost data
- Estimated and Actual land cost sections with 10 fields each
- Total calculations for both sections
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://real-estate-forms-2.preview.emergentagent.com"


class TestLandCostAPI:
    """Tests for Land Cost API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures - get auth token and project"""
        # Get auth token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Get existing projects
        projects_response = requests.get(f"{BASE_URL}/api/projects", headers=self.headers)
        assert projects_response.status_code == 200, f"Failed to get projects: {projects_response.text}"
        projects = projects_response.json()
        assert len(projects) > 0, "No projects found in database for testing"
        self.project_id = projects[0]["project_id"]
        self.project_name = projects[0]["project_name"]
        print(f"Testing with project: {self.project_name} (ID: {self.project_id})")
    
    def test_get_land_cost_returns_200(self):
        """Test GET /api/land-cost/{project_id} returns 200 status code"""
        response = requests.get(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/land-cost returns 200")
    
    def test_get_land_cost_returns_correct_structure(self):
        """Test GET /api/land-cost returns correct data structure with estimated and actual sections"""
        response = requests.get(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure has project_id, estimated, and actual
        assert "project_id" in data, "Response missing 'project_id'"
        assert "estimated" in data, "Response missing 'estimated' section"
        assert "actual" in data, "Response missing 'actual' section"
        
        # Check estimated section has all 10 fields (a-j)
        expected_fields = [
            "land_cost", "premium_cost", "tdr_cost", "statutory_cost",
            "land_premium", "under_rehab_scheme", "estimated_rehab_cost",
            "actual_rehab_cost", "land_clearance_cost", "asr_linked_premium"
        ]
        
        for field in expected_fields:
            assert field in data["estimated"], f"Estimated section missing '{field}'"
            assert field in data["actual"], f"Actual section missing '{field}'"
        
        # Check totals
        assert "total" in data["estimated"], "Estimated section missing 'total'"
        assert "total" in data["actual"], "Actual section missing 'total'"
        
        print("PASS: GET /api/land-cost returns correct structure with all 10 fields")
    
    def test_post_land_cost_saves_data(self):
        """Test POST /api/land-cost/{project_id} saves estimated and actual costs"""
        test_data = {
            "estimated": {
                "land_cost": 5000000,
                "premium_cost": 1000000,
                "tdr_cost": 500000,
                "statutory_cost": 200000,
                "land_premium": 300000,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 100000,
                "asr_linked_premium": 50000
            },
            "actual": {
                "land_cost": 5200000,
                "premium_cost": 1100000,
                "tdr_cost": 480000,
                "statutory_cost": 210000,
                "land_premium": 300000,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 95000,
                "asr_linked_premium": 50000
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers,
            json=test_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        saved_data = response.json()
        assert saved_data["project_id"] == self.project_id
        
        # Verify estimated total calculation
        expected_estimated_total = sum(test_data["estimated"].values())
        assert saved_data["estimated"]["total"] == expected_estimated_total, \
            f"Estimated total mismatch: expected {expected_estimated_total}, got {saved_data['estimated']['total']}"
        
        # Verify actual total calculation
        expected_actual_total = sum(test_data["actual"].values())
        assert saved_data["actual"]["total"] == expected_actual_total, \
            f"Actual total mismatch: expected {expected_actual_total}, got {saved_data['actual']['total']}"
        
        print(f"PASS: POST /api/land-cost saves data correctly")
        print(f"  Estimated Total: {saved_data['estimated']['total']}")
        print(f"  Actual Total: {saved_data['actual']['total']}")
    
    def test_post_land_cost_data_persists(self):
        """Test that saved land cost data persists and can be retrieved"""
        # First save data
        test_data = {
            "estimated": {
                "land_cost": 7500000,
                "premium_cost": 1500000,
                "tdr_cost": 750000,
                "statutory_cost": 300000,
                "land_premium": 400000,
                "under_rehab_scheme": 100000,
                "estimated_rehab_cost": 200000,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 150000,
                "asr_linked_premium": 75000
            },
            "actual": {
                "land_cost": 7800000,
                "premium_cost": 1600000,
                "tdr_cost": 720000,
                "statutory_cost": 320000,
                "land_premium": 400000,
                "under_rehab_scheme": 100000,
                "estimated_rehab_cost": 200000,
                "actual_rehab_cost": 180000,
                "land_clearance_cost": 145000,
                "asr_linked_premium": 80000
            }
        }
        
        # Save
        save_response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers,
            json=test_data
        )
        assert save_response.status_code == 200
        
        # Retrieve and verify
        get_response = requests.get(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        
        # Verify each estimated field
        for field, value in test_data["estimated"].items():
            assert retrieved_data["estimated"][field] == value, \
                f"Estimated {field} mismatch: expected {value}, got {retrieved_data['estimated'][field]}"
        
        # Verify each actual field
        for field, value in test_data["actual"].items():
            assert retrieved_data["actual"][field] == value, \
                f"Actual {field} mismatch: expected {value}, got {retrieved_data['actual'][field]}"
        
        print("PASS: Land cost data persists correctly (Create -> GET verification)")
    
    def test_get_land_cost_empty_project_returns_defaults(self):
        """Test GET /api/land-cost for project without land cost returns default values"""
        # Use a fake project ID
        fake_project_id = "test-fake-project-id-12345"
        response = requests.get(
            f"{BASE_URL}/api/land-cost/{fake_project_id}",
            headers=self.headers
        )
        # Should still return 200 with default/empty values
        assert response.status_code == 200, f"Expected 200 for empty project, got {response.status_code}"
        data = response.json()
        
        # Should have default structure with zeros
        assert data["estimated"]["total"] == 0, "Expected estimated total to be 0 for empty project"
        assert data["actual"]["total"] == 0, "Expected actual total to be 0 for empty project"
        
        print("PASS: GET /api/land-cost returns default values for project without data")
    
    def test_land_cost_total_calculation_correct(self):
        """Test that total calculation sums all 10 fields correctly"""
        test_data = {
            "estimated": {
                "land_cost": 1000000,       # a
                "premium_cost": 200000,      # b
                "tdr_cost": 300000,          # c
                "statutory_cost": 400000,    # d
                "land_premium": 500000,      # e
                "under_rehab_scheme": 600000,# f
                "estimated_rehab_cost": 700000,  # g
                "actual_rehab_cost": 800000,     # h
                "land_clearance_cost": 900000,   # i
                "asr_linked_premium": 100000     # j
            },
            "actual": {
                "land_cost": 0,
                "premium_cost": 0,
                "tdr_cost": 0,
                "statutory_cost": 0,
                "land_premium": 0,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 0,
                "asr_linked_premium": 0
            }
        }
        
        expected_total = 5500000  # Sum of all estimated values
        
        response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers,
            json=test_data
        )
        assert response.status_code == 200
        saved_data = response.json()
        
        assert saved_data["estimated"]["total"] == expected_total, \
            f"Total calculation incorrect: expected {expected_total}, got {saved_data['estimated']['total']}"
        
        print(f"PASS: Total calculation correct - {expected_total}")
    
    def test_land_cost_zero_values_handled(self):
        """Test that zero values are handled correctly"""
        test_data = {
            "estimated": {
                "land_cost": 0,
                "premium_cost": 0,
                "tdr_cost": 0,
                "statutory_cost": 0,
                "land_premium": 0,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 0,
                "asr_linked_premium": 0
            },
            "actual": {
                "land_cost": 0,
                "premium_cost": 0,
                "tdr_cost": 0,
                "statutory_cost": 0,
                "land_premium": 0,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 0,
                "asr_linked_premium": 0
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers,
            json=test_data
        )
        assert response.status_code == 200
        saved_data = response.json()
        
        assert saved_data["estimated"]["total"] == 0, "Estimated total should be 0"
        assert saved_data["actual"]["total"] == 0, "Actual total should be 0"
        
        print("PASS: Zero values handled correctly")
    
    def test_land_cost_requires_authentication(self):
        """Test that land cost endpoints require authentication"""
        # Test GET without auth
        response = requests.get(f"{BASE_URL}/api/land-cost/{self.project_id}")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        # Test POST without auth
        response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            json={"estimated": {}, "actual": {}}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        print("PASS: Land cost endpoints require authentication")


class TestLandCostIntegration:
    """Integration tests - Land Cost data flow to Project Costs page"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        projects_response = requests.get(f"{BASE_URL}/api/projects", headers=self.headers)
        projects = projects_response.json()
        self.project_id = projects[0]["project_id"] if projects else None
    
    def test_land_cost_data_available_for_project_costs_page(self):
        """Test that land cost data saved can be retrieved for Project Costs page display"""
        # Save test land cost data
        test_data = {
            "estimated": {
                "land_cost": 10000000,
                "premium_cost": 2000000,
                "tdr_cost": 1000000,
                "statutory_cost": 500000,
                "land_premium": 800000,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 200000,
                "asr_linked_premium": 150000
            },
            "actual": {
                "land_cost": 10500000,
                "premium_cost": 2100000,
                "tdr_cost": 980000,
                "statutory_cost": 520000,
                "land_premium": 800000,
                "under_rehab_scheme": 0,
                "estimated_rehab_cost": 0,
                "actual_rehab_cost": 0,
                "land_clearance_cost": 190000,
                "asr_linked_premium": 160000
            }
        }
        
        # Save land cost
        save_response = requests.post(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers,
            json=test_data
        )
        assert save_response.status_code == 200
        
        # Verify data can be retrieved (simulating Project Costs page fetch)
        get_response = requests.get(
            f"{BASE_URL}/api/land-cost/{self.project_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        data = get_response.json()
        
        # Verify estimated land cost for display
        assert data["estimated"]["land_cost"] == test_data["estimated"]["land_cost"]
        assert "total" in data["estimated"]
        
        # Verify actual land cost for display
        assert data["actual"]["land_cost"] == test_data["actual"]["land_cost"]
        assert "total" in data["actual"]
        
        print("PASS: Land cost data available for Project Costs page integration")
        print(f"  Estimated Total: {data['estimated']['total']}")
        print(f"  Actual Total: {data['actual']['total']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
