import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB Connection URI (Supports MONGODB_URI or MONGO_URI)
# Example for MongoDB Atlas: mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME", "info_form_db")

safe_uri = MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else MONGODB_URI
print(f"MongoDB target: {safe_uri} (database: {DB_NAME})")

_client = None
_db = None

def get_database():
    """Returns singleton MongoDB database instance"""
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _db = _client[DB_NAME]
    return _db

def get_collection(collection_name="records"):
    """Returns a collection from the database"""
    database = get_database()
    return database[collection_name]
