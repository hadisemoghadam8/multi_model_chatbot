import os

# Main project directory (current directory)
project_dir = "."

json_files = []  # List to store found JSON files

# Walk through all folders and subfolders
for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.json'):  # Check for JSON files
            full_path = os.path.join(root, file)  # Get full file path
            json_files.append(full_path)  # Add to the list

# Print total number of JSON files found
print(f"Total JSON files found: {len(json_files)}")

# Print list of file paths
print("\nList of files:")
for f in json_files:
    print(f)
