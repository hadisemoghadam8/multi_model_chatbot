import os

# مسیر اصلی پروژه
project_dir = "."

json_files = []

# پیمایش کل دایرکتوری‌ها
for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.json'):
            full_path = os.path.join(root, file)
            json_files.append(full_path)

print(f"تعداد کل فایل‌های JSON پیدا شده: {len(json_files)}")
print("\nلیست فایل‌ها:")
for f in json_files:
    print(f)
