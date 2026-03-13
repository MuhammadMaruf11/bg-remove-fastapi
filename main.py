import os
import io
import base64
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # CORS logic
from sqlalchemy.orm import Session
from rembg import remove
from dotenv import load_dotenv

# Database imports
from database.database import engine, Base, get_db
from database.models import ProcessedImage

# Environment variables load kora
load_dotenv()

# Database table auto-create kora (jodi na thake)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Background Remover API")

# --- CORS Middleware (Mobile/Frontend Connection er jonno) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---
def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- API Endpoints ---

@app.get("/")
def root():
    """Server status check korar jonno"""
    return {
        "status": "online",
        "message": "Background Remover API is running",
        "docs": "/docs"
    }

@app.get("/images")
async def get_images(db: Session = Depends(get_db)):
    """Database theke shob processed images niye ashar jonno"""
    try:
        # Tomar model e column nam 'timestamp', tai oita diye sort hobe
        images = db.query(ProcessedImage).order_by(ProcessedImage.timestamp.desc()).all()
        
        return [
            {
                "id": img.id,
                "filename": img.filename,
                "processed": img.processed_image_data,
                "original": img.original_image_data,
                "created_at": img.timestamp # UI te 'created_at' namেই pathalam
            }
            for img in images
        ]
    except Exception as e:
        print(f"Fetch Error: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch history")

@app.post("/process-bg")
async def process_image(file: UploadFile = File(...)):
    """Sudhu process kore original ar processed base64 pathabe (Save hobe na)"""
    try:
        input_data = await file.read()
        
        # Background remove kora (Rembg library)
        output_data = remove(input_data)
        
        return {
            "original": image_to_base64(input_data),
            "processed": image_to_base64(output_data),
            "filename": file.filename
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed")

@app.post("/save-image")
async def save_image(data: dict, db: Session = Depends(get_db)):
    """Mobile app-e 'Save' button chaple database-e entry hobe"""
    try:
        new_entry = ProcessedImage(
            filename=data.get("filename"),
            processed_image_data=data.get("image_data"), # Current view image
            original_image_data=data.get("original_data")
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return {"message": "Saved successfully", "id": new_entry.id}
    except Exception as e:
        db.rollback()
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail="Database save failed")