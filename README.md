# HRMS Lite Backend - FastAPI

This is a FastAPI backend for the HRMS Lite application, converted from Node.js/Express.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:

**For MongoDB with authentication:**
```bash
export MONGODB_URI="mongodb://username:password@localhost:27017/hrms_lite"
export PORT=5000
```

**For MongoDB without authentication (development only):**
```bash
export MONGODB_URI="mongodb://localhost:27017/hrms_lite"
export PORT=5000
```

**For MongoDB Atlas (cloud):**
```bash
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/hrms_lite"
export PORT=5000
```

**Note:** If you're getting authentication errors, make sure your MongoDB URI includes credentials in the format: `mongodb://username:password@host:port/database`

3. Run the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## API Endpoints

### Health Check
- `GET /api/health` - Check server and database status

### Employees
- `GET /api/employees` - Get all employees
- `GET /api/employees/{id}` - Get employee by ID
- `POST /api/employees` - Create new employee
- `DELETE /api/employees/{id}` - Delete employee

### Attendance
- `GET /api/attendance` - Get all attendance records (with optional query params: `employeeId`, `date`)
- `GET /api/attendance/employee/{employeeId}` - Get attendance for specific employee
- `POST /api/attendance` - Mark attendance
- `GET /api/attendance/stats/{employeeId}` - Get attendance statistics

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## Database

The application uses MongoDB with Beanie ODM. Make sure MongoDB is running before starting the server.
