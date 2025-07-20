"""
Basic Pydantic Models

This module demonstrates fundamental Pydantic concepts:
- Creating basic models
- Field types and validation
- Default values
- Optional fields
"""

from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Status(str, Enum):
    """Enum for user status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class User(BaseModel):
    """Basic user model with various field types"""
    
    id: int = Field(..., gt=0, description="User ID must be positive")
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3-50 characters")
    full_name: Optional[str] = Field(None, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = True
    status: Status = Status.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "full_name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "is_active": True,
                "status": "active",
                "tags": ["developer", "python"]
            }
        }


class Address(BaseModel):
    """Address model demonstrating nested models"""
    
    street: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r'^[\d\w\s-]+$', max_length=20)


class UserProfile(BaseModel):
    """Extended user profile with nested models"""
    
    user: User
    address: Optional[Address] = None
    bio: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, pattern=r'^https?://.+')


def create_user_examples():
    """Demonstrate creating and validating user models"""
    
    print("=== Basic User Model Examples ===\n")
    
    # Valid user data
    user_data = {
        "id": 1,
        "username": "alice_smith",
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "age": 25,
        "tags": ["designer", "ui/ux"]
    }
    
    try:
        user = User(**user_data)
        print(f"✅ Created user: {user.username}")
        print(f"   Full name: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Status: {user.status}")
        print(f"   Created at: {user.created_at}")
        print(f"   Tags: {user.tags}\n")
    except ValidationError as e:
        print(f"❌ Validation error: {e}\n")
    
    # User with minimal data (using defaults)
    minimal_user_data = {
        "id": 2,
        "username": "bob",
        "email": "bob@test.com"
    }
    
    try:
        minimal_user = User(**minimal_user_data)
        print(f"✅ Created minimal user: {minimal_user.username}")
        print(f"   Is active: {minimal_user.is_active}")
        print(f"   Status: {minimal_user.status}")
        print(f"   Tags: {minimal_user.tags}\n")
    except ValidationError as e:
        print(f"❌ Validation error: {e}\n")


def demonstrate_validation_errors():
    """Show various validation errors"""
    
    print("=== Validation Error Examples ===\n")
    
    invalid_cases = [
        {
            "name": "Invalid ID (negative)",
            "data": {"id": -1, "username": "test", "email": "test@example.com"}
        },
        {
            "name": "Username too short",
            "data": {"id": 1, "username": "ab", "email": "test@example.com"}
        },
        {
            "name": "Invalid email format",
            "data": {"id": 1, "username": "test", "email": "not-an-email"}
        },
        {
            "name": "Age out of range",
            "data": {"id": 1, "username": "test", "email": "test@example.com", "age": 200}
        }
    ]
    
    for case in invalid_cases:
        try:
            User(**case["data"])
            print(f"❌ Expected validation error for: {case['name']}")
        except ValidationError as e:
            print(f"✅ {case['name']}: {e.errors()[0]['msg']}")
    
    print()


def nested_model_example():
    """Demonstrate nested models"""
    
    print("=== Nested Model Example ===\n")
    
    profile_data = {
        "user": {
            "id": 1,
            "username": "charlie",
            "full_name": "Charlie Brown",
            "email": "charlie@example.com",
            "age": 35,
            "tags": ["manager", "leader"]
        },
        "address": {
            "street": "123 Main Street",
            "city": "New York",
            "country": "USA",
            "postal_code": "10001"
        },
        "bio": "Experienced project manager with a passion for technology.",
        "website": "https://charlie-brown.dev"
    }
    
    try:
        profile = UserProfile(**profile_data)
        print(f"✅ Created profile for: {profile.user.full_name}")
        print(f"   Username: {profile.user.username}")
        print(f"   Address: {profile.address.city}, {profile.address.country}")
        print(f"   Website: {profile.website}")
        print(f"   Bio: {profile.bio[:50]}...")
        
        # Convert to JSON
        print(f"\n📄 JSON representation:")
        print(profile.model_dump_json(indent=2))
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")


if __name__ == "__main__":
    create_user_examples()
    demonstrate_validation_errors()
    nested_model_example()
