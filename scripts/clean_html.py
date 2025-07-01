# clean_html.py
import os, json, bs4, re

RAW_DIR   = "data_sources/websites/raw"
CLEAN_DIR = "data_sources/websites/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

for file in os.listdir(RAW_DIR):
    if not file.endswith(".html"): continue
    html = open(os.path.join(RAW_DIR, file), encoding="utf-8").read()
    soup = bs4.BeautifulSoup(html, "html.parser")

    # حذف اسکریپت، استایل و ناوبری
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    out = os.path.join(CLEAN_DIR, file.replace(".html", ".txt"))
    open(out, "w", encoding="utf-8").write(text)
    print("✅ cleaned →", out)
