# download_articles.py
import os
import requests

def download_pdfs(links_file, output_dir=os.path.expanduser("~/chatbot_env/data_sources/articles")):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(links_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    
    success, failed = 0, 0
    for idx, url in enumerate(links):
        try:
            print(f"⬇️ [{idx+1}/{len(links)}] در حال دانلود: {url}")
            response = requests.get(url, timeout=20)
            response.raise_for_status()

            filename = f"article_{idx+1:03d}.pdf"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as pdf_file:
                pdf_file.write(response.content)

            print(f"✅ ذخیره شد: {filepath}")
            success += 1
        except Exception as e:
            print(f"❌ خطا در دانلود {url} --> {e}")
            failed += 1

    print("\n--- خلاصه ---")
    print(f"📦 موفق: {success}")
    print(f"🚫 ناموفق: {failed}")
    print(f"📁 ذخیره در پوشه: {output_dir}")

if __name__ == "__main__":
    download_pdfs("article_links.txt")
