import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user import User
from auth import get_password_hash


MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI environment variable is not set")

DATABASE_NAME = os.getenv("MONGODB_DB", "hrms_lite")


async def add_users():
    try:
        client = AsyncIOMotorClient(MONGODB_URI,tls=True,tlsAllowInvalidCertificates=True)
        database = client[DATABASE_NAME]

        await init_beanie(database=database, document_models=[User])

        print("Connected to MongoDB")
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

        domains = ["example.com", "test.com", "demo.com", "sample.org", "mail.com"]
        default_password = "password123"

        users_to_insert = []

        for i in range(50):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{domains[i % len(domains)]}"

            if await User.find_one(User.email == email):
                continue

            users_to_insert.append(
                User(
                    email=email,
                    password=get_password_hash(default_password),
                    full_name=f"{first_name} {last_name}",
                )
            )

        if users_to_insert:
            await User.insert_many(users_to_insert)
            print(f"✅ Added {len(users_to_insert)} users")
            print("Default password for all users: password123")
        else:
            print("ℹ️ No new users to insert")

        client.close()

    except Exception as e:
        print("Error adding users:", e)
        raise


if __name__ == "__main__":
    asyncio.run(add_users())
