from pydantic import BaseModel, EmailStr, model_validator, computed_field
from typing import List, Dict


class Address(BaseModel):
    city: str
    state: str
    pin: str

class Patient(BaseModel):

    name: str
    email: EmailStr
    age: int
    address: Address
    weight: float
    height: int
    married: bool
    allergies: List[str]
    contact_details: Dict[str, str] 



address_dict = {'city': 'Islamabad', 'state': 'Capital', 'pin':'2131'}

address1 = Address(**address_dict)
patient_info = {
    'name': 'nitish', 
    'email': 'nitish@example.com',
    'age': 30,
    'address': address1,
    'weight': 70.5,
    'height': 175,
    'married': False,
    'allergies': ['penicillin'],
    'contact_details': {
        'phone': '123-456-7890',
        'emergency_contact': '987-654-3210'
    }
}

patient1 = Patient(**patient_info)