# AI Invoice Extractor

An AI-powered invoice extraction application built with Python, FastAPI, and Google Gemini. It extracts structured information from invoice images and returns the results in JSON format.

## Features

- Upload invoice images in JPG, JPEG, and PNG formats.
- Extract invoice details using Google Gemini AI.
- Extract invoice number, date, and supplier name.
- Extract line items, including description, quantity, and unit price.
- Extract subtotal, VAT, and total amount when available.
- Validate extracted data using Pydantic.
- Check consistency between line items, subtotal, VAT, and total amount.
- Handle invalid files, empty uploads, and API errors.
- Return structured JSON responses.

## Technology Stack

- Python
- FastAPI
- Google Gemini API
- Pydantic
- Uvicorn

## Project Structure

```text
AI-Invoice-Extractor/
│
├── backend/
│   └── app/
│       ├── services/
│       │   └── __init__.py
│       │   └── invoice_service.py
│       │
│       └── main.py
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── sample-scanned-invoice.jpg
└── test_gemini.py
```

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- pip

## Installation

Clone the repository or download the project.

Open the project directory:

```bash
cd AI-Invoice-Extractor
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Linux/macOS:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root directory by copying `.env.example`.

On Linux/macOS:

```bash
cp .env.example .env
```

Open the `.env` file and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

**Important:** Never share your API key or commit the `.env` file to a public repository. The `.env` file is included in `.gitignore`.

## Run the Application

From the project root directory, run:

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

## API Endpoints

### 1. Health Check

**GET /**

Checks whether the application is running.

Example response:

```json
{
  "message": "AI Invoice Extractor is running"
}
```

### 2. Upload Invoice

**POST /upload-invoice**

Uploads an invoice image and extracts its information using Gemini AI.

Request:

- Content-Type: `multipart/form-data`
- Field name: `file`
- Supported formats: JPG, JPEG, PNG

Example response:

```json
{
  "filename": "sample-scanned-invoice.jpg",
  "content_type": "image/jpeg",
  "extracted_data": {
    "invoice_number": "INV-2026-0142",
    "invoice_date": "18 September 2026",
    "supplier_name": "Larkfield Stationers",
    "line_items": [
      {
        "description": "A4 copier paper, 75 gsm, ream of 500",
        "quantity": 20,
        "unit_price": 285
      },
      {
        "description": "Ballpoint pens, blue, box of 50",
        "quantity": 4,
        "unit_price": 420
      },
      {
        "description": "Lever-arch files, A4, pack of 10",
        "quantity": 3,
        "unit_price": 899
      },
      {
        "description": "Whiteboard markers, assorted, pack of 4",
        "quantity": 6,
        "unit_price": 160
      },
      {
        "description": "Desk organiser, mesh, black",
        "quantity": 5,
        "unit_price": 349
      },
      {
        "description": "Sticky notes, 76 x 76 mm, pack of 12",
        "quantity": 8,
        "unit_price": 240
      }
    ],
    "total_amount": 17348.36,
    "subtotal": 14702,
    "vat": 2646.36,
    "validation_warnings": []
  }
}
```

The example response is based on the included sample invoice.

## API Documentation and Testing

FastAPI provides interactive API documentation through Swagger UI.

Open:

`http://127.0.0.1:8000/docs`

Steps:

1. Open the `/upload-invoice` endpoint.
2. Click **Try it out**.
3. Choose an invoice image.
4. Click **Execute**.
5. View the extracted JSON response.

A sample invoice image is included in the project as `sample-scanned-invoice.jpg`.

## Error Handling

The application handles:

- Invalid file types — HTTP 400.
- Empty uploaded files — HTTP 400.
- Gemini API and extraction errors — HTTP 502.
- Invalid request data — FastAPI validation errors.

## Invoice Data Validation

Pydantic validates the structure and data types of the extracted invoice information.

The application also checks:

- Whether the sum of line item amounts matches the subtotal.
- Whether subtotal plus VAT matches the total amount.

Any inconsistencies are returned in the `validation_warnings` field. Extracted values are not automatically modified.

## License

This project was developed as a technical assignment.