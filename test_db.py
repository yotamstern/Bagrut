from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["LiveStreamApp"]
users_collection = db["users"]
streams_collection = db["streams"]


# Function to create a test user
def create_test_user(username, password):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        print(f"User '{username}' already exists!")
        return existing_user["_id"]

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        "username": username,
        "password_hash": hashed_pw,
        "streams": []
    }
    user_id = users_collection.insert_one(user).inserted_id
    print(f"Created user: {username} (ID: {user_id})")
    return user_id


# Function to create a test stream
def create_test_stream(host_id):
    stream = {
        "host": host_id,
        "status": "active",
        "blocked_users": [],
        "connected_users": []
    }

    stream_id = streams_collection.insert_one(stream).inserted_id
    print(f"Created stream (ID: {stream_id})")
    return stream_id


# Function to join a stream
def join_stream(user_id, stream_id):
    stream = streams_collection.find_one({"_id": ObjectId(stream_id)})

    if user_id in stream["blocked_users"]:
        print("User is blocked from the stream!")
        return

    streams_collection.update_one(
        {"_id": ObjectId(stream_id)},
        {"$addToSet": {"connected_users": user_id}}
    )
    print(f"User {user_id} joined stream {stream_id}")


# Function to block a user
def block_user(host_id, stream_id, user_to_block):
    stream = streams_collection.find_one({"_id": ObjectId(stream_id)})

    if stream["host"] != host_id:
        print("Only the host can block users!")
        return

    streams_collection.update_one(
        {"_id": ObjectId(stream_id)},
        {"$addToSet": {"blocked_users": user_to_block}}
    )
    print(f"User {user_to_block} has been blocked from stream {stream_id}")


# Function to list active streams
def list_active_streams():
    streams = streams_collection.find({"status": "active"})
    print("\nActive Streams:")
    for stream in streams:
        print(f"Stream ID: {stream['_id']}, Host: {stream['host']}")


# TESTING THE DATABASE
if __name__ == "__main__":
    # Create test users
    host_id = create_test_user("host_user", "host123")
    user_id = create_test_user("test_user", "test123")

    # Create a test stream
    stream_id = create_test_stream(host_id)

    # User joins the stream
    join_stream(user_id, stream_id)

    # Block the user
    block_user(host_id, stream_id, user_id)

    # List active streams
    list_active_streams()
