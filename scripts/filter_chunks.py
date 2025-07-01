import json
import os

# مسیرها
INPUT_FILE = "processed_chunks/chunks.jsonl"
OUTPUT_FILE = "processed_chunks/cleaned_chunks.jsonl"

# کاراکترهای مشکوک (قابل گسترش)
BAD_CHARS = ["�", "\u200c", "\u200e", "\u202a", "\u202c"]  # ZWNJ، RTL، LRM...

def count_bad_chars(text):
    return sum(text.count(char) for char in BAD_CHARS)

def is_valid_chunk(text):
    reasons = []
    words = text.strip().split()
    
    if len(words) < 30:
        reasons.append("خیلی کوتاه بود (<۳۰ کلمه)")
    
    bad_char_count = count_bad_chars(text)
    if bad_char_count > 3:
        reasons.append(f"کاراکترهای مشکوک زیاد داشت ({bad_char_count})")
    
    return len(reasons) == 0, reasons

def filter_chunks(input_file, output_file):
    total = 0
    kept = 0
    removed = 0

    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8") as fout:
        
        for line in fin:
            total += 1
            chunk = json.loads(line)
            text = chunk.get("text", "")

            valid, reasons = is_valid_chunk(text)
            if valid:
                fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                kept += 1
            else:
                removed += 1
                print(f"⛔ حذف شد: chunk_id={chunk.get('chunk_id')} | دلایل: {'، '.join(reasons)}")

    print("\n--- خلاصه ---")
    print(f"✅ نگه داشته‌شده: {kept}")
    print(f"❌ حذف‌شده: {removed}")
    print(f"📦 مجموع چانک‌ها: {total}")
    print(f"📁 خروجی ذخیره شد در: {output_file}")

if __name__ == "__main__":
    filter_chunks(INPUT_FILE, OUTPUT_FILE)
