"""
Script to add 50 sample employees to the database
Run with: python3 scripts/add_employees.py
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.employee import Employee

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://vishalvats044_db_user:fLZh4q5g84WuVisK@ethera.rmz0zgv.mongodb.net/?appName=ethera")

# Extract database name
if "mongodb+srv://" in MONGODB_URI or "mongodb://" in MONGODB_URI:
    uri_parts = MONGODB_URI.split("/")
    if len(uri_parts) > 3:
        db_part = uri_parts[-1].split("?")[0]
        DATABASE_NAME = db_part if db_part else "hrms_lite"
    else:
        DATABASE_NAME = "hrms_lite"
else:
    DATABASE_NAME = "hrms_lite"


async def add_employees():
    """Add 50 sample employees to the database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[Employee])
        
        print(f"Connected to database: {DATABASE_NAME}")
        
        # Generate 50 employees
        employees_data = []
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica", 
                      "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel", 
                      "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy", 
                      "Donald", "Angela", "Steven", "Lisa", "Paul", "Nancy", "Andrew", "Karen",
                      "Joshua", "Betty", "Kenneth", "Helen", "Kevin", "Sandra", "Brian", "Donna",
                      "George", "Carol", "Edward", "Ruth", "Ronald", "Sharon", "Timothy", "Laura",
                      "Jason", "Emily", "Jeffrey", "Kimberly"]
        
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                     "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
                     "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
                     "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen",
                     "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
                     "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]
        
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", 
                      "IT", "Customer Support", "Product", "Design", "Legal", "Research"]
        
        domains = ["example.com", "test.com", "demo.com", "sample.org", "mail.com"]
        
        for i in range(50):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            full_name = f"{first_name} {last_name}"
            employee_id = f"EMP{str(i + 1).zfill(3)}"  # EMP001, EMP002, etc.
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{domains[i % len(domains)]}"
            department = departments[i % len(departments)]
            
            # Check if employee already exists
            existing_employee = await Employee.find_one(Employee.employee_id == employee_id)
            if existing_employee:
                print(f"Employee {employee_id} ({email}) already exists, skipping...")
                continue
            
            # Check if email already exists
            existing_email = await Employee.find_one(Employee.email == email.lower())
            if existing_email:
                print(f"Email {email} already exists, skipping...")
                continue
            
            employee = Employee(
                employee_id=employee_id,
                full_name=full_name,
                email=email.lower(),
                department=department
            )
            employees_data.append(employee)
        
        # Insert all employees
        if employees_data:
            await Employee.insert_many(employees_data)
            print(f"\n✅ Successfully added {len(employees_data)} employees to the database!")
            print(f"\nSample employees created:")
            for i, emp in enumerate(employees_data[:10], 1):
                print(f"  {i}. {emp.employee_id} - {emp.full_name} ({emp.email}) - {emp.department}")
            if len(employees_data) > 10:
                print(f"  ... and {len(employees_data) - 10} more employees")
        else:
            print("No new employees to add (all employees already exist)")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(add_employees())
