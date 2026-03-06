"""
Test Enhanced Buildings Module
- Building types API
- Single building creation with enhanced fields
- Bulk building creation
- Building CRUD operations with enhanced fields
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_EMAIL = f"test_buildings_{uuid.uuid4().hex[:8]}@test.com"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "Test Buildings User"


class TestSetup:
    """Setup fixtures for test session"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Register user and get auth token"""
        # Register a new test user
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "role": "developer"
        })
        
        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 400 and "already registered" in response.text:
            # Login if already exists
            login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            if login_resp.status_code == 200:
                return login_resp.json()["access_token"]
        
        pytest.skip(f"Could not authenticate: {response.text}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.fixture(scope="class")
    def test_project_id(self, session, auth_headers):
        """Create a test project and return its ID"""
        response = session.post(
            f"{BASE_URL}/api/projects",
            headers=auth_headers,
            json={
                "project_name": f"TEST_BuildingProject_{uuid.uuid4().hex[:6]}",
                "state": "GOA",
                "rera_number": f"GOA/TEST/{uuid.uuid4().hex[:8]}",
                "promoter_name": "Test Promoter",
                "promoter_address": "Test Address",
                "project_address": "Test Project Address"
            }
        )
        assert response.status_code == 200, f"Failed to create project: {response.text}"
        return response.json()["project_id"]


class TestBuildingTypesAPI(TestSetup):
    """Test building types endpoint"""
    
    def test_get_building_types_returns_correct_types(self, session):
        """GET /api/buildings/types returns correct building types"""
        response = session.get(f"{BASE_URL}/api/buildings/types")
        
        # Status code assertion
        assert response.status_code == 200
        
        # Data structure assertions
        data = response.json()
        assert "types" in data
        assert "parking_options" in data
        assert isinstance(data["types"], list)
        assert len(data["types"]) == 4
        
        # Verify all expected types exist
        type_values = [t["value"] for t in data["types"]]
        assert "residential_tower" in type_values
        assert "mixed_tower" in type_values
        assert "row_house" in type_values
        assert "bungalow" in type_values
    
    def test_building_types_have_correct_config(self, session):
        """Verify building types have correct configuration"""
        response = session.get(f"{BASE_URL}/api/buildings/types")
        data = response.json()
        
        for building_type in data["types"]:
            # Each type should have required fields
            assert "value" in building_type
            assert "label" in building_type
            assert "has_commercial" in building_type
            assert "has_apartments_per_floor" in building_type
            assert "is_single_unit" in building_type
            
        # Verify specific type configurations
        mixed_tower = next(t for t in data["types"] if t["value"] == "mixed_tower")
        assert mixed_tower["has_commercial"] == True
        assert mixed_tower["has_apartments_per_floor"] == True
        
        row_house = next(t for t in data["types"] if t["value"] == "row_house")
        assert row_house["has_commercial"] == False
        assert row_house["is_single_unit"] == True
    
    def test_parking_options_exist(self, session):
        """Verify parking options are returned"""
        response = session.get(f"{BASE_URL}/api/buildings/types")
        data = response.json()
        
        assert len(data["parking_options"]) == 3
        parking_fields = [p["field"] for p in data["parking_options"]]
        assert "parking_basement" in parking_fields
        assert "parking_stilt_ground" in parking_fields
        assert "parking_upper_level" in parking_fields


class TestSingleBuildingCreation(TestSetup):
    """Test single building creation with enhanced fields"""
    
    def test_create_residential_tower(self, session, auth_headers, test_project_id):
        """Create a residential tower with all enhanced fields"""
        building_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Tower_A",
            "building_type": "residential_tower",
            "parking_basement": 2,
            "parking_stilt_ground": 1,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 10,
            "apartments_per_floor": 4,
            "estimated_cost": 5000000
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=building_data
        )
        
        # Status assertion
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        # Data assertions
        data = response.json()
        assert data["building_name"] == "TEST_Tower_A"
        assert data["building_type"] == "residential_tower"
        assert data["parking_basement"] == 2
        assert data["parking_stilt_ground"] == 1
        assert data["parking_upper_level"] == 0
        assert data["residential_floors"] == 10
        assert data["apartments_per_floor"] == 4
        assert data["estimated_cost"] == 5000000
        assert "building_id" in data
        
        # Verify calculated fields
        assert data["total_parking_floors"] == 3  # 2+1+0
        assert data["units"] == 40  # 10 floors * 4 apartments
        
        # Verify persistence - GET the building
        get_response = session.get(
            f"{BASE_URL}/api/buildings/{data['building_id']}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["building_name"] == "TEST_Tower_A"
        assert fetched["parking_basement"] == 2
    
    def test_create_mixed_tower(self, session, auth_headers, test_project_id):
        """Create a mixed tower with commercial floors"""
        building_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Mixed_Tower",
            "building_type": "mixed_tower",
            "parking_basement": 1,
            "parking_stilt_ground": 0,
            "parking_upper_level": 2,
            "commercial_floors": 3,
            "residential_floors": 8,
            "apartments_per_floor": 6,
            "estimated_cost": 8000000
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=building_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["building_type"] == "mixed_tower"
        assert data["commercial_floors"] == 3
        assert data["residential_floors"] == 8
        assert data["units"] == 48  # 8 residential floors * 6 apartments
    
    def test_create_row_house(self, session, auth_headers, test_project_id):
        """Create a row house (single unit)"""
        building_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Row_House_1",
            "building_type": "row_house",
            "parking_basement": 0,
            "parking_stilt_ground": 1,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 2,
            "apartments_per_floor": 0,
            "estimated_cost": 1500000
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=building_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["building_type"] == "row_house"
        assert data["units"] == 1  # Single unit for row house
    
    def test_create_bungalow(self, session, auth_headers, test_project_id):
        """Create a bungalow (single unit)"""
        building_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Bungalow_1",
            "building_type": "bungalow",
            "parking_basement": 1,
            "parking_stilt_ground": 0,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 3,
            "apartments_per_floor": 0,
            "estimated_cost": 3000000
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=building_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["building_type"] == "bungalow"
        assert data["units"] == 1  # Single unit for bungalow


class TestBulkBuildingCreation(TestSetup):
    """Test bulk building creation"""
    
    def test_bulk_create_buildings(self, session, auth_headers, test_project_id):
        """POST /api/buildings/bulk creates multiple buildings"""
        bulk_data = {
            "project_id": test_project_id,
            "building_names": ["TEST_Bulk_A", "TEST_Bulk_B", "TEST_Bulk_C"],
            "template": {
                "building_name": "placeholder",  # Will be overridden
                "building_type": "residential_tower",
                "parking_basement": 1,
                "parking_stilt_ground": 1,
                "parking_upper_level": 0,
                "commercial_floors": 0,
                "residential_floors": 12,
                "apartments_per_floor": 4,
                "estimated_cost": 6000000
            }
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings/bulk",
            headers=auth_headers,
            json=bulk_data
        )
        
        # Status assertion
        assert response.status_code == 200, f"Bulk create failed: {response.text}"
        
        # Data assertions
        data = response.json()
        assert data["created"] == 3
        assert len(data["buildings"]) == 3
        assert len(data["errors"]) == 0
        
        # Verify buildings were created with correct names
        building_names = [b["building_name"] for b in data["buildings"]]
        assert "TEST_Bulk_A" in building_names
        assert "TEST_Bulk_B" in building_names
        assert "TEST_Bulk_C" in building_names
        
        # Verify persistence - GET buildings list
        list_response = session.get(
            f"{BASE_URL}/api/buildings?project_id={test_project_id}",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        buildings = list_response.json()
        bulk_buildings = [b for b in buildings if b["building_name"].startswith("TEST_Bulk_")]
        assert len(bulk_buildings) == 3
        
        # Verify all have correct configuration
        for building in bulk_buildings:
            assert building["parking_basement"] == 1
            assert building["residential_floors"] == 12
            assert building["apartments_per_floor"] == 4
    
    def test_bulk_create_empty_names_fails(self, session, auth_headers, test_project_id):
        """Bulk create with empty names should fail gracefully"""
        bulk_data = {
            "project_id": test_project_id,
            "building_names": [],
            "template": {
                "building_name": "placeholder",
                "building_type": "residential_tower",
                "parking_basement": 0,
                "parking_stilt_ground": 0,
                "parking_upper_level": 0,
                "commercial_floors": 0,
                "residential_floors": 5,
                "apartments_per_floor": 2,
                "estimated_cost": 1000000
            }
        }
        
        response = session.post(
            f"{BASE_URL}/api/buildings/bulk",
            headers=auth_headers,
            json=bulk_data
        )
        
        # Should create 0 buildings
        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 0


class TestBuildingUpdate(TestSetup):
    """Test building update with enhanced fields"""
    
    def test_update_building_enhanced_fields(self, session, auth_headers, test_project_id):
        """Update building with enhanced fields"""
        # First create a building
        create_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Update_Building",
            "building_type": "residential_tower",
            "parking_basement": 1,
            "parking_stilt_ground": 0,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 5,
            "apartments_per_floor": 2,
            "estimated_cost": 2000000
        }
        
        create_resp = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=create_data
        )
        assert create_resp.status_code == 200
        building_id = create_resp.json()["building_id"]
        
        # Update the building
        update_data = {
            "building_name": "TEST_Update_Building_Modified",
            "building_type": "mixed_tower",
            "parking_basement": 2,
            "parking_stilt_ground": 1,
            "parking_upper_level": 1,
            "commercial_floors": 2,
            "residential_floors": 8,
            "apartments_per_floor": 6,
            "estimated_cost": 5000000
        }
        
        update_resp = session.put(
            f"{BASE_URL}/api/buildings/{building_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["building_name"] == "TEST_Update_Building_Modified"
        assert updated["building_type"] == "mixed_tower"
        assert updated["parking_basement"] == 2
        assert updated["parking_stilt_ground"] == 1
        assert updated["parking_upper_level"] == 1
        assert updated["commercial_floors"] == 2
        assert updated["residential_floors"] == 8
        assert updated["apartments_per_floor"] == 6
        
        # Verify recalculated fields
        assert updated["total_parking_floors"] == 4  # 2+1+1
        assert updated["units"] == 48  # 8 * 6
        
        # Verify persistence
        get_resp = session.get(
            f"{BASE_URL}/api/buildings/{building_id}",
            headers=auth_headers
        )
        assert get_resp.status_code == 200
        fetched = get_resp.json()
        assert fetched["building_type"] == "mixed_tower"
        assert fetched["commercial_floors"] == 2


class TestBuildingDelete(TestSetup):
    """Test building deletion"""
    
    def test_delete_building(self, session, auth_headers, test_project_id):
        """Delete building and verify removal"""
        # Create a building to delete
        create_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Delete_Building",
            "building_type": "bungalow",
            "parking_basement": 0,
            "parking_stilt_ground": 0,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 2,
            "apartments_per_floor": 0,
            "estimated_cost": 1000000
        }
        
        create_resp = session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=create_data
        )
        assert create_resp.status_code == 200
        building_id = create_resp.json()["building_id"]
        
        # Delete the building
        delete_resp = session.delete(
            f"{BASE_URL}/api/buildings/{building_id}",
            headers=auth_headers
        )
        assert delete_resp.status_code == 200
        
        # Verify deletion - GET should return 404
        get_resp = session.get(
            f"{BASE_URL}/api/buildings/{building_id}",
            headers=auth_headers
        )
        assert get_resp.status_code == 404


class TestBuildingsTableDisplay(TestSetup):
    """Test buildings list returns correct data for table display"""
    
    def test_buildings_list_has_display_fields(self, session, auth_headers, test_project_id):
        """Verify buildings list includes all display fields"""
        # First create a building
        create_data = {
            "project_id": test_project_id,
            "building_name": "TEST_Display_Building",
            "building_type": "residential_tower",
            "parking_basement": 2,
            "parking_stilt_ground": 1,
            "parking_upper_level": 0,
            "commercial_floors": 0,
            "residential_floors": 10,
            "apartments_per_floor": 4,
            "estimated_cost": 5000000
        }
        
        session.post(
            f"{BASE_URL}/api/buildings",
            headers=auth_headers,
            json=create_data
        )
        
        # Get buildings list
        list_resp = session.get(
            f"{BASE_URL}/api/buildings?project_id={test_project_id}",
            headers=auth_headers
        )
        
        assert list_resp.status_code == 200
        buildings = list_resp.json()
        
        # Find our test building
        test_building = next((b for b in buildings if b["building_name"] == "TEST_Display_Building"), None)
        assert test_building is not None
        
        # Verify all display fields exist
        assert "building_name" in test_building
        assert "building_type" in test_building
        assert "parking_basement" in test_building
        assert "parking_stilt_ground" in test_building
        assert "parking_upper_level" in test_building
        assert "floors" in test_building or "residential_floors" in test_building
        assert "units" in test_building
        assert "estimated_cost" in test_building
        assert "total_parking_floors" in test_building


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
