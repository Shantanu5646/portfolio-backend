import os
import io
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

app = FastAPI()

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Admin token (set in .env)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "MySuperSecretToken123")  # fallback if not in .env

# --------------------
# Admin-only PDF Upload
# --------------------
@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    x_admin_token: str = Header(None)  # token in request header
):
    # Authorization check
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file content
    contents = await file.read()

    # Store in GridFS
    fs = db.fs
    file_id = await fs.files.insert_one({
        "filename": file.filename,
        "content": contents
    })

    return {"message": "PDF uploaded successfully", "file_id": str(file_id.inserted_id)}


# --------------------
# Public PDF Download / View
# --------------------
@app.get("/get-pdf/{filename}")
async def get_pdf(filename: str):
    fs = db.fs
    doc = await fs.files.find_one({"filename": filename})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(io.BytesIO(doc["content"]), media_type="application/pdf")
