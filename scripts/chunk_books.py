# chunk_books.py

import os
import fitz  # PyMuPDF for reading PDF files
import json
from tqdm import tqdm  # Progress bar for loops

# Function to extract text chunks from a PDF file
def extract_text_chunks(pdf_path, lang, chunk_size=500):
    doc = fitz.open(pdf_path)  # Open PDF file
    full_text = ""
    
    # Read text from all pages
    for page in doc:
        full_text += page.get_text()
    doc.close()

    # Split text into words
    words = full_text.split()
    chunks = []
    
    # Create chunks of fixed size (default 500 words)
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Save chunk with metadata
        chunks.append({
            "text": chunk_text,       # The chunk text
            "lang": lang,             # Language label (fa or en)
            "source": pdf_path,       # Source file path
            "chunk_id": i // chunk_size  # Chunk index
        })
    return chunks  # Return list of chunks

# Main function
def main():
    # Input folders for Farsi and English books
    input_dirs = {
        "fa": "data_sources/books/fa",
        "en": "data_sources/books/en"
    }
    
    # Create output folder if it doesn't exist
    os.makedirs("processed_chunks", exist_ok=True)
    output_path = "processed_chunks/chunks.jsonl"  # Output file path

    all_chunks = []  # List to store all chunks

    # Loop through languages and files
    for lang, folder in input_dirs.items():
        for filename in tqdm(os.listdir(folder), desc=f"Processing {lang}"):
            if filename.endswith(".pdf"):  # Process only PDF files
                pdf_path = os.path.join(folder, filename)
                try:
                    chunks = extract_text_chunks(pdf_path, lang)
                    all_chunks.extend(chunks)  # Add chunks to the list
                except Exception as e:
                    print(f"[ERROR] Failed on {filename}: {e}")  # Handle errors

    # Save all chunks to output file in JSONL format (one JSON per line)
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"✅ Done! {len(all_chunks)} chunks saved to {output_path}")

# Run main function if script is executed directly
if __name__ == "__main__":
    main()
