import os

def clear_faiss_indexes(directory="retriever"):
    for filename in os.listdir(directory):
        if filename.startswith("faiss_index") or filename.startswith("faiss_meta"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"✅ Removed: {file_path}")

if __name__ == "__main__":
    clear_faiss_indexes()
