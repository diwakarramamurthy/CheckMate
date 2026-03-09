#!/usr/bin/env python3
"""
RERA Compliance Manager - Backend API Testing
Tests all the core functionalities of the FastAPI backend
"""

import requests
import sys
import json
import time
from datetime import datetime

class RERABackendTester:
    def __init__(self, base_url="https://real-estate-forms-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.test_user = None
        self.test_project_id = None
        self.test_building_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_test(self, name, success, message="", error_detail=""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if message:
            print(f"    {message}")
        if error_detail:
            print(f"    Error: {error_detail}")
            self.errors.append({"test": name, "error": error_detail})
        if success:
            self.tests_passed += 1
        print()

    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            return response
        except Exception as e:
            return None

    def test_health_check(self):
        """Test API health endpoint"""
        response = self.make_request('GET', '/health')
        if response and response.status_code == 200:
            self.log_test("Health Check", True, "API is healthy")
            return True
        else:
            self.log_test("Health Check", False, error_detail="Health endpoint failed")
            return False

    def test_user_registration(self):
        """Test user registration with different roles"""
        test_email = f"test_user_{int(time.time())}@example.com"
        registration_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "name": "Test User",
            "role": "developer",
            "phone": "+919876543210",
            "firm_name": "Test Developer Firm"
        }
        
        response = self.make_request('POST', '/auth/register', registration_data)
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                self.token = data['access_token']
                self.test_user = data['user']
                self.log_test("User Registration", True, f"User created with ID: {self.test_user['user_id']}")
                return True
        
        self.log_test("User Registration", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        return False

    def test_user_login(self):
        """Test user login"""
        if not self.test_user:
            self.log_test("User Login", False, error_detail="No test user available")
            return False
        
        login_data = {
            "email": self.test_user['email'],
            "password": "TestPassword123!"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.log_test("User Login", True, "Login successful")
                return True
        
        self.log_test("User Login", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        response = self.make_request('GET', '/auth/me')
        if response and response.status_code == 200:
            data = response.json()
            if 'user_id' in data and 'email' in data:
                self.log_test("Get User Profile", True, f"Profile retrieved for: {data['email']}")
                return True
        
        self.log_test("Get User Profile", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        return False

    def test_project_crud(self):
        """Test project CRUD operations"""
        # Create project
        project_data = {
            "project_name": f"Test Project {int(time.time())}",
            "state": "GOA",
            "rera_number": f"RERA/GOA/{int(time.time())}",
            "promoter_name": "Test Promoter Ltd",
            "promoter_address": "123 Test Address, Goa",
            "project_address": "456 Project Site, Goa",
            "district": "North Goa",
            "architect_name": "Test Architect",
            "architect_license": "AR123456",
            "engineer_name": "Test Engineer", 
            "engineer_license": "EN123456",
            "ca_name": "Test CA",
            "ca_firm_name": "Test CA Firm"
        }
        
        # CREATE
        response = self.make_request('POST', '/projects', project_data)
        if response and response.status_code == 200:
            data = response.json()
            self.test_project_id = data['project_id']
            self.log_test("Project Creation", True, f"Project created with ID: {self.test_project_id}")
        else:
            self.log_test("Project Creation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
            return False

        # READ
        response = self.make_request('GET', f'/projects/{self.test_project_id}')
        if response and response.status_code == 200:
            self.log_test("Project Read", True, "Project retrieved successfully")
        else:
            self.log_test("Project Read", False, error_detail=f"Status: {response.status_code if response else 'No response'}")

        # LIST
        response = self.make_request('GET', '/projects')
        if response and response.status_code == 200:
            projects = response.json()
            if isinstance(projects, list) and len(projects) > 0:
                self.log_test("Project List", True, f"Retrieved {len(projects)} projects")
            else:
                self.log_test("Project List", False, error_detail="No projects in list")
        else:
            self.log_test("Project List", False, error_detail=f"Status: {response.status_code if response else 'No response'}")

        # UPDATE
        update_data = {**project_data, "project_name": f"Updated Test Project {int(time.time())}"}
        response = self.make_request('PUT', f'/projects/{self.test_project_id}', update_data)
        if response and response.status_code == 200:
            self.log_test("Project Update", True, "Project updated successfully")
        else:
            self.log_test("Project Update", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_building_crud(self):
        """Test building CRUD operations"""
        if not self.test_project_id:
            self.log_test("Building CRUD", False, error_detail="No test project available")
            return False

        building_data = {
            "project_id": self.test_project_id,
            "building_name": "Tower A",
            "floors": 10,
            "units": 40,
            "estimated_cost": 50000000
        }
        
        # CREATE
        response = self.make_request('POST', '/buildings', building_data)
        if response and response.status_code == 200:
            data = response.json()
            self.test_building_id = data['building_id']
            self.log_test("Building Creation", True, f"Building created with ID: {self.test_building_id}")
        else:
            self.log_test("Building Creation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
            return False

        # READ
        response = self.make_request('GET', '/buildings', params={'project_id': self.test_project_id})
        if response and response.status_code == 200:
            buildings = response.json()
            if len(buildings) > 0:
                self.log_test("Building List", True, f"Retrieved {len(buildings)} buildings")
            else:
                self.log_test("Building List", False, error_detail="No buildings found")
        else:
            self.log_test("Building List", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_construction_progress(self):
        """Test construction progress functionality"""
        if not self.test_building_id:
            self.log_test("Construction Progress", False, error_detail="No test building available")
            return False

        # Get default activities
        response = self.make_request('GET', '/construction-progress/default-activities')
        if response and response.status_code == 200:
            activities = response.json()
            self.log_test("Default Activities", True, f"Retrieved {len(activities)} default activities")
        else:
            self.log_test("Default Activities", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
            return False

        # Create progress entry
        progress_data = {
            "building_id": self.test_building_id,
            "quarter": "Q1",
            "year": 2024,
            "activities": [
                {"activity_name": "Excavation", "weightage": 5, "completion_percentage": 100},
                {"activity_name": "Foundation", "weightage": 10, "completion_percentage": 75}
            ]
        }
        
        response = self.make_request('POST', '/construction-progress', progress_data)
        if response and response.status_code == 200:
            self.log_test("Construction Progress Creation", True, "Progress entry created")
        else:
            self.log_test("Construction Progress Creation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")

        # Get progress
        response = self.make_request('GET', '/construction-progress', params={
            'project_id': self.test_project_id,
            'quarter': 'Q1',
            'year': 2024
        })
        if response and response.status_code == 200:
            progress_list = response.json()
            self.log_test("Construction Progress Read", True, f"Retrieved {len(progress_list)} progress entries")
        else:
            self.log_test("Construction Progress Read", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_project_costs(self):
        """Test project costs functionality"""
        if not self.test_project_id:
            self.log_test("Project Costs", False, error_detail="No test project available")
            return False

        cost_data = {
            "project_id": self.test_project_id,
            "quarter": "Q1",
            "year": 2024,
            "land_acquisition_cost": 10000000,
            "construction_cost": 30000000,
            "estimated_land_cost": 12000000,
            "estimated_development_cost": 35000000
        }
        
        # CREATE
        response = self.make_request('POST', '/project-costs', cost_data)
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Project Costs Creation", True, f"Cost entry created with calculated totals")
        else:
            self.log_test("Project Costs Creation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")

        # READ
        response = self.make_request('GET', '/project-costs', params={
            'project_id': self.test_project_id,
            'quarter': 'Q1',
            'year': 2024
        })
        if response and response.status_code == 200:
            costs = response.json()
            if len(costs) > 0:
                self.log_test("Project Costs Read", True, f"Retrieved cost data")
            else:
                self.log_test("Project Costs Read", False, error_detail="No cost data found")
        else:
            self.log_test("Project Costs Read", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_unit_sales(self):
        """Test unit sales functionality"""
        if not self.test_project_id or not self.test_building_id:
            self.log_test("Unit Sales", False, error_detail="No test project/building available")
            return False

        sale_data = {
            "project_id": self.test_project_id,
            "unit_number": "A-101", 
            "building_id": self.test_building_id,
            "building_name": "Tower A",
            "carpet_area": 850,
            "sale_value": 7500000,
            "amount_received": 5000000,
            "buyer_name": "Test Buyer",
            "agreement_date": "2024-01-15"
        }
        
        # CREATE
        response = self.make_request('POST', '/unit-sales', sale_data)
        if response and response.status_code == 200:
            data = response.json()
            sale_id = data['sale_id']
            self.log_test("Unit Sales Creation", True, f"Sale created with ID: {sale_id}")
        else:
            self.log_test("Unit Sales Creation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
            return False

        # READ
        response = self.make_request('GET', '/unit-sales', params={'project_id': self.test_project_id})
        if response and response.status_code == 200:
            sales = response.json()
            if len(sales) > 0:
                self.log_test("Unit Sales Read", True, f"Retrieved {len(sales)} sales records")
            else:
                self.log_test("Unit Sales Read", False, error_detail="No sales data found")
        else:
            self.log_test("Unit Sales Read", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_dashboard(self):
        """Test dashboard functionality"""
        if not self.test_project_id:
            self.log_test("Dashboard", False, error_detail="No test project available")
            return False

        response = self.make_request('GET', f'/dashboard/{self.test_project_id}')
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['project_completion_percentage', 'total_estimated_cost', 'cost_incurred', 'receivables']
            if all(field in data for field in required_fields):
                self.log_test("Dashboard", True, "Dashboard data retrieved with all required fields")
            else:
                self.log_test("Dashboard", False, error_detail="Missing required dashboard fields")
        else:
            self.log_test("Dashboard", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_report_generation(self):
        """Test report generation functionality"""
        if not self.test_project_id:
            self.log_test("Report Generation", False, error_detail="No test project available")
            return False

        response = self.make_request('GET', f'/generate-report/{self.test_project_id}/form-1', params={
            'quarter': 'Q1',
            'year': 2024
        })
        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                self.log_test("Report Generation", True, "Report data generated successfully")
            else:
                self.log_test("Report Generation", False, error_detail="No report data returned")
        else:
            self.log_test("Report Generation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_data_validation(self):
        """Test data validation functionality"""
        if not self.test_project_id:
            self.log_test("Data Validation", False, error_detail="No test project available")
            return False

        response = self.make_request('GET', f'/validate/{self.test_project_id}')
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['is_valid', 'errors', 'warnings', 'summary']
            if all(field in data for field in required_fields):
                self.log_test("Data Validation", True, f"Validation completed - Valid: {data['is_valid']}")
            else:
                self.log_test("Data Validation", False, error_detail="Missing validation response fields")
        else:
            self.log_test("Data Validation", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_excel_template(self):
        """Test Excel template download"""
        response = self.make_request('GET', '/import/sales-template')
        if response and response.status_code == 200:
            if response.headers.get('content-type', '').startswith('application/vnd.openxmlformats'):
                self.log_test("Excel Template Download", True, "Template downloaded successfully")
            else:
                self.log_test("Excel Template Download", False, error_detail="Invalid content type")
        else:
            self.log_test("Excel Template Download", False, error_detail=f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def cleanup(self):
        """Clean up test data"""
        if self.test_project_id:
            response = self.make_request('DELETE', f'/projects/{self.test_project_id}')
            if response and response.status_code == 200:
                print("✅ Test data cleaned up successfully")
            else:
                print("⚠️ Failed to clean up test project")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting RERA Compliance Manager Backend Tests")
        print("=" * 60)
        
        # Basic connectivity and health
        if not self.test_health_check():
            print("❌ API Health check failed - stopping tests")
            return False
        
        # Authentication tests
        if not self.test_user_registration():
            print("❌ User registration failed - stopping tests")
            return False
        
        self.test_user_login()
        self.test_get_user_profile()
        
        # Core functionality tests
        if self.test_project_crud():
            self.test_building_crud()
            self.test_construction_progress()
            self.test_project_costs()
            self.test_unit_sales()
            self.test_dashboard()
            self.test_report_generation()
            self.test_data_validation()
        
        # Utility tests
        self.test_excel_template()
        
        # Clean up
        self.cleanup()
        
        # Final results
        print("=" * 60)
        print(f"📊 Tests Complete: {self.tests_passed}/{self.tests_run} passed")
        if self.errors:
            print(f"❌ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"   - {error['test']}: {error['error']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = RERABackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())