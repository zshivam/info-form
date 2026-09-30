# ==============================================================================
# Info Form API - Serverless FastAPI Backend for Vercel
# ==============================================================================

import os
import re
import uuid
import base64
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

app = FastAPI(title="inFOrm Directory Hub API", version="1.0.0")
handler = app

# ------------------------------------------------------------------------------
# 1. CORS Configuration
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 2. Database Connection & Helpers
# ------------------------------------------------------------------------------
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "info_form_db")

_client = None
_db = None
_use_memory = False
_memory_records = []

def init_mongo():
    global _client, _db, _use_memory
    if not MONGODB_URI:
        _use_memory = True
        return None

    try:
        if _db is None and not _use_memory:
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                socketTimeoutMS=2000
            )
            _client.admin.command('ping')
            _db = _client[DB_NAME]
            print("Successfully connected to MongoDB Atlas!")
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
        "id": str(doc.get("_id", "")),
        "name": doc.get("name", ""),
        "category": doc.get("category", "General"),
        "contact": str(doc.get("contact", "")),
        "email": doc.get("email"),
        "address": doc.get("address", ""),
        "notes": doc.get("notes"),
        "image": doc.get("image", ""),
        "created_at": doc.get("created_at")
    }

# ------------------------------------------------------------------------------
# 3. In-Memory Storage Fallback (Zero-Config local / preview mode)
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# 4. API Endpoints (in logical order: Health -> Submit -> List -> Delete)
# ------------------------------------------------------------------------------

# Root & Healthcheck
@app.get("/")
@app.get("/api")
@app.get("/api/")
@app.get("/api/health")
def health_check():
    using_memory = not MONGODB_URI or _use_memory
    return {
        "status": "healthy",
        "service": "inFOrm Directory API",
        "database": "in-memory (configure MONGODB_URI on Vercel to persist)" if using_memory else "MongoDB Atlas",
        "endpoints": {
            "health": "GET /api/health",
            "submit": "POST /api/submit or /submit",
            "records": "GET /api/records or /records",
            "delete": "DELETE /api/records/{id} or /records/{id}"
        }
    }

@app.get("/favicon.ico")
def favicon():
    return {}

# Create Record (Submit)
@app.post("/submit")
@app.post("/submit/")
@app.post("/api/submit")
@app.post("/api/submit/")
def submit_form(
    name: str = Form(...),
    category: str = Form("General"),
    contact: str = Form(...),
    email: str = Form(None),
    address: str = Form(""),
    notes: str = Form(None),
    image: UploadFile = File(None),
    image_url: str = Form(None)
):
    try:
        final_image = ""

        # Handle uploaded file
        if image and hasattr(image, 'file'):
            image_bytes = image.file.read()
            if image_bytes:
                content_type = image.content_type or "image/jpeg"
                base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
                final_image = f"data:{content_type};base64,{base64_encoded}"

        # Handle direct image URL fallback
        if not final_image and image_url:
            final_image = image_url.strip()

        record_doc = {
            "name": name.strip(),
            "category": category.strip() if category and category.strip() else "General",
            "contact": contact.strip(),
            "email": email.strip() if email and email.strip() else None,
            "address": address.strip(),
            "notes": notes.strip() if notes and notes.strip() else None,
            "image": final_image,
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

# Read Records (List & Filter)
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
                    if q in (r.get("name") or "").lower()
                    or q in (r.get("address") or "").lower()
                    or q in str(r.get("contact", "")).lower()
                    or q in (r.get("email") or "").lower()
                    or q in (r.get("notes") or "").lower()
                    or q in (r.get("category") or "").lower()
                ]
            return [record_helper(doc) for doc in raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {str(e)}")

# Delete Record
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

