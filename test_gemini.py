from pathlib import Path

from backend.app.services.invoice_service import extract_invoice_data

image_path = Path("sample-scanned-invoice.jpg")

image_bytes = image_path.read_bytes()

result = extract_invoice_data(
    image_bytes=image_bytes,
    mime_type="image/jpeg"
)

print(result)