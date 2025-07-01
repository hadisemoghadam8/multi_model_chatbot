# process_websites.py
import os, json

def chunk_text(txt, max_words=150):
    w = txt.split()
    return [" ".join(w[i:i+max_words]) for i in range(0, len(w), max_words)]

BASE_DIR  = os.path.dirname(__file__)
CLEAN_DIR = os.path.join(BASE_DIR, "..", "data", "data_sources", "websites", "clean")
OUT_DIR   = os.path.join(BASE_DIR, "..", "data", "json_output", "websites")
os.makedirs(OUT_DIR, exist_ok=True)

for file in os.listdir(CLEAN_DIR):
    if not file.endswith(".txt"):
        continue
    text  = open(os.path.join(CLEAN_DIR, file), encoding="utf-8").read()
    title = os.path.splitext(file)[0]

    chunks = [c for c in chunk_text(text) if len(c.split()) >= 10]
    data = {
        "meta": {"title": title, "type": "website", "source_path": file},
        "chunks": [
            {"chunk_id": f"web_{i+1:04d}", "content": ch}
            for i, ch in enumerate(chunks)
        ]
    }
    with open(os.path.join(OUT_DIR, title + ".json"), "w", encoding="utf-8") as out_file:
        json.dump(data, out_file, ensure_ascii=False, indent=2)
    print("✅ processed →", title + ".json")
