# pdf_reader.py
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            if page_text:
                text += f"\n\n--- Page {page_num} ---\n\n"
                text += page_text
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
