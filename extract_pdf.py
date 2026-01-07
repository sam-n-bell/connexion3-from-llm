
import sys
from pypdf import PdfReader

pdf_path = "/Users/sambell/Desktop/FG-1D-2020_User_Guide.pdf"

try:
    reader = PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    
    # Extract text from all pages
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            print(f"--- Page {i+1} ---")
            print(text)
            print("\n")
except Exception as e:
    print(f"Error reading PDF: {e}")
