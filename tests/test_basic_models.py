"""
Tests for Basic Pydantic Models

This module contains comprehensive tests for basic Pydantic functionality.
Run with: python -m pytest tests/test_basic        # Too many tags
        with py        # Street too short
        with pytest.raises(ValidationError):
            Address(
                street="123",
                city="City",
                country="Country",
                postal_code="12345"
            )
        
        # Invalid postal code format (use shorter string to test pattern)
        with pytest.raises(ValidationError):
            Address(
                street="123 Main Street",
                city="City",
                country="Country",
                postal_code="12345@#$"
            )ionError):
            User(
                id=1,
                username="test",
                email="test@example.com",
                tags=[f"tag{i}" for i in range(15)]  # More than 10 tags
            )py -v
"""

import pytest
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import List, Optional
from enum import Enum


# Test models (replicated here for testing)
class Status(str, Enum):
    """Enum for user status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class User(BaseModel):
    """Basic user model for testing"""
    
    id: int = Field(..., gt=0, description="User ID must be positive")
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3-50 characters")
    full_name: Optional[str] = Field(None, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = True
    status: Status = Status.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list, max_length=10)


class Address(BaseModel):
    """Address model for testing"""
    
    street: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r'^[\d\w\s-]+$', max_length=20)


class UserProfile(BaseModel):
    """Extended user profile for testing"""
    
    user: User
    address: Optional[Address] = None
    bio: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, pattern=r'^https?://.+')


class TestUser:
    """Test cases for the User model"""
    
    def test_create_valid_user(self):
        """Test creating a user with valid data"""
        user_data = {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "full_name": "Test User",
            "age": 25
        }
        
        user = User(**user_data)
        
        assert user.id == 1
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.age == 25
        assert user.is_active is True  # Default value
        assert user.status == Status.ACTIVE  # Default value
        assert isinstance(user.created_at, datetime)
        assert user.tags == []  # Default empty list
    
    def test_user_with_minimal_data(self):
        """Test creating a user with only required fields"""
        user_data = {
            "id": 2,
            "username": "minimal",
            "email": "minimal@test.com"
        }
        
        user = User(**user_data)
        
        assert user.id == 2
        assert user.username == "minimal"
        assert user.email == "minimal@test.com"
        assert user.full_name is None  # Optional field
        assert user.age is None  # Optional field
        assert user.is_active is True
    
    def test_user_validation_errors(self):
        """Test various validation errors"""
        
        # Invalid ID (negative)
        with pytest.raises(ValidationError):
            User(id=-1, username="test", email="test@example.com")
        
        # Username too short
        with pytest.raises(ValidationError):
            User(id=1, username="ab", email="test@example.com")
        
        # Username too long
        with pytest.raises(ValidationError):
            User(id=1, username="a" * 51, email="test@example.com")
        
        # Invalid email format
        with pytest.raises(ValidationError):
            User(id=1, username="test", email="not-an-email")
        
        # Age out of range
        with pytest.raises(ValidationError):
            User(id=1, username="test", email="test@example.com", age=200)
        
        # Negative age
        with pytest.raises(ValidationError):
            User(id=1, username="test", email="test@example.com", age=-5)
    
    def test_user_json_serialization(self):
        """Test JSON serialization and deserialization"""
        user_data = {
            "id": 1,
            "username": "json_test",
            "email": "json@test.com",
            "full_name": "JSON Test User",
            "age": 30,
            "tags": ["developer", "python"]
        }
        
        user = User(**user_data)
        
        # Test serialization
        json_str = user.model_dump_json()
        assert "json_test" in json_str
        assert "json@test.com" in json_str
        
        # Test deserialization
        user_from_json = User.model_validate_json(json_str)
        assert user_from_json.username == user.username
        assert user_from_json.email == user.email
    
    def test_user_tags_validation(self):
        """Test tags field validation"""
        # Valid tags
        user_data = {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "tags": ["python", "fastapi", "pydantic"]
        }
        
        user = User(**user_data)
        assert len(user.tags) == 3
        
        # Too many tags
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                username="test",
                email="test@example.com",
                tags=[f"tag{i}" for i in range(15)]  # More than 10 tags
            )
        assert "at most 10 items" in str(exc_info.value)


class TestAddress:
    """Test cases for the Address model"""
    
    def test_create_valid_address(self):
        """Test creating an address with valid data"""
        address_data = {
            "street": "123 Main Street",
            "city": "New York",
            "country": "USA",
            "postal_code": "10001"
        }
        
        address = Address(**address_data)
        
        assert address.street == "123 Main Street"
        assert address.city == "New York"
        assert address.country == "USA"
        assert address.postal_code == "10001"
    
    def test_address_validation_errors(self):
        """Test address validation errors"""
        
        # Street too short
        with pytest.raises(ValidationError):
            Address(
                street="123",
                city="City",
                country="Country",
                postal_code="12345"
            )
        
        # Invalid postal code format (use shorter string to test pattern)
        with pytest.raises(ValidationError):
            Address(
                street="123 Main Street",
                city="City",
                country="Country",
                postal_code="12345@#$"
            )


class TestUserProfile:
    """Test cases for the UserProfile model"""
    
    def test_create_valid_user_profile(self):
        """Test creating a user profile with nested models"""
        profile_data = {
            "user": {
                "id": 1,
                "username": "profile_test",
                "email": "profile@test.com",
                "full_name": "Profile Test User",
                "age": 28
            },
            "address": {
                "street": "456 Test Avenue",
                "city": "Test City",
                "country": "Test Country",
                "postal_code": "12345"
            },
            "bio": "Test bio for user profile",
            "website": "https://example.com"
        }
        
        profile = UserProfile(**profile_data)
        
        assert profile.user.username == "profile_test"
        assert profile.address.city == "Test City"
        assert profile.bio == "Test bio for user profile"
        assert profile.website == "https://example.com"
    
    def test_user_profile_with_minimal_data(self):
        """Test creating a user profile with only required fields"""
        profile_data = {
            "user": {
                "id": 1,
                "username": "minimal_profile",
                "email": "minimal@test.com"
            }
        }
        
        profile = UserProfile(**profile_data)
        
        assert profile.user.username == "minimal_profile"
        assert profile.address is None
        assert profile.bio is None
        assert profile.website is None
    
    def test_user_profile_validation_errors(self):
        """Test user profile validation errors"""
        
        # Invalid nested user data
        with pytest.raises(ValidationError):
            UserProfile(user={
                "id": -1,  # Invalid ID
                "username": "test",
                "email": "test@example.com"
            })
        
        # Invalid nested address data
        with pytest.raises(ValidationError):
            UserProfile(
                user={
                    "id": 1,
                    "username": "test",
                    "email": "test@example.com"
                },
                address={
                    "street": "123",  # Too short
                    "city": "City",
                    "country": "Country",
                    "postal_code": "12345"
                }
            )
        
        # Invalid website URL
        with pytest.raises(ValidationError):
            UserProfile(
                user={
                    "id": 1,
                    "username": "test",
                    "email": "test@example.com"
                },
                website="not-a-valid-url"
            )


class TestDataValidation:
    """Test various data validation scenarios"""
    
    def test_type_coercion(self):
        """Test automatic type conversion"""
        # String ID should be converted to int
        user = User(
            id="123",  # String that can be converted to int
            username="test",
            email="test@example.com",
            age="25"  # String that can be converted to int
        )
        
        assert user.id == 123
        assert isinstance(user.id, int)
        assert user.age == 25
        assert isinstance(user.age, int)
    
    def test_enum_validation(self):
        """Test enum field validation"""
        # Valid enum value
        user = User(
            id=1,
            username="test",
            email="test@example.com",
            status="active"
        )
        assert user.status == Status.ACTIVE
        
        # Invalid enum value
        with pytest.raises(ValidationError):
            User(
                id=1,
                username="test",
                email="test@example.com",
                status="invalid_status"
            )
    
    def test_optional_fields(self):
        """Test handling of optional fields"""
        # All optional fields as None
        user = User(
            id=1,
            username="test",
            email="test@example.com",
            full_name=None,
            age=None
        )
        
        assert user.full_name is None
        assert user.age is None
        
        # Optional fields with values
        user = User(
            id=1,
            username="test",
            email="test@example.com",
            full_name="Test User",
            age=30
        )
        
        assert user.full_name == "Test User"
        assert user.age == 30
    
    def test_default_values(self):
        """Test default field values"""
        user = User(
            id=1,
            username="test",
            email="test@example.com"
        )
        
        # Test default values
        assert user.is_active is True
        assert user.status == Status.ACTIVE
        assert user.tags == []
        assert isinstance(user.created_at, datetime)
    
    def test_field_constraints(self):
        """Test various field constraints"""
        # Test string length constraints
        with pytest.raises(ValidationError):
            User(id=1, username="ab", email="test@example.com")  # Too short
        
        with pytest.raises(ValidationError):
            User(id=1, username="a" * 51, email="test@example.com")  # Too long
        
        # Test numeric constraints
        with pytest.raises(ValidationError):
            User(id=0, username="test", email="test@example.com")  # ID must be > 0
        
        with pytest.raises(ValidationError):
            User(id=1, username="test", email="test@example.com", age=151)  # Age too high


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
