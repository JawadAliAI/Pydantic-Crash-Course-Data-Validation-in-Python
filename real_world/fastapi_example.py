"""
Real-World Example: FastAPI Integration with Pydantic

This module demonstrates how to use Pydantic with FastAPI for building
robust APIs with automatic validation, serialization, and documentation.

Features demonstrated:
- Request/Response models with Pydantic
- Automatic OpenAPI documentation
- Data validation and error handling
- Nested models and relationships
- Query parameters with validation
- Custom response models
"""

from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uvicorn


# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Pydantic Models
class UserBase(BaseModel):
    """Base user model with common fields"""
    
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating a new user"""
    
    password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "password": "securepassword123",
                "is_active": True
            }
        }


class UserResponse(UserBase):
    """Model for user responses (excludes password)"""
    
    user_id: int = Field(..., gt=0)
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00"
            }
        }


class TaskBase(BaseModel):
    """Base task model"""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    tags: List[str] = Field(default_factory=list, max_items=10)


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    
    assigned_to: Optional[int] = Field(None, gt=0, description="User ID of assignee")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication to the API",
                "status": "todo",
                "priority": "high",
                "due_date": "2024-02-01",
                "assigned_to": 1,
                "tags": ["backend", "security"]
            }
        }


class TaskUpdate(BaseModel):
    """Model for updating a task"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = Field(None, max_items=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "in_progress",
                "priority": "critical",
                "description": "Updated description with more details"
            }
        }


class TaskResponse(TaskBase):
    """Model for task responses"""
    
    task_id: int = Field(..., gt=0)
    created_by: int = Field(..., gt=0)
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested user information
    creator: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication to the API",
                "status": "in_progress",
                "priority": "high",
                "due_date": "2024-02-01",
                "created_by": 1,
                "assigned_to": 2,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-16T14:20:00",
                "tags": ["backend", "security"]
            }
        }


class TaskListResponse(BaseModel):
    """Model for paginated task list responses"""
    
    tasks: List[TaskResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [],
                "total": 50,
                "page": 1,
                "per_page": 10,
                "pages": 5
            }
        }


class ErrorResponse(BaseModel):
    """Model for error responses"""
    
    error: str
    detail: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "The provided data is invalid",
                "errors": [
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }


# In-memory storage (in real apps, use a database)
users_db: Dict[int, Dict] = {}
tasks_db: Dict[int, Dict] = {}
user_counter = 0
task_counter = 0


# FastAPI app
app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management API built with FastAPI and Pydantic",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Helper functions
def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    return users_db.get(user_id)


def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Get task by ID"""
    return tasks_db.get(task_id)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail="The provided data is invalid",
            errors=[
                {
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        ).dict()
    )


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
async def create_user(user_data: UserCreate):
    """
    Create a new user
    
    - **username**: Unique username (3-50 characters, alphanumeric + underscore)
    - **email**: Valid email address
    - **full_name**: User's full name
    - **password**: Password (minimum 8 characters)
    - **is_active**: Whether the user account is active
    """
    global user_counter
    
    # Check if username already exists
    for user in users_db.values():
        if user["username"] == user_data.username:
            raise HTTPException(
                status_code=400,
                detail=f"Username '{user_data.username}' already exists"
            )
    
    # Check if email already exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{user_data.email}' already exists"
            )
    
    user_counter += 1
    user_dict = user_data.dict()
    user_dict.update({
        "user_id": user_counter,
        "created_at": datetime.now()
    })
    
    # Remove password from stored data (in real apps, hash it)
    del user_dict["password"]
    
    users_db[user_counter] = user_dict
    return UserResponse(**user_dict)


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of users to return"),
    active_only: bool = Query(True, description="Only return active users")
):
    """
    Get a list of users
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    - **active_only**: Filter to only active users
    """
    users = list(users_db.values())
    
    if active_only:
        users = [user for user in users if user.get("is_active", True)]
    
    return [UserResponse(**user) for user in users[skip:skip + limit]]


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to retrieve")
):
    """
    Get a specific user by ID
    
    - **user_id**: The unique identifier of the user
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)


# Task endpoints
@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
async def create_task(task_data: TaskCreate, creator_id: int = Query(..., gt=0)):
    """
    Create a new task
    
    - **creator_id**: ID of the user creating the task
    - **title**: Task title (required)
    - **description**: Optional task description
    - **status**: Task status (todo, in_progress, done)
    - **priority**: Task priority (low, medium, high, critical)
    - **due_date**: Optional due date
    - **assigned_to**: Optional user ID to assign the task to
    - **tags**: List of tags for the task
    """
    global task_counter
    
    # Verify creator exists
    if not get_user_by_id(creator_id):
        raise HTTPException(status_code=404, detail="Creator user not found")
    
    # Verify assignee exists if provided
    if task_data.assigned_to and not get_user_by_id(task_data.assigned_to):
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    task_counter += 1
    task_dict = task_data.dict()
    task_dict.update({
        "task_id": task_counter,
        "created_by": creator_id,
        "created_at": datetime.now(),
        "updated_at": None
    })
    
    tasks_db[task_counter] = task_dict
    
    # Add creator and assignee information
    task_response = TaskResponse(**task_dict)
    task_response.creator = UserResponse(**users_db[creator_id])
    if task_data.assigned_to:
        task_response.assignee = UserResponse(**users_db[task_data.assigned_to])
    
    return task_response


@app.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    assigned_to: Optional[int] = Query(None, gt=0, description="Filter by assigned user ID"),
    created_by: Optional[int] = Query(None, gt=0, description="Filter by creator user ID"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    Get a paginated list of tasks with optional filtering
    
    - **page**: Page number for pagination
    - **per_page**: Number of items per page
    - **status**: Filter by task status
    - **priority**: Filter by task priority
    - **assigned_to**: Filter by assigned user ID
    - **created_by**: Filter by creator user ID
    - **tag**: Filter by tag
    """
    tasks = list(tasks_db.values())
    
    # Apply filters
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    if priority:
        tasks = [task for task in tasks if task["priority"] == priority]
    
    if assigned_to:
        tasks = [task for task in tasks if task.get("assigned_to") == assigned_to]
    
    if created_by:
        tasks = [task for task in tasks if task["created_by"] == created_by]
    
    if tag:
        tasks = [task for task in tasks if tag.lower() in [t.lower() for t in task.get("tags", [])]]
    
    # Pagination
    total = len(tasks)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_tasks = tasks[start:end]
    
    # Add user information to tasks
    task_responses = []
    for task in paginated_tasks:
        task_response = TaskResponse(**task)
        task_response.creator = UserResponse(**users_db[task["created_by"]])
        if task.get("assigned_to"):
            assignee = users_db.get(task["assigned_to"])
            if assignee:
                task_response.assignee = UserResponse(**assignee)
        task_responses.append(task_response)
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: int = Path(..., gt=0, description="The ID of the task to retrieve")
):
    """
    Get a specific task by ID
    
    - **task_id**: The unique identifier of the task
    """
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_response = TaskResponse(**task)
    task_response.creator = UserResponse(**users_db[task["created_by"]])
    if task.get("assigned_to"):
        assignee = users_db.get(task["assigned_to"])
        if assignee:
            task_response.assignee = UserResponse(**assignee)
    
    return task_response


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_update: TaskUpdate,
    task_id: int = Path(..., gt=0, description="The ID of the task to update")
):
    """
    Update a specific task
    
    - **task_id**: The unique identifier of the task
    - Only provided fields will be updated
    """
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify assignee exists if being updated
    if task_update.assigned_to and not get_user_by_id(task_update.assigned_to):
        raise HTTPException(status_code=404, detail="Assigned user not found")
    
    # Update only provided fields
    update_data = task_update.dict(exclude_unset=True)
    if update_data:
        task.update(update_data)
        task["updated_at"] = datetime.now()
        tasks_db[task_id] = task
    
    task_response = TaskResponse(**task)
    task_response.creator = UserResponse(**users_db[task["created_by"]])
    if task.get("assigned_to"):
        assignee = users_db.get(task["assigned_to"])
        if assignee:
            task_response.assignee = UserResponse(**assignee)
    
    return task_response


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
async def delete_task(
    task_id: int = Path(..., gt=0, description="The ID of the task to delete")
):
    """
    Delete a specific task
    
    - **task_id**: The unique identifier of the task to delete
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API and basic statistics.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "stats": {
            "users": len(users_db),
            "tasks": len(tasks_db),
            "active_users": len([u for u in users_db.values() if u.get("is_active", True)])
        }
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "User management",
            "Task management",
            "Automatic validation",
            "OpenAPI documentation",
            "Pagination and filtering"
        ]
    }


if __name__ == "__main__":
    print("Starting Task Management API...")
    print("Features:")
    print("- Automatic request/response validation with Pydantic")
    print("- Interactive API documentation at http://localhost:8000/docs")
    print("- Alternative documentation at http://localhost:8000/redoc")
    print("- Health check at http://localhost:8000/health")
    print()
    print("Example usage:")
    print("1. Create a user: POST /users")
    print("2. Create a task: POST /tasks")
    print("3. List tasks: GET /tasks")
    print("4. Update a task: PATCH /tasks/{task_id}")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
