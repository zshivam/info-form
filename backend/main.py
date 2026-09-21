from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
from bson import ObjectId
import re
import os
import uuid
import base64

import database
from models import record_helper

app = FastAPI(title="Info Form API")

# Allow all origins for seamless Vercel previews and deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads" if "VERCEL" in os.environ else "uploads")
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    pass


@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    using_memory = database.is_using_memory()
    return {
        "status": "healthy",
        "database": "in-memory (set MONGODB_URI to persist)" if using_memory else "MongoDB Atlas",
        "message": "Info Form API is operational on Vercel",
        "endpoints": {
            "submit": "POST /submit/ or POST /api/submit/",
            "records": "GET /records/ or GET /api/records/",
            "delete": "DELETE /records/{id}/ or DELETE /api/records/{id}/"
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

        # Convert image to Base64 data URI to guarantee 100% persistence on Vercel Serverless
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

        col = database.get_collection("records")
        if col is not None:
            res = col.insert_one(record_doc)
            rec_id = str(res.inserted_id)
        else:
            rec_id = database.memory_insert(record_doc)

        return {"message": "Data saved successfully", "record_id": rec_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save record: {str(e)}")

@app.get("/records")
@app.get("/records/")
@app.get("/api/records")
@app.get("/api/records/")
def get_records(
    category: str = None,
    search: str = None
):
    try:
        col = database.get_collection("records")
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
            # In-memory store fallback
            raw = database.memory_find({"category": category} if category and category != "All" else None)
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
        col = database.get_collection("records")
        if col is not None:
            if not ObjectId.is_valid(record_id):
                raise HTTPException(status_code=400, detail="Invalid record ID format")

            res = col.delete_one({"_id": ObjectId(record_id)})
            if res.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Record not found")
        else:
            deleted = database.memory_delete(record_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Record not found")

        return {"message": "Record deleted successfully", "id": record_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")
