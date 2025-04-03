from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["LiveStreamApp"]
users_collection = db["users"]

# Fetch all users with hashed passwords
users = list(users_collection.find({}, {"_id": 0, "username": 1, "password_hash": 1}))

for user in users:
    print(f"Username: {user['username']}, Hashed Password: {user['password_hash']}")
