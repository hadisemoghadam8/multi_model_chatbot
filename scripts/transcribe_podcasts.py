import os
import json
import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def chunk_text(text, max_words=150):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def process_audio_file(audio_path, output_path, language="fa", source_type="podcast"):
    title = os.path.splitext(os.path.basename(audio_path))[0]
    text = transcribe_audio(audio_path)
    chunks = chunk_text(text)

    structured_chunks = [{
        "chunk_id": f"{source_type}_{language}_{str(i+1).zfill(4)}",
        "content": ch,
        "source": audio_path
    } for i, ch in enumerate(chunks) if len(ch.strip()) >= 30]

    result = {
        "meta": {
            "title": title,
            "language": language,
            "type": source_type,
            "source_path": audio_path
        },
        "chunks": structured_chunks
    }

    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, f"{title}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Processed: {title}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_dirs = {
        "fa": os.path.join(base_dir, "..", "data", "data_sources", "podcasts", "fa"),
        "en": os.path.join(base_dir, "..", "data", "data_sources", "podcasts", "en")
    }
    output_base = os.path.join(base_dir, "..", "data", "json_output", "podcasts")

    for lang, input_dir in input_dirs.items():
        output_dir = os.path.join(output_base, lang)
        os.makedirs(output_dir, exist_ok=True)
        for file in os.listdir(input_dir):
            if file.endswith((".mp3", ".m4a", ".wav")):
                process_audio_file(os.path.join(input_dir, file), output_dir, language=lang)
