"""
Pydantic: Why Use It?

This module demonstrates the power of Pydantic for data validation and modeling.
Pydantic provides:
1. Automatic data validation
2. Type conversion
3. Clear error messages
4. IDE support with type hints
5. JSON serialization/deserialization
6. Integration with FastAPI and other frameworks
"""

from pydantic import BaseModel, EmailStr, AnyUrl, Field, ValidationError
from typing import List, Dict, Optional, Annotated
import json

class Patient(BaseModel):
    """
    A Patient model demonstrating various Pydantic features:
    - Field validation with constraints
    - Type conversion
    - Optional fields with defaults
    - Custom field descriptions and examples
    """
    
    name: Annotated[
        str, 
        Field(
            max_length=50, 
            title='Name of the patient', 
            description='Give the name of the patient in less than 50 chars', 
            examples=['Nitish', 'Amit']
        )
    ]
    email: EmailStr
    linkedin_url: AnyUrl
    age: int = Field(gt=0, lt=120, description="Age must be between 1 and 119")
    weight: Annotated[float, Field(gt=0, strict=True, description="Weight in kg")]
    married: Annotated[
        Optional[bool], 
        Field(default=None, description='Is the patient married or not')
    ]
    allergies: Annotated[
        Optional[List[str]], 
        Field(default=None, max_length=5, description="List of allergies (max 5)")
    ]
    contact_details: Dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "age": 30,
                "weight": 75.5,
                "married": True,
                "allergies": ["peanuts", "shellfish"],
                "contact_details": {
                    "phone": "+1234567890",
                    "address": "123 Main St, City, Country"
                }
            }
        }


def update_patient_data(patient: Patient) -> None:
    """
    Process patient data - demonstrates type safety and validation
    """
    print(f"Patient Name: {patient.name}")
    print(f"Patient Age: {patient.age}")
    print(f"Allergies: {patient.allergies or 'None'}")
    print(f"Married: {patient.married if patient.married is not None else 'Not specified'}")
    print(f"Email: {patient.email}")
    print(f"LinkedIn: {patient.linkedin_url}")
    print(f"Weight: {patient.weight} kg")
    print(f"Contact Details: {patient.contact_details}")
    print('Patient data processed successfully!\n')


def demonstrate_validation_errors():
    """
    Demonstrate how Pydantic handles validation errors
    """
    print("=== Demonstrating Validation Errors ===")
    
    # Invalid data that will cause validation errors
    invalid_data = {
        'name': '',  # Empty name
        'email': 'not-an-email',  # Invalid email
        'linkedin_url': 'not-a-url',  # Invalid URL
        'age': -5,  # Invalid age
        'weight': 'not-a-number',  # Invalid weight type
        'contact_details': 'not-a-dict'  # Invalid type
    }
    
    try:
        patient = Patient(**invalid_data)
    except ValidationError as e:
        print("Validation failed with the following errors:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")
        print()


def demonstrate_json_serialization():
    """
    Demonstrate JSON serialization and deserialization
    """
    print("=== JSON Serialization Demo ===")
    
    patient_data = {
        'name': 'Alice Johnson',
        'email': 'alice@example.com',
        'linkedin_url': 'https://linkedin.com/in/alicejohnson',
        'age': 28,
        'weight': 65.2,
        'married': True,
        'allergies': ['dust', 'pollen'],
        'contact_details': {'phone': '+1987654321', 'city': 'New York'}
    }
    
    patient = Patient(**patient_data)
    
    # Convert to JSON
    json_data = patient.model_dump_json(indent=2)
    print(f"Patient as JSON:\n{json_data}\n")
    
    # Parse from JSON
    patient_from_json = Patient.model_validate_json(json_data)
    print(f"Parsed back from JSON: {patient_from_json.name}")
    print()


if __name__ == "__main__":
    print("=== Pydantic Demo: Patient Management System ===\n")
    
    # Original example with valid data
    patient_info = {
        'name': 'Nitish Kumar',
        'email': 'nitish@gmail.com',
        'linkedin_url': 'https://linkedin.com/in/nitish1322',
        'age': 30,  # Will be converted from string to int if passed as string
        'weight': 75.2,
        'married': True,
        'allergies': ['peanuts'],
        'contact_details': {'phone': '2353462', 'emergency_contact': 'John Doe'}
    }
    
    try:
        patient1 = Patient(**patient_info)
        update_patient_data(patient1)
        
        # Demonstrate additional features
        demonstrate_validation_errors()
        demonstrate_json_serialization()
        
    except ValidationError as e:
        print(f"Error creating patient: {e}")
    
    print("=== Demo Complete ===")