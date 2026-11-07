
import json
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"

EXTRACTION_PROMPT = """
You are an invoice data extractor.

Read the invoice image and extract only values that are clearly visible.
Never invent, guess, or calculate missing values.

Return JSON that matches this structure:
{
  "invoice_number": string or null,
  "invoice_date": string or null,
  "supplier_name": string or null,
  "line_items": [
    {
      "description": string or null,
      "quantity": number or null,
      "unit_price": number or null
    }
  ] or null,
  "total_amount": number or null,
  "subtotal": number or null,
  "vat": number or null
}

Rules:
- If a field is not present or not readable, use null.
- subtotal and vat are optional. Use null when they are not printed on the invoice.
- Do not compute total, subtotal, or VAT from other numbers.
- Return valid JSON only. No markdown. No extra commentary.
""".strip()


class InvoiceExtractionError(Exception):
    """Raised when Gemini cannot extract invoice data."""


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    supplier_name: Optional[str] = None
    line_items: Optional[list[LineItem]] = None
    total_amount: Optional[float] = None
    subtotal: Optional[float] = None
    vat: Optional[float] = None


def validate_invoice_totals(invoice: InvoiceData) -> list[str]:
    warnings = []

    if invoice.line_items and all(
        item.quantity is not None and item.unit_price is not None
        for item in invoice.line_items
    ):
        calculated_subtotal = sum(
            item.quantity * item.unit_price
            for item in invoice.line_items
        )

        if invoice.subtotal is not None:
            if abs(calculated_subtotal - invoice.subtotal) > 0.01:
                warnings.append(
                    "Line item total does not match subtotal."
                )

    if invoice.subtotal is not None and invoice.vat is not None:
        calculated_total = invoice.subtotal + invoice.vat

        if invoice.total_amount is not None:
            if abs(calculated_total - invoice.total_amount) > 0.01:
                warnings.append(
                    "Subtotal plus VAT does not match total amount."
                )

    return warnings


def _get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise InvoiceExtractionError(
            "GEMINI_API_KEY is not set. Add it to your environment before extracting invoices."
        )

    return genai.Client(api_key=api_key)


def _parse_gemini_response(response) -> InvoiceData:
    if getattr(response, "parsed", None) is not None:
        parsed = response.parsed

        if isinstance(parsed, InvoiceData):
            return parsed

        try:
            return InvoiceData.model_validate(parsed)
        except ValidationError as exc:
            raise InvoiceExtractionError(
                "Gemini returned JSON that does not match the invoice schema."
            ) from exc

    raw_text = (getattr(response, "text", None) or "").strip()

    if not raw_text:
        raise InvoiceExtractionError("Gemini returned an empty response.")

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")

        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        payload = json.loads(raw_text)
        return InvoiceData.model_validate(payload)

    except (json.JSONDecodeError, ValidationError) as exc:
        raise InvoiceExtractionError(
            "Gemini returned a response that could not be parsed as invoice JSON."
        ) from exc


def extract_invoice_data(image_bytes: bytes, mime_type: str) -> dict:
    """Send invoice image bytes to Gemini and return extracted fields as a dict."""

    if not image_bytes:
        raise InvoiceExtractionError("Invoice image bytes are empty.")

    client = _get_gemini_client()
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[image_part, EXTRACTION_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceData,
            ),
        )

    except errors.APIError as exc:
        raise InvoiceExtractionError(
            f"Gemini API request failed: {exc.message or str(exc)}"
        ) from exc

    except Exception as exc:
        raise InvoiceExtractionError(
            "Unexpected error while calling Gemini for invoice extraction."
        ) from exc

    invoice = _parse_gemini_response(response)

    extracted_data = invoice.model_dump()
    extracted_data["validation_warnings"] = validate_invoice_totals(invoice)

    return extracted_data
