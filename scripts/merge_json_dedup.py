
import os
import json
from collections import defaultdict

# Base data directory
base_dir = "json_output"

# Output directory for merged files
output_dir = os.path.join(base_dir, "merged")
os.makedirs(output_dir, exist_ok=True)

# Categories and corresponding output filenames
categories = {
    "articles/en": "all_articles_en.json",
    "books/en": "all_books_en.json",
    "books/fa": "all_books_fa.json",
    "podcasts/en": "all_podcasts_en.json",
    "podcasts/fa": "all_podcasts_fa.json",
    "websites": "all_websites.json",
}

# Function to load JSON data from a file
def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Return list of items
            if isinstance(data, list):
                return data
            else:
                return [data]
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

# Function to remove duplicates based on 'title' or 'content' fields
def deduplicate(items):
    seen = set()
    unique_items = []
    
    for item in items:
        # Priority for duplicate detection: title > content > entire JSON string
        key = item.get('title') or item.get('content') or json.dumps(item, sort_keys=True)
        
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    return unique_items

# Main merging process
for category_path, output_filename in categories.items():
    full_path = os.path.join(base_dir, category_path)
    
    # Skip if folder does not exist
    if not os.path.exists(full_path):
        print(f"Skipping missing category: {category_path}")
        continue

    all_items = []
    
    # Load all JSON files in the category folder
    for filename in os.listdir(full_path):
        if filename.endswith('.json'):
            file_path = os.path.join(full_path, filename)
            all_items.extend(load_json(file_path))

    print(f"Loaded {len(all_items)} items from {category_path}")

    # Remove duplicate entries
    unique_items = deduplicate(all_items)
    print(f"After deduplication: {len(unique_items)} items")

    # Save merged and cleaned data
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)

    print(f"Saved merged file: {output_path}")

print("\nAll categories merged and cleaned successfully ✅")
