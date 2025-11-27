import os
import io
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

app = FastAPI()

# --- MongoDB connection ---
if not MONGO_URI or not DB_NAME:
    raise RuntimeError("MONGO_URI or DB_NAME not set in environment")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Use a simple collection for PDFs
pdf_collection = db["pdf_files"]

# --- Admin token for protected upload ---
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "MySuperSecretToken123")
print("ADMIN_TOKEN at startup:", ADMIN_TOKEN)


# --------------------
# Admin-only PDF Upload
# --------------------
@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    x_admin_token: str = Header(None)
):
    # Debug log
    print("Received x_admin_token header:", x_admin_token)

    # Authorization check
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file content
    contents = await file.read()

    # Store in MongoDB collection
    doc = {
        "filename": file.filename,
        "content": contents,
    }

    result = await pdf_collection.insert_one(doc)

    return {
        "message": "PDF uploaded successfully",
        "file_id": str(result.inserted_id),
        "filename": file.filename,
    }


# --------------------
# Public PDF Download / View
# --------------------
@app.get("/get-pdf/{filename}")
async def get_pdf(filename: str):
    # Find document by exact filename
    doc = await pdf_collection.find_one({"filename": filename})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")

    # content is stored as bytes (or Binary) -> wrap in BytesIO
    file_bytes = doc["content"]
    if isinstance(file_bytes, memoryview):
        file_bytes = file_bytes.tobytes()

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        },
    )
