import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract


# -----------------------------
# OPTIONAL (Windows only)
# -----------------------------
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_with_pdfplumber(file_path):
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("pdfplumber error:", e)
        return ""

    return text


def extract_with_ocr(file_path):
    text = ""

    try:
        images = convert_from_path(file_path)

        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            text += page_text + "\n"

    except Exception as e:
        print("OCR error (pdf2image / tesseract / poppler):", e)
        return ""

    return text


def extract_resume_text(file_path):

    if not file_path:
        print("No file path provided")
        return ""

    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return ""

    print("Step 1: Trying pdfplumber...")

    text = extract_with_pdfplumber(file_path)

    if text.strip():
        print("Extracted using pdfplumber")
        return text.lower().strip()

    print("Step 2: Falling back to OCR...")

    text = extract_with_ocr(file_path)

    if text.strip():
        print("Extracted using OCR")
    else:
        print("No text extracted from PDF")

    return text.lower().strip()