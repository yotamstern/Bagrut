from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId

# Connect to MongoDB (running locally on default port 27017)
client = MongoClient("mongodb://localhost:27017/")

# Create (or connect to) the database
db = client["LiveStreamApp"]

# Collections
users_collection = db["users"]
streams_collection = db["streams"]

print("Connected to MongoDB!")


#register a user
def register_user(username, password):
    if users_collection.find_one({"username": username}):
        return "Username already exists!"

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        "username": username,
        "password_hash": hashed_pw,
        "streams": []
    }
    users_collection.insert_one(user)
    return f"User {username} registered successfully!"


#create a stream
def create_stream(host_username):
    user = users_collection.find_one({"username": host_username})
    if not user:
        return "User not found!"

    stream = {
        "host": user["_id"],
        "status": "active",
        "blocked_users": [],
        "connected_users": []
    }

    stream_id = streams_collection.insert_one(stream).inserted_id
    return f"Stream created with ID: {str(stream_id)}"


#allow a user to join a stream
def join_stream(username, stream_id):
    user = users_collection.find_one({"username": username})
    stream = streams_collection.find_one({"_id": ObjectId(stream_id)})

    if not user:
        return "User not found!"
    if not stream:
        return "Stream not found!"
    if user["_id"] in stream["blocked_users"]:
        return "You are blocked from this stream!"

    streams_collection.update_one(
        {"_id": ObjectId(stream_id)},
        {"$addToSet": {"connected_users": user["_id"]}}
    )

    return f"User {username} joined stream {stream_id}"


#block users from the stream
def block_user(host_username, stream_id, user_to_block):
    host = users_collection.find_one({"username": host_username})
    stream = streams_collection.find_one({"_id": ObjectId(stream_id)})
    blocked_user = users_collection.find_one({"username": user_to_block})

    if not host or not stream or not blocked_user:
        return "Invalid user or stream ID"

    if stream["host"] != host["_id"]:
        return "Only the host can block users!"

    streams_collection.update_one(
        {"_id": ObjectId(stream_id)},
        {"$addToSet": {"blocked_users": blocked_user["_id"]}}
    )

    return f"User {user_to_block} has been blocked from stream {stream_id}"
