from pydantic import BaseModel, EmailStr, model_validator, computed_field
from typing import List, Dict

class Patient(BaseModel):

    name: str
    email: EmailStr
    age: int
    weight: float
    height: int
    married: bool
    allergies: List[str]
    contact_details: Dict[str, str]


@computed_field
@property
def calculated_bmi(self)-> float:
    """Calculate Body Mass Index (BMI)"""
    if self.weight <= 0 or self.age <= 0:
        return 0.0
    return self.weight / ((self.age / 100) ** 2)


def update_patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print(patient.married)
    print(f'Calculated BMI: {patient.calculated_bmi}')
    print('updated')

patient_info = {'name':'nitish', 'email':'abc@icici.com', 'age': '65', 'weight': 75.2,'height': 175, 'married': True, 'allergies': ['pollen', 'dust'], 'contact_details':{'phone':'2353462', 'emergency':'235236'}}

patient1 = Patient(**patient_info) 

update_patient_data(patient1)