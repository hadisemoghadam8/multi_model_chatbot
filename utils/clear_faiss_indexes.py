import os  # For interacting with the file system

# Function to remove all FAISS index and metadata files from a directory
def clear_faiss_indexes(directory="retriever"):
    for filename in os.listdir(directory):
        # Check for FAISS index or metadata files by name prefix
        if filename.startswith("faiss_index") or filename.startswith("faiss_meta"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)  # Delete the file
            print(f"✅ Removed: {file_path}")  # Confirmation message

# Run the cleanup function if script is executed directly
if __name__ == "__main__":
    clear_faiss_indexes()
