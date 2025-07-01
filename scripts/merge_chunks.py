#merge_chunks.py

import os, json

# مسیر پوشه‌های خروجی JSON
INPUT_DIRS = [
    "json_output/books/fa",
    "json_output/books/en",
    "json_output/articles/en",
    "json_output/podcasts/fa",
    "json_output/podcasts/en",
    "json_output/websites"
]

# فایل‌های خروجی merge
OUTPUT_FA = "processed_chunks/all_chunks_fa.jsonl"
OUTPUT_EN = "processed_chunks/all_chunks_en.jsonl"

def merge_chunks(lang, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as fout:
        for d in INPUT_DIRS:
            # فقط پوشه‌هایی که حاوی lang هستند را وارد کن
            if f"/{lang}" not in d and not (lang=="fa" and "websites" in d):
                continue
            for fname in os.listdir(d):
                path = os.path.join(d, fname)
                data = json.load(open(path, encoding="utf-8"))
                # اگر ساختار data['chunks'] باشه
                for chunk in data.get("chunks", []):
                    fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"✅ Merge کامل شد → {out_file}")

if __name__ == "__main__":
    merge_chunks("fa", OUTPUT_FA)
    merge_chunks("en", OUTPUT_EN)
