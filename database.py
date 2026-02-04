import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.employee import Employee
from models.attendance import Attendance
from models.user import User


MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI environment variable is not set")

DATABASE_NAME = os.getenv("MONGODB_DB", "hrms_lite")


client = None
database = None
last_db_error = None



async def ensure_attendance_indexes(db):
    """
    Ensure the Attendance collection uses the correct unique index.

    Some earlier versions created a unique index on (employee_id, date). Since most
    documents don't have an employee_id field, MongoDB treats it as null, which can
    cause E11000 duplicate key errors when multiple employees mark attendance for
    the same date. This function drops the old index (if present) and creates the
    correct unique index on (employeeId, date).
    """
    collection = db["attendances"]

    # Drop the old incorrect index if it exists
    try:
        await collection.drop_index("employee_id_1_date_1")
        print("Dropped old index: employee_id_1_date_1")
    except Exception:
        pass

    # Ensure the correct index exists (idempotent)
    try:
        await collection.create_index(
            [("employeeId", 1), ("date", 1)],
            unique=True,
            name="employeeId_1_date_1",
        )
    except Exception as e:
        # Don't block server startup; attendance endpoints can still function.
        print(f"Warning: failed to ensure attendance index: {e}")


async def init_db():
    global client, database, last_db_error

    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]

        await client.admin.command("ping")

        await ensure_attendance_indexes(database)

        await init_beanie(
            database=database,
            document_models=[Employee, Attendance, User],
        )

        last_db_error = None
        print("Connected to MongoDB")
        return database

    except Exception as e:
        last_db_error = str(e)
        database = None
        print("MongoDB connection error:", last_db_error)
        return None


async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

async def get_db_status():
    """Check if database is connected"""
    try:
        if client:
            await client.admin.command('ping')
            return True
    except:
        pass
    return False

def get_database():
    """Get the database instance"""
    global database
    return database

def get_last_db_error():
    """Get last database connection error (if any)."""
    global last_db_error
    return last_db_error
