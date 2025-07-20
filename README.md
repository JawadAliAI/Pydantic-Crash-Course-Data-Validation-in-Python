# Pydantic Learning Project

A comprehensive learning resource for Pydantic v2 with practical examples, exercises, and real-world applications.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Examples](#examples)
- [Exercises](#exercises)
- [Real-World Applications](#real-world-applications)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

This project is designed to help developers learn Pydantic v2, a powerful Python library for data validation and settings management using Python type hints. It provides a structured approach to learning with examples, exercises, and real-world scenarios.

## Features

- ✅ Pydantic v2 examples and best practices
- ✅ Type validation and data conversion
- ✅ Custom validators and field constraints
- ✅ Integration with FastAPI
- ✅ Practical exercises with solutions
- ✅ Real-world use cases
- ✅ Comprehensive test suite

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Pydantic
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
Pydantic/
├── 1_Pydantic_why.py          # Introduction and motivation
├── examples/                   # Learning examples
│   ├── 01_basic_models.py     # Basic Pydantic models
│   └── 02_data_types.py       # Data types and validation
├── exercises/                  # Practice exercises
│   ├── exercise_01_user_profile.py
│   └── solutions/             # Exercise solutions
│       └── solution_01_user_profile.py
├── real_world/                 # Real-world applications
│   └── fastapi_example.py     # FastAPI integration
├── tests/                      # Test files
│   └── test_basic_models.py
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Getting Started

1. Start with `1_Pydantic_why.py` to understand the motivation behind Pydantic
2. Explore the examples in the `examples/` directory
3. Try the exercises in the `exercises/` directory
4. Check your solutions against the provided solutions
5. Explore real-world applications in the `real_world/` directory

## Examples

### Basic Model Example

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
```

### Advanced Validation

```python
from pydantic import BaseModel, Field, validator

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()
```

## Exercises

The `exercises/` directory contains hands-on exercises to practice Pydantic concepts:

1. **User Profile** - Create a comprehensive user model with validation
2. More exercises coming soon...

## Real-World Applications

Explore practical applications in the `real_world/` directory:

- **FastAPI Integration** - Learn how to use Pydantic with FastAPI for API development

## Testing

Run the test suite:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest tests/ --cov=.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
