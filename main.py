import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db, close_db, get_db_status, get_last_db_error
from routers import employees, attendance, auth

PORT = int(os.getenv("PORT", 5000))
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hrms_lite")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        # For development, continue even if MongoDB is not available
        # In production, you might want to exit the process
    
    yield
    
    # Shutdown
    await close_db()


app = FastAPI(
    title="HRMS Lite API",
    description="HRMS Lite Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(attendance.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db_status = await get_db_status()
    return {
        "status": "OK",
        "message": "Server is running",
        "database": "Connected" if db_status else "Disconnected",
        "databaseError": None if db_status else get_last_db_error(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
