# clean_html.py

import os, json, bs4, re  # os for file handling, bs4 for HTML parsing, re for regex

# Folder paths
RAW_DIR   = "data_sources/websites/raw"    # Raw HTML files
CLEAN_DIR = "data_sources/websites/clean"  # Clean text output

# Create output folder if it doesn't exist
os.makedirs(CLEAN_DIR, exist_ok=True)

# Loop through files in raw directory
for file in os.listdir(RAW_DIR):
    if not file.endswith(".html"): 
        continue  # Skip non-HTML files
    
    # Read HTML content
    html = open(os.path.join(RAW_DIR, file), encoding="utf-8").read()
    soup = bs4.BeautifulSoup(html, "html.parser")  # Parse HTML

    # Remove unwanted tags: script, style, nav, footer, header
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Get clean text, replace multiple spaces with one space
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

    # Define output file path with .txt extension
    out = os.path.join(CLEAN_DIR, file.replace(".html", ".txt"))

    # Save cleaned text
    open(out, "w", encoding="utf-8").write(text)
    
    print("✅ cleaned →", out)  # Print success message
