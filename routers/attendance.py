from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from models.attendance import Attendance
from models.employee import Employee
from database import get_database, ensure_attendance_indexes

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


class AttendanceOut(BaseModel):
    _id: str
    employeeId: str
    date: date
    status: Literal["Present", "Absent"]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


@router.get("/", response_model=List[AttendanceOut])
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
        employee_id_norm = employee_id.upper()
        query["$or"] = [{"employeeId": employee_id_norm}, {"employee_id": employee_id_norm}]
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
        employee_id_value = record.get("employeeId") or record.get("employee_id")
        if not employee_id_value:
            continue

        record_date = record.get("date")
        attendance_list.append(
            AttendanceOut.model_validate(
                {
                    "_id": str(record.get("_id")),
                    "employeeId": employee_id_value,
                    "date": record_date.date() if isinstance(record_date, datetime) else record_date,
                    "status": record.get("status"),
                    "createdAt": record.get("createdAt"),
                    "updatedAt": record.get("updatedAt"),
                }
            )
        )
    
    return attendance_list


@router.get("/employee/{employee_id}", response_model=List[AttendanceOut])
async def get_employee_attendance(employee_id: str):
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    employee_id_norm = employee_id.upper()
    records = (
        await database.attendances.find(
            {"$or": [{"employeeId": employee_id_norm}, {"employee_id": employee_id_norm}]}
        )
        .sort([("date", -1)])
        .to_list(length=None)
    )
    
    # Convert to Attendance objects
    attendance_list = []
    for record in records:
        employee_id_value = record.get("employeeId") or record.get("employee_id")
        if not employee_id_value:
            continue

        record_date = record.get("date")
        attendance_list.append(
            AttendanceOut.model_validate(
                {
                    "_id": str(record.get("_id")),
                    "employeeId": employee_id_value,
                    "date": record_date.date() if isinstance(record_date, datetime) else record_date,
                    "status": record.get("status"),
                    "createdAt": record.get("createdAt"),
                    "updatedAt": record.get("updatedAt"),
                }
            )
        )
    
    return attendance_list


@router.post("/", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
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

    employee_id = attendance_data.employee_id
    date_dt = datetime.combine(attendance_data.date, datetime.min.time())

    async def upsert_and_fetch():
        now = datetime.utcnow()
        await database.attendances.update_one(
            {
                "$or": [
                    {"employeeId": employee_id, "date": date_dt},
                    {"employee_id": employee_id, "date": date_dt},
                ]
            },
            {
                # Keep both field variants for backward compatibility with legacy indexes/data.
                "$set": {
                    "employeeId": employee_id,
                    "employee_id": employee_id,
                    "status": attendance_data.status,
                    "updatedAt": now,
                },
                "$setOnInsert": {"date": date_dt, "createdAt": now},
            },
            upsert=True,
        )
        saved_doc = await database.attendances.find_one(
            {
                "$or": [
                    {"employeeId": employee_id, "date": date_dt},
                    {"employee_id": employee_id, "date": date_dt},
                ]
            }
        )
        return saved_doc

    try:
        saved = await upsert_and_fetch()
    except Exception as e:
        error_str = str(e)
        if "duplicate key" in error_str.lower() or "E11000" in error_str:
            if "employee_id_1_date_1" in error_str or ("employee_id" in error_str and "employeeId" not in error_str):
                await ensure_attendance_indexes(database)
                try:
                    saved = await upsert_and_fetch()
                except Exception as e2:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Attendance conflict: {str(e2)}",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Attendance already exists for this employee on this date",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error marking attendance: {error_str}",
            )

    if not saved:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking attendance: could not read saved record",
        )

    employee_id_value = saved.get("employeeId") or saved.get("employee_id")
    if not employee_id_value:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error marking attendance: saved record missing employeeId",
        )

    saved_date = saved.get("date")
    return AttendanceOut.model_validate(
        {
            "_id": str(saved.get("_id")),
            "employeeId": employee_id_value,
            "date": saved_date.date() if isinstance(saved_date, datetime) else saved_date,
            "status": saved.get("status"),
            "createdAt": saved.get("createdAt"),
            "updatedAt": saved.get("updatedAt"),
        }
    )


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
        {"$or": [{"employeeId": employee_id}, {"employee_id": employee_id}]}
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
