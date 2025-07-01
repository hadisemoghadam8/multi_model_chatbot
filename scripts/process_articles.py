import os
import json
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
    return text

def chunk_text(text, max_words=150):
    words = text.split()
    chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return chunks

def filter_chunks(chunks):
    valid, removed = [], []
    for chunk in chunks:
        reason = None
        if len(chunk.strip()) < 30:
            reason = "خیلی کوتاه"
        elif len(chunk.split()) < 10:
            reason = "کمتر از ۱۰ کلمه"
        elif chunk.isdigit():
            reason = "فقط عدد (شماره صفحه)"
        elif not any(c.isalpha() for c in chunk):
            reason = "فاقد حرف خوانا"

        if reason:
            removed.append({"content": chunk, "reason": reason})
        else:
            valid.append(chunk)
    return valid, removed

def process_pdf_file(pdf_path, output_path, language="en", source_type="article"):
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    valid_chunks, removed_chunks = filter_chunks(chunks)

    structured_chunks = [{
        "chunk_id": f"{source_type}_{language}_{str(i + 1).zfill(4)}",
        "page": None,
        "content": ch
    } for i, ch in enumerate(valid_chunks)]

    result = {
        "meta": {
            "title": title,
            "language": language,
            "type": source_type,
            "source_path": pdf_path
        },
        "chunks": structured_chunks,
        "removed_chunks": removed_chunks
    }

    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, f"{title}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Processed: {title}")

if __name__ == "__main__":
    articles_dir = os.path.expanduser("~/chatbot_env/data/data_sources/articles")
    output_dir = os.path.expanduser("~/chatbot_env/data/json_output/articles")
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(articles_dir):
        if file.endswith(".pdf"):
            process_pdf_file(os.path.join(articles_dir, file), output_dir, language="en")
