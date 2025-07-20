"""
Exercise 1: User Profile Management System

Your task is to create a comprehensive user profile management system using Pydantic.
This exercise will test your understanding of:
- Basic model creation
- Field validation and constraints
- Custom validators
- Nested models
- Error handling

INSTRUCTIONS:
1. Complete the UserProfile model with proper validation
2. Implement the ProfileManager class methods
3. Add appropriate error handling
4. Test your implementation with the provided test cases

REQUIREMENTS:
- All fields should have appropriate validation
- Email should be validated for proper format
- Age should be between 13 and 120
- Username should be 3-30 characters, alphanumeric + underscore
- Bio should not exceed 500 characters
- Social media URLs should be valid URLs
- Skills should be unique and lowercased
- Address should be complete (all fields required)

TODO: Complete the implementation below
"""

from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Union
from datetime import datetime, date
from enum import Enum
import re


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Address(BaseModel):
    """Address model - TODO: Add proper field validation"""
    
    # TODO: Add fields with appropriate validation:
    # - street (required, 5-200 characters)
    # - city (required, 2-100 characters)
    # - state (optional, 2-100 characters)
    # - country (required, 2-100 characters)
    # - postal_code (required, valid format)
    pass


class SocialMedia(BaseModel):
    """Social media links - TODO: Add URL validation"""
    
    # TODO: Add optional fields for social media platforms:
    # - linkedin (optional, valid URL)
    # - twitter (optional, valid URL)
    # - github (optional, valid URL)
    # - website (optional, valid URL)
    pass


class UserProfile(BaseModel):
    """
    User profile model
    TODO: Complete this model with all required fields and validation
    """
    
    # TODO: Add the following fields with proper validation:
    # - user_id (required, positive integer)
    # - username (required, 3-30 chars, alphanumeric + underscore)
    # - email (required, valid email format)
    # - first_name (required, 1-50 characters)
    # - last_name (required, 1-50 characters)
    # - age (required, 13-120)
    # - gender (optional, use Gender enum)
    # - date_of_birth (optional, date type)
    # - bio (optional, max 500 characters)
    # - skills (list of strings, unique, lowercase, max 20 items)
    # - address (optional, Address model)
    # - social_media (optional, SocialMedia model)
    # - is_active (boolean, default True)
    # - created_at (datetime, auto-generated)
    # - updated_at (optional datetime)
    pass
    
    # TODO: Add custom validators:
    # - username: only alphanumeric and underscore allowed
    # - skills: should be unique, lowercase, no empty strings
    # - bio: strip whitespace, no profanity (basic check)
    # - date_of_birth: should not be in the future, should match age
    
    # TODO: Add root validator to ensure date_of_birth matches age (if both provided)


class ProfileManager:
    """
    Profile manager class to handle user profiles
    TODO: Complete the implementation
    """
    
    def __init__(self):
        self.profiles: Dict[int, UserProfile] = {}
        self.username_index: Dict[str, int] = {}
    
    def create_profile(self, profile_data: Dict) -> UserProfile:
        """
        Create a new user profile
        TODO: Implement this method
        
        Should:
        1. Validate the profile data using UserProfile model
        2. Check if user_id or username already exists
        3. Store the profile
        4. Return the created profile
        
        Raises:
        - ValidationError: if data is invalid
        - ValueError: if user_id or username already exists
        """
        pass
    
    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Get a profile by user_id
        TODO: Implement this method
        """
        pass
    
    def get_profile_by_username(self, username: str) -> Optional[UserProfile]:
        """
        Get a profile by username
        TODO: Implement this method
        """
        pass
    
    def update_profile(self, user_id: int, updates: Dict) -> UserProfile:
        """
        Update an existing profile
        TODO: Implement this method
        
        Should:
        1. Check if profile exists
        2. Apply updates while maintaining validation
        3. Update the updated_at timestamp
        4. Return updated profile
        
        Raises:
        - ValueError: if profile doesn't exist
        - ValidationError: if updates are invalid
        """
        pass
    
    def delete_profile(self, user_id: int) -> bool:
        """
        Delete a profile
        TODO: Implement this method
        
        Returns True if deleted, False if not found
        """
        pass
    
    def search_profiles(self, **criteria) -> List[UserProfile]:
        """
        Search profiles by criteria
        TODO: Implement basic search functionality
        
        Should support searching by:
        - age range
        - skills
        - city
        - is_active status
        """
        pass


def test_user_profile():
    """
    Test function to validate your implementation
    TODO: Run this after completing your implementation
    """
    
    print("=== Testing User Profile System ===\n")
    
    manager = ProfileManager()
    
    # Test data
    valid_profile_data = {
        "user_id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "gender": "male",
        "bio": "Software developer passionate about Python",
        "skills": ["python", "javascript", "sql", "git"],
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "country": "USA",
            "postal_code": "10001"
        },
        "social_media": {
            "github": "https://github.com/johndoe",
            "linkedin": "https://linkedin.com/in/johndoe"
        }
    }
    
    try:
        # Test profile creation
        print("1. Testing profile creation...")
        profile = manager.create_profile(valid_profile_data)
        print(f"   ✅ Created profile for {profile.first_name} {profile.last_name}")
        
        # Test profile retrieval
        print("2. Testing profile retrieval...")
        retrieved = manager.get_profile(1)
        print(f"   ✅ Retrieved profile: {retrieved.username}")
        
        # Test profile update
        print("3. Testing profile update...")
        updated = manager.update_profile(1, {"bio": "Updated bio", "age": 26})
        print(f"   ✅ Updated profile: {updated.bio}")
        
        # Test validation errors
        print("4. Testing validation errors...")
        invalid_data = valid_profile_data.copy()
        invalid_data["age"] = 5  # Too young
        
        try:
            manager.create_profile(invalid_data)
            print("   ❌ Should have failed validation")
        except ValidationError:
            print("   ✅ Correctly caught validation error")
        
        print("\n🎉 All tests passed! Your implementation is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Please complete your implementation and try again.")


if __name__ == "__main__":
    # TODO: Remove this comment and complete the implementation above
    print("Please complete the TODO items in this file.")
    print("Once completed, run this file to test your implementation.")
    
    # Uncomment the line below after completing your implementation:
    # test_user_profile()
