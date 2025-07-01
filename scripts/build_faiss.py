#build_faiss.py
import os, json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "all-MiniLM-L6-v2"

def build_index(jsonl_path, index_path, meta_path):
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    model = SentenceTransformer(EMBED_MODEL)

    texts, metas = [], []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            texts.append(chunk["content"])
            metas.append({"chunk_id": chunk["chunk_id"], "source": chunk.get("source","")})

    embeddings = model.encode(texts, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    with open(meta_path, "w", encoding="utf-8") as mf:
        json.dump(metas, mf, ensure_ascii=False, indent=2)
    print(f"✅ FAISS ساخته شد: {index_path}")

if __name__ == "__main__":
    build_index(
      "data/processed_chunks/all_chunks_fa.jsonl",
      "data/retriever/faiss_index_fa.bin",
      "data/retriever/faiss_meta_fa.json"
    )
    build_index(
      "data/processed_chunks/all_chunks_en.jsonl",
      "data/retriever/faiss_index_en.bin",
      "data/retriever/faiss_meta_en.json"
    )
