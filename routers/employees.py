from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from models.employee import Employee
from pydantic import BaseModel, EmailStr, Field, field_validator

router = APIRouter(prefix="/api/employees", tags=["employees"])


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    department: str

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID is required')
        return v.strip().upper()

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full Name is required')
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email is required')
        return v.strip().lower()

    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        if not v or not v.strip():
            raise ValueError('Department is required')
        return v.strip()

    class Config:
        populate_by_name = True


@router.get("/", response_model=List[Employee])
async def get_all_employees():
    """Get all employees"""
    try:
        # Get all employees and sort in Python (handles missing createdAt field)
        employees = await Employee.find_all().to_list()
        # Sort by created_at, handling None values
        employees.sort(key=lambda x: x.created_at if x.created_at else datetime.min, reverse=True)
        return employees
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database authentication required. Please set MONGODB_URI with credentials."
            )
        # If sorting fails, return unsorted list
        try:
            employees = await Employee.find_all().to_list()
            return employees
        except Exception as e2:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching employees: {str(e2)}"
            )


@router.get("/{id}", response_model=Employee)
async def get_employee(id: str):
    """Get a single employee by ID"""
    try:
        employee = await Employee.get(id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid employee ID: {str(e)}"
        )


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_data: EmployeeCreate):
    """Create a new employee"""
    try:
        # Check for duplicate employee ID
        existing_employee_by_id = await Employee.find_one(
            Employee.employee_id == employee_data.employee_id
        )
        if existing_employee_by_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already exists"
            )

        # Check for duplicate email
        existing_employee_by_email = await Employee.find_one(
            Employee.email == employee_data.email
        )
        if existing_employee_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        # Create employee - use Python field names (populate_by_name handles aliases)
        employee = Employee(
            employee_id=employee_data.employee_id,
            full_name=employee_data.full_name,
            email=employee_data.email,
            department=employee_data.department
        )

        saved_employee = await employee.insert()
        return saved_employee
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = str(e)
        # Provide more detailed error information
        if "employee_id" in error_details.lower() or "employeeId" in error_details.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid employee data: {error_details}. Please check employeeId, fullName, email, and department fields."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating employee: {error_details}"
        )


@router.delete("/{id}")
async def delete_employee(id: str):
    """Delete an employee"""
    try:
        employee = await Employee.get(id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        await employee.delete()
        return {"message": "Employee deleted successfully", "employee": employee}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid employee ID: {str(e)}"
        )
