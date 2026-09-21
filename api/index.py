from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
import re
import os
import uuid
import base64
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = FastAPI(title="Info Form API (Vercel Serverless)")

# Enable CORS for frontend on Vercel and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "info_form_db")

_client = None
_db = None
_use_memory = False

# Seed realistic dummy records for localhost testing when no live DB is connected
DUMMY_RECORDS = [
    {
        "_id": "demo-1",
        "name": "Alex Rivera",
        "address": "404 Silicon Ave, San Francisco, CA",
        "contact": 9876543210,
        "email": "alex.rivera@techflow.io",
        "category": "Team Member",
        "notes": "Lead Full-Stack Architect & UI Designer",
        "image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
        "created_at": "2026-09-20T10:00:00Z"
    },
    {
        "_id": "demo-2",
        "name": "Sophia Chen",
        "address": "72 Park Row, New York, NY",
        "contact": 9123456780,
        "email": "sophia.chen@vanguard.co",
        "category": "Client",
        "notes": "Enterprise Partner - Key Account Director",
        "image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80",
        "created_at": "2026-09-19T14:30:00Z"
    },
    {
        "_id": "demo-3",
        "name": "Marcus Vance",
        "address": "15 King Street, Austin, TX",
        "contact": 9012345678,
        "email": "marcus.vance@apexlogistics.com",
        "category": "Vendor",
        "notes": "Logistics Coordinator & Equipment Specialist",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
        "created_at": "2026-09-18T09:15:00Z"
    }
]
_memory_records = list(DUMMY_RECORDS)

def init_mongo():
    global _client, _db, _use_memory
    if not MONGODB_URI:
        _use_memory = True
        return None

    try:
        if _db is None and not _use_memory:
            safe_uri = MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else MONGODB_URI
            print(f"Connecting to MongoDB: {safe_uri}")
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=4000)
            _client.admin.command('ping')
            _db = _client[DB_NAME]
            print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB connection fallback: {e}")
        _use_memory = True
        return None
    return _db

def get_collection(name="records"):
    db = init_mongo()
    return db[name] if db is not None else None

def record_helper(doc):
    if not doc:
        return {}
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name", ""),
        "address": doc.get("address", ""),
        "contact": doc.get("contact", ""),
        "email": doc.get("email"),
        "category": doc.get("category", "General"),
        "notes": doc.get("notes"),
        "image": doc.get("image", ""),
        "created_at": doc.get("created_at")
    }

# In-memory storage fallback to ensure app runs immediately even before MONGODB_URI is configured
def memory_insert(record_doc):
    rec_id = uuid.uuid4().hex[:12]
    doc = dict(record_doc)
    doc["_id"] = rec_id
    _memory_records.insert(0, doc)
    return rec_id

def memory_find(category=None):
    if category and category != "All":
        return [r for r in _memory_records if r.get("category") == category]
    return list(_memory_records)

def memory_delete(rec_id):
    global _memory_records
    before = len(_memory_records)
    _memory_records = [r for r in _memory_records if str(r.get("_id")) != str(rec_id)]
    return len(_memory_records) < before

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    using_memory = not MONGODB_URI or _use_memory
    return {
        "status": "healthy",
        "database": "in-memory (add MONGODB_URI in Vercel to persist permanently)" if using_memory else "MongoDB Atlas",
        "message": "Info Form API is operational on Vercel!",
        "endpoints": {
            "submit": "POST /submit or /api/submit",
            "records": "GET /records or /api/records",
            "delete": "DELETE /records/{id} or /api/records/{id}"
        }
    }

@app.post("/submit")
@app.post("/submit/")
@app.post("/api/submit")
@app.post("/api/submit/")
def submit_form(
    name: str = Form(...),
    address: str = Form(""),
    contact: int = Form(...),
    email: str = Form(None),
    category: str = Form("General"),
    notes: str = Form(None),
    image: UploadFile = File(...)
):
    try:
        image_bytes = image.file.read()
        content_type = image.content_type or "image/jpeg"
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        image_data_uri = f"data:{content_type};base64,{base64_encoded}"

        record_doc = {
            "name": name,
            "address": address,
            "contact": contact,
            "email": email.strip() if email and email.strip() else None,
            "category": category.strip() if category and category.strip() else "General",
            "notes": notes.strip() if notes and notes.strip() else None,
            "image": image_data_uri,
            "created_at": datetime.utcnow().isoformat()
        }

        col = get_collection("records")
        if col is not None:
            res = col.insert_one(record_doc)
            rec_id = str(res.inserted_id)
        else:
            rec_id = memory_insert(record_doc)

        return {"message": "Data saved successfully", "record_id": rec_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save record: {str(e)}")

@app.get("/records")
@app.get("/records/")
@app.get("/api/records")
@app.get("/api/records/")
def get_records(category: str = None, search: str = None):
    try:
        col = get_collection("records")
        if col is not None:
            query = {}
            if category and category != "All":
                query["category"] = category
            if search and search.strip():
                pattern = re.compile(re.escape(search.strip()), re.IGNORECASE)
                query["$or"] = [
                    {"name": pattern},
                    {"address": pattern},
                    {"email": pattern},
                    {"notes": pattern},
                    {"category": pattern}
                ]
            cursor = col.find(query).sort("_id", -1)
            return [record_helper(doc) for doc in cursor]
        else:
            raw = memory_find(category)
            if search and search.strip():
                q = search.strip().lower()
                raw = [
                    r for r in raw
                    if q in r.get("name", "").lower()
                    or q in r.get("address", "").lower()
                    or q in str(r.get("contact", "")).lower()
                    or q in (r.get("email") or "").lower()
                    or q in (r.get("notes") or "").lower()
                    or q in r.get("category", "").lower()
                ]
            return [record_helper(doc) for doc in raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {str(e)}")

@app.delete("/records/{record_id}")
@app.delete("/records/{record_id}/")
@app.delete("/api/records/{record_id}")
@app.delete("/api/records/{record_id}/")
def delete_record(record_id: str):
    try:
        col = get_collection("records")
        if col is not None:
            if not ObjectId.is_valid(record_id):
                raise HTTPException(status_code=400, detail="Invalid record ID format")
            res = col.delete_one({"_id": ObjectId(record_id)})
            if res.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Record not found")
        else:
            if not memory_delete(record_id):
                raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record deleted successfully", "id": record_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")
