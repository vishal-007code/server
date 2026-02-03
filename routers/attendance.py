from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from models.attendance import Attendance
from models.employee import Employee
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    date: date
    status: Literal["Present", "Absent"] = "Present"

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v):
        return v.strip().upper()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ["Present", "Absent"]:
            raise ValueError("Invalid status")
        return v

    class Config:
        populate_by_name = True


class AttendanceStats(BaseModel):
    employee_id: str
    total_days: int
    present_days: int
    absent_days: int


@router.get("/", response_model=List[Attendance])
async def get_all_attendance(
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    date_filter: Optional[date] = Query(None, alias="date"),
):
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    # Build query
    query = {}
    if employee_id:
        query["employeeId"] = employee_id.upper()
    if date_filter:
        # Convert date to datetime for query
        date_start = datetime.combine(date_filter, datetime.min.time())
        date_end = datetime.combine(date_filter, datetime.max.time())
        query["date"] = {"$gte": date_start, "$lte": date_end}
    
    # Fetch records
    records = await database.attendances.find(query).sort([("date", -1), ("createdAt", -1)]).to_list(length=None)
    
    # Convert to Attendance objects
    attendance_list = []
    for record in records:
        attendance_dict = {
            "employeeId": record["employeeId"],
            "date": record["date"].date().isoformat() if isinstance(record["date"], datetime) else str(record["date"]),
            "status": record["status"],
        }
        if record.get("createdAt"):
            attendance_dict["createdAt"] = record["createdAt"].isoformat() if isinstance(record["createdAt"], datetime) else record["createdAt"]
        if record.get("updatedAt"):
            attendance_dict["updatedAt"] = record["updatedAt"].isoformat() if isinstance(record["updatedAt"], datetime) else record["updatedAt"]
        
        attendance = Attendance.model_validate(attendance_dict)
        attendance.id = ObjectId(record["_id"])
        attendance_list.append(attendance)
    
    return attendance_list


@router.get("/employee/{employee_id}", response_model=List[Attendance])
async def get_employee_attendance(employee_id: str):
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    records = await database.attendances.find(
        {"employeeId": employee_id.upper()}
    ).sort([("date", -1)]).to_list(length=None)
    
    # Convert to Attendance objects
    attendance_list = []
    for record in records:
        attendance_dict = {
            "employeeId": record["employeeId"],
            "date": record["date"].date().isoformat() if isinstance(record["date"], datetime) else str(record["date"]),
            "status": record["status"],
        }
        if record.get("createdAt"):
            attendance_dict["createdAt"] = record["createdAt"].isoformat() if isinstance(record["createdAt"], datetime) else record["createdAt"]
        if record.get("updatedAt"):
            attendance_dict["updatedAt"] = record["updatedAt"].isoformat() if isinstance(record["updatedAt"], datetime) else record["updatedAt"]
        
        attendance = Attendance.model_validate(attendance_dict)
        attendance.id = ObjectId(record["_id"])
        attendance_list.append(attendance)
    
    return attendance_list


@router.post("/", response_model=Attendance, status_code=status.HTTP_201_CREATED)
async def mark_attendance(attendance_data: AttendanceCreate):
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    employee = await Employee.find_one(
        Employee.employee_id == attendance_data.employee_id
    )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    records = await database.attendances.find(
        {"employeeId": attendance_data.employee_id}
    ).to_list(length=None)

    for r in records:
        if r["date"].date() == attendance_data.date:
            await database.attendances.update_one(
                {"_id": r["_id"]},
                {
                    "$set": {
                        "status": attendance_data.status,
                        "updatedAt": datetime.utcnow(),
                    }
                },
            )
            saved = await database.attendances.find_one({"_id": r["_id"]})
            break
    else:
        try:
            result = await database.attendances.insert_one(
                {
                    "employeeId": attendance_data.employee_id,
                    "date": datetime.combine(
                        attendance_data.date, datetime.min.time()
                    ),
                    "status": attendance_data.status,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                }
            )
            saved = await database.attendances.find_one(
                {"_id": result.inserted_id}
            )
        except Exception as e:
            error_str = str(e)
            # Handle duplicate key error - might be due to old index
            if "duplicate key" in error_str.lower() or "E11000" in error_str:
                # Check if it's the old index issue
                if "employee_id" in error_str and "employeeId" not in error_str:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database index error: Old index 'employee_id_1_date_1' exists. Please run: mongosh 'your-connection-string' --file scripts/fix_attendance_index.js"
                    )
                # Try to find existing record by employeeId and date
                date_dt = datetime.combine(attendance_data.date, datetime.min.time())
                existing = await database.attendances.find_one({
                    "employeeId": attendance_data.employee_id,
                    "date": date_dt
                })
                if existing:
                    # Update existing record
                    await database.attendances.update_one(
                        {"_id": existing["_id"]},
                        {
                            "$set": {
                                "status": attendance_data.status,
                                "updatedAt": datetime.utcnow(),
                            }
                        }
                    )
                    saved = await database.attendances.find_one({"_id": existing["_id"]})
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Attendance already exists for this employee on this date"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error marking attendance: {error_str}"
                )

    attendance_dict = {
        "employeeId": saved["employeeId"],
        "date": saved["date"].date().isoformat(),
        "status": saved["status"],
        "createdAt": saved["createdAt"].isoformat(),
        "updatedAt": saved["updatedAt"].isoformat(),
    }

    attendance = Attendance.model_validate(attendance_dict)
    attendance.id = ObjectId(saved["_id"])
    return attendance


@router.get("/stats/{employee_id}", response_model=AttendanceStats)
async def get_attendance_stats(employee_id: str):
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    employee_id = employee_id.upper()

    records = await database.attendances.find(
        {"employeeId": employee_id}
    ).to_list(length=None)

    total_days = len(records)
    present_days = sum(1 for r in records if r["status"] == "Present")
    absent_days = sum(1 for r in records if r["status"] == "Absent")

    return AttendanceStats(
        employee_id=employee_id,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
    )
