
from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.app.services.invoice_service import (
    InvoiceExtractionError,
    extract_invoice_data,
)

app = FastAPI()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


@app.get("/")
def health_check():
    return {"message": "AI Invoice Extractor is running"}


@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, JPEG, and PNG files are allowed.",
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        extracted_data = extract_invoice_data(
            image_bytes=image_bytes,
            mime_type=file.content_type,
        )
    except InvoiceExtractionError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "extracted_data": extracted_data,
    }
