"""
Script to add 50 sample users to the database
Run with: python3 scripts/add_users.py
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user import User
from auth import get_password_hash

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


async def add_users():
    """Add 50 sample users to the database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[User])
        
        print(f"Connected to database: {DATABASE_NAME}")
        
        # Generate 50 users
        users_data = []
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
        
        domains = ["example.com", "test.com", "demo.com", "sample.org", "mail.com"]
        
        for i in range(50):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            full_name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}{i}@{domains[i % len(domains)]}"
            password = "password123"  # Default password for all users
            
            # Check if user already exists
            existing_user = await User.find_one(User.email == email.lower())
            if existing_user:
                print(f"User {email} already exists, skipping...")
                continue
            
            user = User(
                email=email.lower(),
                password=get_password_hash(password),
                full_name=full_name
            )
            users_data.append(user)
        
        # Insert all users
        if users_data:
            await User.insert_many(users_data)
            print(f"\n✅ Successfully added {len(users_data)} users to the database!")
            print(f"\nDefault password for all users: password123")
            print(f"\nSample users created:")
            for i, user in enumerate(users_data[:5], 1):
                print(f"  {i}. {user.full_name} - {user.email}")
            if len(users_data) > 5:
                print(f"  ... and {len(users_data) - 5} more users")
        else:
            print("No new users to add (all users already exist)")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(add_users())
