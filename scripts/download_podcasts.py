# download_podcasts.py
import os, requests

def download_mp3s(links_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(links_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    for idx, url in enumerate(links):
        print(f"⬇️ Downloading {url}")
        filename = f"podcast_{idx+1:03d}.mp3"
        filepath = os.path.join(output_dir, filename)

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved: {filepath}")
        except Exception as e:
            print(f"❌ Error: {e}")
