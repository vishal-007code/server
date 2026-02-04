import os
from beanie import init_beanie

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Failed to import Motor (the async MongoDB driver). This is usually caused by an incompatible "
        "`pymongo` version.\n\n"
        "Fix (recommended):\n"
        "  cd server\n"
        "  py -3.11 -m venv .venv\n"
        "  .\\.venv\\Scripts\\Activate.ps1\n"
        "  python -m pip install -U pip\n"
        "  pip install -r requirements.txt\n\n"
        "Then re-run:\n"
        "  python main.py\n\n"
        f"Original import error: {e!r}"
    ) from e
from models.employee import Employee
from models.attendance import Attendance
from models.user import User

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hrms_lite")
# Extract database name from URI
if "mongodb+srv://" in MONGODB_URI or "mongodb://" in MONGODB_URI:
    # Extract database name from URI (format: mongodb://.../database_name?options)
    uri_parts = MONGODB_URI.split("/")
    if len(uri_parts) > 3:
        db_part = uri_parts[-1].split("?")[0]  # Remove query parameters
        DATABASE_NAME = db_part if db_part and db_part.strip() else "hrms_lite"
    else:
        DATABASE_NAME = "hrms_lite"
else:
    DATABASE_NAME = "hrms_lite"

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
    """Initialize MongoDB connection and Beanie"""
    global client, database, last_db_error
    
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        
        # Test connection with authentication
        await client.admin.command('ping')

        # One-time migration: fix old attendance index if present
        await ensure_attendance_indexes(database)
        
        await init_beanie(
            database=database,
            document_models=[Employee, Attendance, User]
        )
        
        last_db_error = None
        print("Connected to MongoDB")
        return database
    except Exception as e:
        error_msg = str(e)
        last_db_error = error_msg
        print(f"\n{'='*60}")
        print("MongoDB connection error:")
        print(f"{error_msg}")
        print(f"\nCurrent MONGODB_URI: {MONGODB_URI}")
        print(f"Database name: {DATABASE_NAME}")
        print(f"\n{'='*60}")
        print("To fix authentication issues:")
        print("  1. Set MONGODB_URI with credentials:")
        print("     export MONGODB_URI='mongodb://username:password@localhost:27017/hrms_lite'")
        print("\n  2. OR for MongoDB Atlas:")
        print("     export MONGODB_URI='mongodb+srv://username:password@cluster.mongodb.net/hrms_lite'")
        print("\n  3. OR disable MongoDB authentication (development only)")
        print(f"{'='*60}\n")
        # Reset database to None on error
        database = None
        # Don't raise - let the server start but API calls will fail
        # This allows the server to run and show the error message
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
