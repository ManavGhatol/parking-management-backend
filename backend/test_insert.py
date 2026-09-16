from pymongo import MongoClient

# 1. Local MongoDB se connect karein
client = MongoClient("mongodb://localhost:27017/")

# 2. Database aur collection set karein
db = client["parking_audit_db"]  # Using the name from your database.py
collection = db["vehicles_test"]

# 3. Ek test data insert karein
test_data = {
    "vehicle_number": "MH-27-TEST",
    "owner_name": "Manav",
    "parking_slot": 1
}

# 4. Data ko database me push karein
collection.insert_one(test_data)
print("✅ Data successfully insert ho gaya! Ab Compass check karein.")
