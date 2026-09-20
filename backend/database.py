import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB Connection URI (Supports MONGODB_URI or MONGO_URI)
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "info_form_db")

_client = None
_db = None
_use_memory = False
_memory_records = []

def init_mongo():
    global _client, _db, _use_memory
    if not MONGODB_URI:
        print("Note: MONGODB_URI not provided. Running with in-memory storage fallback.")
        _use_memory = True
        return None

    try:
        if _db is None and not _use_memory:
            safe_uri = MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else MONGODB_URI
            print(f"Connecting to MongoDB: {safe_uri} (database: {DB_NAME})")
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=4000)
            _client.admin.command('ping')
            _db = _client[DB_NAME]
            print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Warning: MongoDB connection failed ({e}). Using in-memory fallback so app runs without crashing.")
        _use_memory = True
        return None
    return _db

def get_database():
    return init_mongo()

def is_using_memory():
    global _use_memory
    init_mongo()
    return _use_memory

def get_collection(collection_name="records"):
    db = get_database()
    if db is not None:
        return db[collection_name]
    return None

# Memory store helpers (guarantees app runs even before MONGODB_URI is added in Vercel settings)
def memory_insert(record_doc):
    record_id = uuid.uuid4().hex[:12]
    doc = dict(record_doc)
    doc["_id"] = record_id
    _memory_records.insert(0, doc)
    return record_id

def memory_find(query=None):
    results = list(_memory_records)
    if not query:
        return results
    if "category" in query and query["category"] != "All":
        results = [r for r in results if r.get("category") == query["category"]]
    return results

def memory_delete(record_id):
    global _memory_records
    initial_len = len(_memory_records)
    _memory_records = [r for r in _memory_records if str(r.get("_id")) != str(record_id)]
    return len(_memory_records) < initial_len
