from fastapi import FastAPI, Depends, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models
import os
import uvicorn
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # removed /info-form
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit/")
def submit_form(
    name: str = Form(...),
    address: str = Form(...),
    contact: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded image to disk
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())

    # Save data including image filename to DB (only filename)
    form_data = models.FormData(
        name=name,
        address=address,
        contact=contact,
        image=image.filename
    )
    db.add(form_data)
    db.commit()

    return {"message": "Data saved successfully"}

@app.get("/records/")
def get_records(db: Session = Depends(get_db)):
    return db.query(models.FormData).all()
