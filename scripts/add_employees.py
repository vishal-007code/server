import asyncio
import sys
import os
import certifi


from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.employee import Employee

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI environment variable is not set")

DATABASE_NAME = os.getenv("MONGODB_DB", "hrms_lite")


async def add_employees():
    try:
        client = AsyncIOMotorClient(MONGODB_URI,tls=True,tlsCAFile=certifi.where(),serverSelectionTimeoutMS=30000)
        database = client[DATABASE_NAME]

        await init_beanie(database=database, document_models=[Employee])

        print(f"Connected to MongoDB")
        print(f"Database name: {DATABASE_NAME}")

        first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
            "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel",
            "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy",
            "Donald", "Angela", "Steven", "Lisa", "Paul", "Nancy", "Andrew", "Karen",
            "Joshua", "Betty", "Kenneth", "Helen", "Kevin", "Sandra", "Brian", "Donna",
            "George", "Carol", "Edward", "Ruth", "Ronald", "Sharon", "Timothy", "Laura",
            "Jason", "Emily", "Jeffrey", "Kimberly"
        ]

        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
            "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen",
            "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
            "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
        ]

        departments = [
            "Engineering", "Sales", "Marketing", "HR", "Finance", "Operations",
            "IT", "Customer Support", "Product", "Design", "Legal", "Research"
        ]

        domains = ["example.com", "test.com", "demo.com", "sample.org", "mail.com"]

        employees_to_insert = []

        for i in range(50):
            employee_id = f"EMP{str(i + 1).zfill(3)}"
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{domains[i % len(domains)]}"
            department = departments[i % len(departments)]

            if await Employee.find_one(Employee.employee_id == employee_id):
                continue

            if await Employee.find_one(Employee.email == email):
                continue

            employees_to_insert.append(
                Employee(
                    employee_id=employee_id,
                    full_name=f"{first_name} {last_name}",
                    email=email,
                    department=department,
                )
            )

        if employees_to_insert:
            await Employee.insert_many(employees_to_insert)
            print(f"✅ Added {len(employees_to_insert)} employees")
        else:
            print("ℹ️ No new employees to insert")

        client.close()

    except Exception as e:
        print("Error adding employees:", e)
        raise


if __name__ == "__main__":
    asyncio.run(add_employees())
