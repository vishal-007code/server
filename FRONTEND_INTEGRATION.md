# Frontend API Integration Guide

## Base URL
```
http://localhost:5000
```

---

## Step 1: Setup API Configuration

### Create API configuration file (e.g., `api.js` or `api.ts`)

**JavaScript:**
```javascript
const API_BASE_URL = 'http://localhost:5000';

export default API_BASE_URL;
```

**TypeScript:**
```typescript
const API_BASE_URL: string = 'http://localhost:5000';
export default API_BASE_URL;
```

**Using Environment Variables:**
```javascript
// .env file
REACT_APP_API_URL=http://localhost:5000

// In your code
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

---

## Step 2: Employee APIs Integration

### 2.1 Get All Employees
```javascript
const getEmployees = async () => {
  const response = await fetch(`${API_BASE_URL}/api/employees`);
  const data = await response.json();
  return data;
};
```

### 2.2 Get Single Employee
```javascript
const getEmployee = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/employees/${id}`);
  const data = await response.json();
  return data;
};
```

### 2.3 Create Employee
```javascript
const createEmployee = async (employeeData) => {
  const response = await fetch(`${API_BASE_URL}/api/employees`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      employeeId: employeeData.employeeId,
      fullName: employeeData.fullName,
      email: employeeData.email,
      department: employeeData.department
    })
  });
  const data = await response.json();
  return data;
};
```

### 2.4 Delete Employee
```javascript
const deleteEmployee = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/employees/${id}`, {
    method: 'DELETE'
  });
  const data = await response.json();
  return data;
};
```

---

## Step 3: Attendance APIs Integration

### 3.1 Get All Attendance Records
```javascript
// Get all
const getAllAttendance = async () => {
  const response = await fetch(`${API_BASE_URL}/api/attendance`);
  const data = await response.json();
  return data;
};

// Filter by employeeId
const getAttendanceByEmployee = async (employeeId) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance?employeeId=${employeeId}`);
  const data = await response.json();
  return data;
};

// Filter by date
const getAttendanceByDate = async (date) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance?date=${date}`);
  const data = await response.json();
  return data;
};

// Filter by both
const getAttendanceFiltered = async (employeeId, date) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance?employeeId=${employeeId}&date=${date}`);
  const data = await response.json();
  return data;
};
```

### 3.2 Get Employee Attendance
```javascript
const getEmployeeAttendance = async (employeeId) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance/employee/${employeeId}`);
  const data = await response.json();
  return data;
};
```

### 3.3 Mark Attendance
```javascript
const markAttendance = async (attendanceData) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      employeeId: attendanceData.employeeId,
      date: attendanceData.date, // Format: YYYY-MM-DD
      status: attendanceData.status // 'Present' or 'Absent'
    })
  });
  const data = await response.json();
  return data;
};
```

### 3.4 Get Attendance Statistics
```javascript
const getAttendanceStats = async (employeeId) => {
  const response = await fetch(`${API_BASE_URL}/api/attendance/stats/${employeeId}`);
  const data = await response.json();
  return data;
};
```

---

## Step 4: Error Handling

### Add error handling wrapper
```javascript
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// Usage
const result = await apiCall(`${API_BASE_URL}/api/employees`);
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error);
}
```

---

## Step 5: Using with Axios (Alternative)

### Install Axios
```bash
npm install axios
```

### Create Axios instance
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Employees
export const getEmployees = () => api.get('/api/employees');
export const getEmployee = (id) => api.get(`/api/employees/${id}`);
export const createEmployee = (data) => api.post('/api/employees', data);
export const deleteEmployee = (id) => api.delete(`/api/employees/${id}`);

// Attendance
export const getAttendance = (params) => api.get('/api/attendance', { params });
export const getEmployeeAttendance = (employeeId) => api.get(`/api/attendance/employee/${employeeId}`);
export const markAttendance = (data) => api.post('/api/attendance', data);
export const getAttendanceStats = (employeeId) => api.get(`/api/attendance/stats/${employeeId}`);
```

---

## Step 6: React Hook Example

```javascript
import { useState, useEffect } from 'react';

const useEmployees = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/employees');
        const data = await response.json();
        setEmployees(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  return { employees, loading, error };
};

export default useEmployees;
```

---

## Step 7: Request/Response Formats

### Employee Object
```json
{
  "id": "507f1f77bcf86cd799439011",
  "employeeId": "EMP001",
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "department": "Engineering",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z"
}
```

### Attendance Object
```json
{
  "id": "507f1f77bcf86cd799439012",
  "employeeId": "EMP001",
  "date": "2024-01-01",
  "status": "Present",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z"
}
```

### Attendance Stats Object
```json
{
  "employeeId": "EMP001",
  "totalDays": 30,
  "presentDays": 25,
  "absentDays": 5
}
```

---

## Important Notes

1. **Date Format**: Use `YYYY-MM-DD` format (e.g., `2024-01-01`)
2. **Status Values**: Only `"Present"` or `"Absent"` are allowed
3. **Employee ID**: Automatically converted to uppercase
4. **Email**: Automatically converted to lowercase
5. **CORS**: Already enabled for all origins
6. **Error Responses**: Check `response.status` and `response.json()` for error details

---

## Step 8: Authentication APIs Integration

### 8.1 Signup (Register)
```javascript
const signup = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      fullName: userData.fullName
    })
  });
  const data = await response.json();
  return data; // Returns { access_token, token_type, user }
};
```

### 8.2 Login
```javascript
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      password: password
    })
  });
  const data = await response.json();
  return data; // Returns { access_token, token_type, user }
};
```

### 8.3 Get Current User (Protected Route)
```javascript
const getCurrentUser = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });
  const data = await response.json();
  return data;
};
```

### 8.4 Store Token and Use in Requests
```javascript
// After login/signup, store the token
localStorage.setItem('token', response.access_token);

// Use token in subsequent requests
const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });
};

// Example: Get employees with authentication
const getEmployees = async () => {
  const response = await fetchWithAuth(`${API_BASE_URL}/api/employees`);
  const data = await response.json();
  return data;
};
```

---

## Quick Reference

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/signup` | POST | Register new user | No |
| `/api/auth/login` | POST | Login user | No |
| `/api/auth/me` | GET | Get current user | Yes |
| `/api/employees` | GET | Get all employees | No |
| `/api/employees/{id}` | GET | Get employee by ID | No |
| `/api/employees` | POST | Create employee | No |
| `/api/employees/{id}` | DELETE | Delete employee | No |
| `/api/attendance` | GET | Get all attendance (with optional query params) | No |
| `/api/attendance/employee/{employeeId}` | GET | Get employee attendance | No |
| `/api/attendance` | POST | Mark attendance | No |
| `/api/attendance/stats/{employeeId}` | GET | Get attendance statistics | No |
| `/api/health` | GET | Health check | No |
