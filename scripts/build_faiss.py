#build_faiss.py
# --- Required Libraries ---
import os, json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Embedding model used to encode text chunks into vectors
EMBED_MODEL = "all-MiniLM-L6-v2"

def build_index(jsonl_path, index_path, meta_path):
    # Create directory for FAISS index if it doesn't exist
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    # Load the sentence transformer model
    model = SentenceTransformer(EMBED_MODEL)

    texts, metas = [], []

    # Read JSONL file line by line and extract text + metadata
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            texts.append(chunk["content"])  # The actual text content
            metas.append({
                "chunk_id": chunk["chunk_id"],
                "source": chunk.get("source", "")  # Optional source info
            })

    # Generate embeddings (vectors) for all text chunks
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Create a FAISS index using L2 (Euclidean) distance
    dim = embeddings.shape[1]  # Vector dimension
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)  # Add all vectors to the index

    # Save FAISS index to disk
    faiss.write_index(index, index_path)

    # Save associated metadata to a JSON file
    with open(meta_path, "w", encoding="utf-8") as mf:
        json.dump(metas, mf, ensure_ascii=False, indent=2)

    print(f"✅ FAISS index created: {index_path}")


if __name__ == "__main__":
    # Build FAISS index for Persian chunks
    build_index(
      "data/processed_chunks/all_chunks_fa.jsonl",     # Input data
      "data/retriever/faiss_index_fa.bin",             # FAISS index output
      "data/retriever/faiss_meta_fa.json"              # Metadata output
    )

    # Build FAISS index for English chunks
    build_index(
      "data/processed_chunks/all_chunks_en.jsonl",
      "data/retriever/faiss_index_en.bin",
      "data/retriever/faiss_meta_en.json"
    )

