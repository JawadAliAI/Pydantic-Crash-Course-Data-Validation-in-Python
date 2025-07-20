"""
Solution: User Profile Management System

This is the complete solution for Exercise 1.
Study this implementation to understand proper Pydantic usage patterns.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from typing import List, Dict, Optional, Union
from datetime import datetime, date, timedelta
from enum import Enum
import re


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Address(BaseModel):
    """Address model with proper field validation"""
    
    street: str = Field(..., min_length=5, max_length=200, description="Street address")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: Optional[str] = Field(None, min_length=2, max_length=100, description="State/Province")
    country: str = Field(..., min_length=2, max_length=100, description="Country name")
    postal_code: str = Field(..., pattern=r'^[\d\w\s-]{3,12}$', description="Postal/ZIP code")
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v):
        # Remove any extra whitespace
        return v.strip() if v else v


class SocialMedia(BaseModel):
    """Social media links with URL validation"""
    
    linkedin: Optional[str] = Field(None, pattern=r'^https?://(?:www\.)?linkedin\.com/.+')
    twitter: Optional[str] = Field(None, pattern=r'^https?://(?:www\.)?twitter\.com/.+')
    github: Optional[str] = Field(None, pattern=r'^https?://(?:www\.)?github\.com/.+')
    website: Optional[str] = Field(None, pattern=r'^https?://.+\..+')


class UserProfile(BaseModel):
    """Complete user profile model with validation"""
    
    user_id: int = Field(..., gt=0, description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Email address")
    first_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    age: int = Field(..., ge=13, le=120, description="User age")
    gender: Optional[Gender] = Field(None, description="User gender")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    skills: List[str] = Field(default_factory=list, max_items=20, description="User skills")
    address: Optional[Address] = Field(None, description="User address")
    social_media: Optional[SocialMedia] = Field(None, description="Social media links")
    is_active: bool = Field(True, description="Account status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        """Validate and clean skills list"""
        if not v:
            return v
        
        # Clean skills: strip whitespace, convert to lowercase, remove empty strings
        cleaned_skills = [skill.strip().lower() for skill in v if skill.strip()]
        
        # Remove duplicates while preserving order
        unique_skills = []
        for skill in cleaned_skills:
            if skill not in unique_skills:
                unique_skills.append(skill)
        
        return unique_skills
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        """Validate and clean bio"""
        if not v:
            return v
        
        # Strip whitespace
        cleaned_bio = v.strip()
        
        # Basic profanity filter (simple example)
        profanity_words = ['badword1', 'badword2']  # In real app, use a proper filter
        for word in profanity_words:
            if word.lower() in cleaned_bio.lower():
                raise ValueError('Bio contains inappropriate content')
        
        return cleaned_bio
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        """Validate date of birth"""
        if v and v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v
    
    @model_validator(mode='after')
    def validate_age_consistency(self):
        """Ensure date of birth matches age if both provided"""
        age = self.age
        date_of_birth = self.date_of_birth
        
        if age and date_of_birth:
            today = date.today()
            calculated_age = today.year - date_of_birth.year
            
            # Adjust if birthday hasn't occurred this year
            if today.month < date_of_birth.month or \
               (today.month == date_of_birth.month and today.day < date_of_birth.day):
                calculated_age -= 1
            
            # Allow 1 year tolerance for age discrepancy
            if abs(calculated_age - age) > 1:
                raise ValueError(f'Age {age} does not match date of birth (calculated: {calculated_age})')
        
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "age": 25,
                "gender": "male",
                "bio": "Software developer passionate about Python",
                "skills": ["python", "javascript", "sql"],
                "is_active": True
            }
        }


class ProfileManager:
    """Profile manager with complete implementation"""
    
    def __init__(self):
        self.profiles: Dict[int, UserProfile] = {}
        self.username_index: Dict[str, int] = {}
    
    def create_profile(self, profile_data: Dict) -> UserProfile:
        """Create a new user profile"""
        
        # First validate the data
        profile = UserProfile(**profile_data)
        
        # Check if user_id already exists
        if profile.user_id in self.profiles:
            raise ValueError(f"User ID {profile.user_id} already exists")
        
        # Check if username already exists
        if profile.username in self.username_index:
            raise ValueError(f"Username '{profile.username}' already exists")
        
        # Store the profile
        self.profiles[profile.user_id] = profile
        self.username_index[profile.username] = profile.user_id
        
        return profile
    
    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get a profile by user_id"""
        return self.profiles.get(user_id)
    
    def get_profile_by_username(self, username: str) -> Optional[UserProfile]:
        """Get a profile by username"""
        user_id = self.username_index.get(username.lower())
        if user_id:
            return self.profiles.get(user_id)
        return None
    
    def update_profile(self, user_id: int, updates: Dict) -> UserProfile:
        """Update an existing profile"""
        
        if user_id not in self.profiles:
            raise ValueError(f"Profile with user_id {user_id} not found")
        
        current_profile = self.profiles[user_id]
        
        # Get current profile data and apply updates
        current_data = current_profile.model_dump()
        current_data.update(updates)
        current_data['updated_at'] = datetime.now()
        
        # Handle username change (update index)
        old_username = current_profile.username
        new_username = updates.get('username', old_username)
        
        if new_username != old_username:
            if new_username.lower() in self.username_index:
                raise ValueError(f"Username '{new_username}' already exists")
            
            # Remove old username from index
            del self.username_index[old_username]
        
        # Validate updated data
        updated_profile = UserProfile(**current_data)
        
        # Store updated profile and update index
        self.profiles[user_id] = updated_profile
        if new_username != old_username:
            self.username_index[new_username.lower()] = user_id
        
        return updated_profile
    
    def delete_profile(self, user_id: int) -> bool:
        """Delete a profile"""
        
        if user_id not in self.profiles:
            return False
        
        profile = self.profiles[user_id]
        
        # Remove from both indexes
        del self.profiles[user_id]
        del self.username_index[profile.username]
        
        return True
    
    def search_profiles(self, **criteria) -> List[UserProfile]:
        """Search profiles by criteria"""
        
        results = []
        
        for profile in self.profiles.values():
            match = True
            
            # Age range search
            if 'min_age' in criteria and profile.age < criteria['min_age']:
                match = False
            if 'max_age' in criteria and profile.age > criteria['max_age']:
                match = False
            
            # Skills search
            if 'skills' in criteria:
                required_skills = [skill.lower() for skill in criteria['skills']]
                if not any(skill in profile.skills for skill in required_skills):
                    match = False
            
            # City search
            if 'city' in criteria and profile.address:
                if profile.address.city.lower() != criteria['city'].lower():
                    match = False
            
            # Active status search
            if 'is_active' in criteria and profile.is_active != criteria['is_active']:
                match = False
            
            # Gender search
            if 'gender' in criteria and profile.gender != criteria['gender']:
                match = False
            
            if match:
                results.append(profile)
        
        return results
    
    def get_statistics(self) -> Dict[str, Union[int, float, Dict]]:
        """Get statistics about stored profiles"""
        
        if not self.profiles:
            return {"total_profiles": 0}
        
        profiles = list(self.profiles.values())
        
        # Basic stats
        stats = {
            "total_profiles": len(profiles),
            "active_profiles": sum(1 for p in profiles if p.is_active),
            "average_age": sum(p.age for p in profiles) / len(profiles),
        }
        
        # Gender distribution
        gender_dist = {}
        for profile in profiles:
            gender = profile.gender.value if profile.gender else "unknown"
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
        stats["gender_distribution"] = gender_dist
        
        # Top skills
        skill_count = {}
        for profile in profiles:
            for skill in profile.skills:
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
        stats["top_skills"] = dict(top_skills)
        
        return stats


def test_user_profile():
    """Test function to validate the implementation"""
    
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
        "date_of_birth": date(1999, 3, 15),
        "bio": "Software developer passionate about Python",
        "skills": ["Python", "JavaScript", "SQL", "Git", "python"],  # Test duplicate removal
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
        # Test 1: Profile creation
        print("1. Testing profile creation...")
        profile = manager.create_profile(valid_profile_data)
        print(f"   ✅ Created profile for {profile.first_name} {profile.last_name}")
        print(f"   ✅ Skills deduplicated: {profile.skills}")
        print(f"   ✅ Username normalized: {profile.username}")
        
        # Test 2: Profile retrieval
        print("\n2. Testing profile retrieval...")
        retrieved = manager.get_profile(1)
        print(f"   ✅ Retrieved by ID: {retrieved.username}")
        
        retrieved_by_username = manager.get_profile_by_username("john_doe")
        print(f"   ✅ Retrieved by username: {retrieved_by_username.email}")
        
        # Test 3: Profile update
        print("\n3. Testing profile update...")
        updated = manager.update_profile(1, {
            "bio": "Updated bio: Senior Python developer",
            "age": 26,
            "skills": ["python", "django", "fastapi", "postgresql"]
        })
        print(f"   ✅ Updated profile: {updated.bio}")
        print(f"   ✅ Updated skills: {updated.skills}")
        print(f"   ✅ Updated timestamp: {updated.updated_at}")
        
        # Test 4: Create second profile
        print("\n4. Creating second profile...")
        profile_data_2 = {
            "user_id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "age": 30,
            "gender": "female",
            "skills": ["python", "machine-learning", "data-science"],
            "address": {
                "street": "456 Tech Ave",
                "city": "San Francisco",
                "country": "USA",
                "postal_code": "94105"
            }
        }
        
        profile2 = manager.create_profile(profile_data_2)
        print(f"   ✅ Created second profile: {profile2.username}")
        
        # Test 5: Search functionality
        print("\n5. Testing search functionality...")
        
        # Search by age range
        young_profiles = manager.search_profiles(min_age=25, max_age=30)
        print(f"   ✅ Found {len(young_profiles)} profiles aged 25-30")
        
        # Search by skills
        python_devs = manager.search_profiles(skills=["python"])
        print(f"   ✅ Found {len(python_devs)} Python developers")
        
        # Search by city
        sf_profiles = manager.search_profiles(city="San Francisco")
        print(f"   ✅ Found {len(sf_profiles)} profiles in San Francisco")
        
        # Test 6: Statistics
        print("\n6. Testing statistics...")
        stats = manager.get_statistics()
        print(f"   ✅ Total profiles: {stats['total_profiles']}")
        print(f"   ✅ Average age: {stats['average_age']:.1f}")
        print(f"   ✅ Top skills: {list(stats['top_skills'].keys())[:3]}")
        
        # Test 7: Validation errors
        print("\n7. Testing validation errors...")
        
        # Invalid age
        try:
            invalid_data = valid_profile_data.copy()
            invalid_data["user_id"] = 3
            invalid_data["age"] = 5  # Too young
            manager.create_profile(invalid_data)
            print("   ❌ Should have failed validation")
        except ValidationError as e:
            print("   ✅ Correctly caught age validation error")
        
        # Invalid email
        try:
            invalid_data = valid_profile_data.copy()
            invalid_data["user_id"] = 4
            invalid_data["email"] = "invalid-email"
            manager.create_profile(invalid_data)
            print("   ❌ Should have failed validation")
        except ValidationError as e:
            print("   ✅ Correctly caught email validation error")
        
        # Duplicate username
        try:
            invalid_data = valid_profile_data.copy()
            invalid_data["user_id"] = 5
            # Same username as first profile
            manager.create_profile(invalid_data)
            print("   ❌ Should have failed duplicate username check")
        except ValueError as e:
            print("   ✅ Correctly caught duplicate username error")
        
        # Test 8: Profile deletion
        print("\n8. Testing profile deletion...")
        deleted = manager.delete_profile(2)
        print(f"   ✅ Profile deleted: {deleted}")
        
        remaining_profile = manager.get_profile(2)
        print(f"   ✅ Profile no longer exists: {remaining_profile is None}")
        
        print("\n🎉 All tests passed! Implementation is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_user_profile()
