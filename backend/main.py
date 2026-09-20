from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
import models
import os
import uuid
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Info Form API")

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

# Serve uploaded files if directory exists
if os.path.exists(UPLOAD_FOLDER):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {
        "status": "healthy",
        "message": "Info Form API is operational on Vercel Serverless",
        "endpoints": {
            "submit": "POST /submit/ or POST /api/submit/",
            "records": "GET /records/ or GET /api/records/",
            "uploads": "GET /uploads/{filename}"
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
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        image_bytes = image.file.read()

        # Check if running in Serverless environment or save as data URI to guarantee persistence
        # Data URI allows image to be stored directly in DB, 100% resilient across serverless instances
        import base64
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

        # Use image_data_uri so images display permanently on Vercel
        form_data = models.FormData(
            name=name,
            address=address,
            contact=contact,
            email=email if email and email.strip() else None,
            category=category if category and category.strip() else "General",
            notes=notes if notes and notes.strip() else None,
            image=image_data_uri
        )
        db.add(form_data)
        db.commit()
        db.refresh(form_data)

        return {"message": "Data saved successfully", "record_id": form_data.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save record: {str(e)}")

@app.get("/records/")
@app.get("/api/records/")
def get_records(
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.FormData)
    if category and category != "All":
        query = query.filter(models.FormData.category == category)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.FormData.name.ilike(search_pattern)) |
            (models.FormData.address.ilike(search_pattern)) |
            (models.FormData.email.ilike(search_pattern)) |
            (models.FormData.notes.ilike(search_pattern))
        )
    return query.order_by(models.FormData.id.desc()).all()

@app.delete("/records/{record_id}/")
@app.delete("/api/records/{record_id}/")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.FormData).filter(models.FormData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Optionally remove local file if present
    if record.image and not record.image.startswith("data:"):
        image_path = os.path.join(UPLOAD_FOLDER, record.image)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass

    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully", "id": record_id}



