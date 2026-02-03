import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.employee import Employee
from models.attendance import Attendance
from models.user import User

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://vishalvats044_db_user:fLZh4q5g84WuVisK@ethera.rmz0zgv.mongodb.net/hrms_lite?appName=ethera")
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

async def init_db():
    """Initialize MongoDB connection and Beanie"""
    global client, database
    
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        
        # Test connection with authentication
        await client.admin.command('ping')
        
        await init_beanie(
            database=database,
            document_models=[Employee, Attendance, User]
        )
        
        print("Connected to MongoDB")
        return database
    except Exception as e:
        error_msg = str(e)
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
