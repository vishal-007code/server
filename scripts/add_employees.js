// MongoDB shell script to add 50 employees
// Run with: mongosh <your-connection-string> < scripts/add_employees.js
// Or: mongosh "mongodb+srv://..." --file scripts/add_employees.js

use hrms_lite;

// Sample data arrays
const firstNames = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica", 
                   "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel", 
                   "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy", 
                   "Donald", "Angela", "Steven", "Lisa", "Paul", "Nancy", "Andrew", "Karen",
                   "Joshua", "Betty", "Kenneth", "Helen", "Kevin", "Sandra", "Brian", "Donna",
                   "George", "Carol", "Edward", "Ruth", "Ronald", "Sharon", "Timothy", "Laura",
                   "Jason", "Emily", "Jeffrey", "Kimberly"];

const lastNames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
                  "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
                  "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen",
                  "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
                  "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"];

const departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", 
                    "IT", "Customer Support", "Product", "Design"];

const domains = ["example.com", "test.com", "demo.com", "sample.org", "mail.com"];

// Generate 50 employees
const employees = [];

for (let i = 0; i < 50; i++) {
  const firstName = firstNames[i % firstNames.length];
  const lastName = lastNames[i % lastNames.length];
  const fullName = `${firstName} ${lastName}`;
  const employeeId = `EMP${String(i + 1).padStart(3, '0')}`;
  const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}${i}@${domains[i % domains.length]}`;
  const department = departments[i % departments.length];
  
  employees.push({
    employeeId: employeeId,
    fullName: fullName,
    email: email.toLowerCase(),
    department: department,
    createdAt: new Date(),
    updatedAt: new Date()
  });
}

// Insert employees
try {
  const result = db.employees.insertMany(employees);
  print(`✅ Successfully inserted ${result.insertedCount} employees`);
  print(`\nSample employees:`);
  employees.slice(0, 5).forEach((emp, idx) => {
    print(`  ${idx + 1}. ${emp.employeeId} - ${emp.fullName} (${emp.email}) - ${emp.department}`);
  });
  if (employees.length > 5) {
    print(`  ... and ${employees.length - 5} more employees`);
  }
} catch (error) {
  if (error.code === 11000) {
    print("⚠️  Some employees already exist (duplicate key error)");
    print("   Trying to insert individually...");
    
    let inserted = 0;
    let skipped = 0;
    
    employees.forEach(emp => {
      try {
        db.employees.insertOne(emp);
        inserted++;
      } catch (e) {
        if (e.code === 11000) {
          skipped++;
        } else {
          print(`Error inserting ${emp.employeeId}: ${e.message}`);
        }
      }
    });
    
    print(`✅ Inserted ${inserted} new employees, skipped ${skipped} duplicates`);
  } else {
    print(`❌ Error: ${error.message}`);
  }
}
