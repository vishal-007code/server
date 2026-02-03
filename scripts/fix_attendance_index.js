// Script to fix the attendance index
// Run with: mongosh "your-connection-string" --file scripts/fix_attendance_index.js

// Switch to the database
db = db.getSiblingDB('hrms_lite');

// Drop the old incorrect index
try {
  db.attendances.dropIndex("employee_id_1_date_1");
  print("✅ Dropped old index: employee_id_1_date_1");
} catch (e) {
  print("ℹ️  Old index doesn't exist or already dropped");
}

// Create the correct index with MongoDB field names
try {
  db.attendances.createIndex(
    { "employeeId": 1, "date": 1 },
    { unique: true, name: "employeeId_1_date_1" }
  );
  print("✅ Created correct index: employeeId_1_date_1");
} catch (e) {
  print("⚠️  Index creation error: " + e.message);
}

// List all indexes to verify
print("\nCurrent indexes on attendances collection:");
db.attendances.getIndexes().forEach(function(index) {
  print("  - " + index.name + ": " + JSON.stringify(index.key));
});
