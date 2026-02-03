# Database Seeding Scripts

Scripts to populate the database with sample data.

## Add 50 Users

### Using Python Script (Recommended)
```bash
cd /home/kartikeybajpai/Desktop/ethara_ai_assignment_vishal_vats/server
python3 scripts/add_users.py
```

This will:
- Create 50 sample users
- Set default password: `password123` for all users
- Skip users that already exist

### Using MongoDB Shell
```bash
mongosh "mongodb+srv://vishalvats044_db_user:fLZh4q5g84WuVisK@ethera.rmz0zgv.mongodb.net/hrms_lite?appName=ethera" --file scripts/add_employees.js
```

## Add 50 Employees

### Using MongoDB Shell
```bash
mongosh "mongodb+srv://vishalvats044_db_user:fLZh4q5g84WuVisK@ethera.rmz0zgv.mongodb.net/hrms_lite?appName=ethera" --file scripts/add_employees.js
```

Or connect first, then run:
```bash
mongosh "mongodb+srv://..."
use hrms_lite
# Then paste the JavaScript code from add_employees.js
```

## Direct MongoDB Queries

### Add Users (MongoDB Shell)
```javascript
use hrms_lite;

// Single user
db.users.insertOne({
  email: "user@example.com",
  password: "$2b$12$...", // Hashed password
  fullName: "John Doe",
  createdAt: new Date(),
  updatedAt: new Date()
});

// Multiple users (50 users)
const users = [];
for (let i = 0; i < 50; i++) {
  users.push({
    email: `user${i}@example.com`,
    password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5", // Use get_password_hash in Python
    fullName: `User ${i}`,
    createdAt: new Date(),
    updatedAt: new Date()
  });
}
db.users.insertMany(users);
```

### Add Employees (MongoDB Shell)
```javascript
use hrms_lite;

// Single employee
db.employees.insertOne({
  employeeId: "EMP001",
  fullName: "John Doe",
  email: "john.doe@example.com",
  department: "Engineering",
  createdAt: new Date(),
  updatedAt: new Date()
});

// Multiple employees (50 employees)
const employees = [];
for (let i = 0; i < 50; i++) {
  employees.push({
    employeeId: `EMP${String(i + 1).padStart(3, '0')}`,
    fullName: `Employee ${i + 1}`,
    email: `employee${i}@example.com`,
    department: "Engineering",
    createdAt: new Date(),
    updatedAt: new Date()
  });
}
db.employees.insertMany(employees);
```
