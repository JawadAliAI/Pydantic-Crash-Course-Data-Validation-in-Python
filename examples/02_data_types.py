"""
Data Types and Advanced Validation

This module demonstrates:
- Various Pydantic data types
- Custom validators
- Field constraints
- Type coercion
- Complex validation patterns
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from typing import List, Dict, Union, Optional, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Product(BaseModel):
    """Product model demonstrating various data types and validation"""
    
    # String types with validation
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    sku: str = Field(..., pattern=r'^[A-Z]{3}-\d{6}$', description="Format: ABC-123456")
    
    # Numeric types with constraints
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    weight: float = Field(..., gt=0, description="Weight in kg")
    quantity: int = Field(0, ge=0, le=10000)
    
    # Boolean and enum
    is_active: bool = True
    priority: Priority = Priority.MEDIUM
    
    # Date and datetime
    created_date: date = Field(default_factory=date.today)
    updated_at: Optional[datetime] = None
    
    # Complex types
    tags: List[str] = Field(default_factory=list, max_items=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dimensions: Dict[str, float] = Field(default_factory=dict)
    
    # Union types
    identifier: Union[int, str] = Field(..., description="Can be either ID number or string code")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Custom name validation"""
        if not v or v.isspace():
            raise ValueError('Name cannot be empty or whitespace only')
        
        # Convert to title case
        return v.title()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags"""
        if not v:
            return v
            
        # Remove duplicates and empty strings, convert to lowercase
        cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
        
        if len(cleaned_tags) > 10:
            raise ValueError('Too many tags (maximum 10)')
        
        return cleaned_tags
    
    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        """Validate product dimensions"""
        if not v:
            return v
        
        required_dims = ['length', 'width', 'height']
        for dim in required_dims:
            if dim in v and v[dim] <= 0:
                raise ValueError(f'{dim} must be positive')
        
        return v
    
    @model_validator(mode='after')
    def validate_product_consistency(self):
        """Cross-field validation"""
        priority = self.priority
        is_active = self.is_active
        quantity = self.quantity or 0
        
        # Critical priority items must be active and in stock
        if priority == Priority.CRITICAL:
            if not is_active:
                raise ValueError('Critical priority items must be active')
            if quantity == 0:
                raise ValueError('Critical priority items must be in stock')
        
        return self


class Order(BaseModel):
    """Order model with complex validation logic"""
    
    order_id: str = Field(..., pattern=r'^ORD-\d{8}-[A-Z]{2}$')
    customer_email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    items: List[Dict[str, Union[str, int, float]]] = Field(..., min_items=1)
    total_amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    order_date: datetime = Field(default_factory=datetime.now)
    shipping_address: Dict[str, str]
    status: str = Field("pending", pattern=r'^(pending|confirmed|shipped|delivered|cancelled)$')
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        """Validate order items structure"""
        required_fields = {'product_id', 'quantity', 'price'}
        
        for i, item in enumerate(v):
            if not isinstance(item, dict):
                raise ValueError(f'Item {i} must be a dictionary')
            
            if not required_fields.issubset(item.keys()):
                raise ValueError(f'Item {i} missing required fields: {required_fields - item.keys()}')
            
            if item['quantity'] <= 0:
                raise ValueError(f'Item {i} quantity must be positive')
            
            if item['price'] <= 0:
                raise ValueError(f'Item {i} price must be positive')
        
        return v
    
    @field_validator('shipping_address')
    @classmethod
    def validate_shipping_address(cls, v):
        """Validate shipping address completeness"""
        required_fields = {'street', 'city', 'country', 'postal_code'}
        missing_fields = required_fields - v.keys()
        
        if missing_fields:
            raise ValueError(f'Missing shipping address fields: {missing_fields}')
        
        # Basic postal code validation (simple example)
        postal_code = v.get('postal_code', '')
        if not re.match(r'^[\d\w\s-]{3,10}$', postal_code):
            raise ValueError('Invalid postal code format')
        
        return v
    
    @model_validator(mode='after')
    def validate_total_consistency(self):
        """Validate that total amount matches items"""
        items = self.items or []
        total_amount = self.total_amount
        
        if items and total_amount:
            calculated_total = sum(
                Decimal(str(item['quantity'])) * Decimal(str(item['price']))
                for item in items
            )
            
            # Allow small rounding differences
            if abs(calculated_total - total_amount) > Decimal('0.01'):
                raise ValueError(
                    f'Total amount {total_amount} does not match calculated total {calculated_total}'
                )
        
        return self


def demonstrate_data_types():
    """Show various data type examples"""
    
    print("=== Data Types Demo ===\n")
    
    product_data = {
        "name": "  wireless headphones  ",  # Will be stripped and title-cased
        "sku": "AUD-123456",
        "price": "99.99",  # String will be converted to Decimal
        "weight": 0.5,
        "quantity": 50,
        "priority": "high",
        "tags": ["audio", "wireless", "bluetooth", "audio"],  # Duplicates will be removed
        "metadata": {
            "brand": "TechCorp",
            "model": "WH-1000X",
            "color": "black"
        },
        "dimensions": {
            "length": 18.5,
            "width": 15.2,
            "height": 8.3
        },
        "identifier": "12345"  # Can be string or int
    }
    
    try:
        product = Product(**product_data)
        print(f"✅ Created product: {product.name}")
        print(f"   SKU: {product.sku}")
        print(f"   Price: ${product.price}")
        print(f"   Priority: {product.priority}")
        print(f"   Tags: {product.tags}")
        print(f"   Metadata: {product.metadata}")
        print()
    except ValidationError as e:
        print(f"❌ Product validation error:")
        for error in e.errors():
            print(f"   {error['loc']}: {error['msg']}")
        print()


def demonstrate_complex_validation():
    """Show complex validation scenarios"""
    
    print("=== Complex Validation Demo ===\n")
    
    # Valid order
    order_data = {
        "order_id": "ORD-20241220-US",
        "customer_email": "customer@example.com",
        "items": [
            {"product_id": "AUD-123456", "quantity": 2, "price": 99.99},
            {"product_id": "ACC-789012", "quantity": 1, "price": 29.99}
        ],
        "total_amount": "229.97",  # 2*99.99 + 1*29.99
        "shipping_address": {
            "street": "123 Tech Street",
            "city": "San Francisco",
            "country": "USA",
            "postal_code": "94105"
        }
    }
    
    try:
        order = Order(**order_data)
        print(f"✅ Created order: {order.order_id}")
        print(f"   Customer: {order.customer_email}")
        print(f"   Items: {len(order.items)}")
        print(f"   Total: ${order.total_amount}")
        print(f"   Status: {order.status}")
        print()
    except ValidationError as e:
        print(f"❌ Order validation error:")
        for error in e.errors():
            print(f"   {error['loc']}: {error['msg']}")
        print()


def demonstrate_validation_errors():
    """Show various validation error scenarios"""
    
    print("=== Validation Errors Demo ===\n")
    
    # Invalid product data
    invalid_products = [
        {
            "name": "Invalid SKU Product",
            "data": {"name": "Test", "sku": "INVALID", "price": 10.0, "weight": 1.0, "identifier": 1}
        },
        {
            "name": "Critical Priority But Inactive",
            "data": {
                "name": "Test", "sku": "TST-123456", "price": 10.0, "weight": 1.0,
                "priority": "critical", "is_active": False, "identifier": 1
            }
        },
        {
            "name": "Too Many Tags",
            "data": {
                "name": "Test", "sku": "TST-123456", "price": 10.0, "weight": 1.0,
                "tags": [f"tag{i}" for i in range(15)], "identifier": 1
            }
        }
    ]
    
    for case in invalid_products:
        try:
            Product(**case["data"])
            print(f"❌ Expected error for: {case['name']}")
        except ValidationError as e:
            print(f"✅ {case['name']}: {e.errors()[0]['msg']}")
    
    print()


if __name__ == "__main__":
    demonstrate_data_types()
    demonstrate_complex_validation()
    demonstrate_validation_errors()
