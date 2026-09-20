from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime
from bson import ObjectId
import re
import os
import uuid
import base64

import database
from models import record_helper

app = FastAPI(title="Info Form API (MongoDB)")

# Allow frontend origins: production, Vercel previews, and local development
allowed_origins = [
    "https://info-form-9q9n.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    allowed_origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads" if "VERCEL" in os.environ else "uploads")
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    pass

# Mount static files folder if directory exists
if os.path.exists(UPLOAD_FOLDER):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {
        "status": "healthy",
        "database": "MongoDB",
        "message": "Info Form API is operational with MongoDB",
        "endpoints": {
            "submit": "POST /submit/ or POST /api/submit/",
            "records": "GET /records/ or GET /api/records/",
            "delete": "DELETE /records/{id}/ or DELETE /api/records/{id}/"
        }
    }

@app.post("/submit/")
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

        # Encode image to Base64 data URI so image is stored directly in MongoDB document
        # This guarantees 100% permanence and eliminates ephemeral disk issues on Vercel Serverless
        content_type = image.content_type or "image/jpeg"
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        image_data_uri = f"data:{content_type};base64,{base64_encoded}"

        # Also write to local uploads folder if available
        original_ext = Path(image.filename).suffix if image.filename else ".jpg"
        if not original_ext:
            original_ext = ".jpg"
        unique_filename = f"{uuid.uuid4().hex}{original_ext}"
        try:
            image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
        except Exception:
            pass

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
        res = col.insert_one(record_doc)

        return {"message": "Data saved successfully", "record_id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save record to MongoDB: {str(e)}")

@app.get("/records/")
@app.get("/api/records/")
def get_records(
    category: str = None,
    search: str = None
):
    try:
        col = database.get_collection("records")
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
        records = [record_helper(doc) for doc in cursor]
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records from MongoDB: {str(e)}")

@app.delete("/records/{record_id}/")
@app.delete("/api/records/{record_id}/")
def delete_record(record_id: str):
    try:
        if not ObjectId.is_valid(record_id):
            raise HTTPException(status_code=400, detail="Invalid record ID format")

        col = database.get_collection("records")
        res = col.delete_one({"_id": ObjectId(record_id)})

        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Record not found")

        return {"message": "Record deleted successfully", "id": record_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")
