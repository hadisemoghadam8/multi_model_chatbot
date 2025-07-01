# merge_chunks.py

import os, json

# List of folders containing chunked JSON files
INPUT_DIRS = [
    "json_output/books/fa",
    "json_output/books/en",
    "json_output/articles/en",
    "json_output/podcasts/fa",
    "json_output/podcasts/en",
    "json_output/websites"
]

# Output files for merged chunks
OUTPUT_FA = "processed_chunks/all_chunks_fa.jsonl"
OUTPUT_EN = "processed_chunks/all_chunks_en.jsonl"

# Function to merge chunks based on language
def merge_chunks(lang, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)  # Create output folder if needed
    
    with open(out_file, "w", encoding="utf-8") as fout:
        for d in INPUT_DIRS:
            
            # Only include folders that match the language
            if f"/{lang}" not in d and not (lang == "fa" and "websites" in d):
                continue

            # Loop through all files in the folder
            for fname in os.listdir(d):
                path = os.path.join(d, fname)
                
                # Read JSON file
                data = json.load(open(path, encoding="utf-8"))
                
                # If data contains 'chunks', write each chunk to output
                for chunk in data.get("chunks", []):
                    fout.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"✅ Merge completed → {out_file}")

# Run merge for both Farsi and English chunks
if __name__ == "__main__":
    merge_chunks("fa", OUTPUT_FA)
    merge_chunks("en", OUTPUT_EN)
