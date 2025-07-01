import os
import requests
import zipfile
import tarfile
import shutil

# Paths for different stages
download_dir = "downloads"       # Folder to save downloaded files
extract_dir = "extracted"        # Folder to extract compressed files
final_data_dir = "data"          # Final organized data folder

# List of (URL, filename) to download
download_links = [
    # JSON datasets from different sources
    ("https://raw.githubusercontent.com/ajaykuma/Stress-Management-Articles/master/data/articles.json", "articles.json"),
    ("https://raw.githubusercontent.com/nikhilkumarsingh/mental-health-podcasts/main/data/podcasts_fa.json", "podcasts_fa.json"),
    ("https://raw.githubusercontent.com/FrancescoSaverioZuppichini/health-books-json/master/books/fa-books.json", "fa-books.json"),
    ("https://datahub.io/core/mental-health/r/mental-health.json", "mental-health.json"),
    ("https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.json", "housing.json"),
    ("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.json", "vaccinations.json"),
    ("https://raw.githubusercontent.com/ozlerhakan/mongodb-json-files/master/datasets/stress-management.json", "stress-management.json"),
    ("https://raw.githubusercontent.com/imaad/stress-tracker-dataset/master/data/stress_entries.json", "stress_entries.json"),
    ("https://raw.githubusercontent.com/firatkara-open-source/health-articles-json/master/articles_fa.json", "articles_fa.json"),
    ("https://raw.githubusercontent.com/benoitvallon/100-best-books/master/books.json", "books.json"),
    ("https://raw.githubusercontent.com/jdorfman/Awesome-JSON-Datasets/master/books.json", "awesome_books.json"),
    ("https://raw.githubusercontent.com/azharimm/awesome-mental-health-apis/main/podcasts.json", "podcasts_apis.json"),
    ("https://raw.githubusercontent.com/Biuni/PokemonGO-Pokedex/master/pokedex.json", "pokedex.json"),
    ("https://data.sfgov.org/resource/yyjz-gm2v.json?$$app_token=YOUR_APP_TOKEN", "sfgov_data.json"),
    ("https://data.cityofnewyork.us/resource/nwxe-4ae8.json", "nyc_data.json"),
    ("https://data.cdc.gov/resource/ysku-2s3m.json", "cdc_ysku_2s3m.json"),
    ("https://data.cdc.gov/resource/w9zu-fywh.json", "cdc_w9zu_fywh.json"),
    ("https://data.cdc.gov/resource/q9bm-ucbu.json", "cdc_q9bm_ucbu.json"),
    ("https://api.covidtracking.com/v1/states/current.json", "covidtracking_states.json"),
    ("https://datahub.io/core/global-temp/r/annual.json", "global_temp_annual.json"),
    ("https://datahub.io/core/world-cities/r/world-cities.json", "world_cities.json"),
    ("https://raw.githubusercontent.com/zemirco/sf-city-lots-json/master/citylots.json", "sf_city_lots.json"),
    ("https://raw.githubusercontent.com/grammakov/usa-cities-json/master/cities.json", "usa_cities.json"),
    ("https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json", "cities.json"),
    ("https://raw.githubusercontent.com/FreeCodeCamp/ProjectReferenceData/master/cyclist-data.json", "cyclist_data.json"),
    ("https://raw.githubusercontent.com/FreeCodeCamp/ProjectReferenceData/master/GDP-data.json", "GDP_data.json"),
    ("https://raw.githubusercontent.com/FreeCodeCamp/ProjectReferenceData/master/global-temperature.json", "global_temperature.json"),
]
# Step 1: Download files
os.makedirs(download_dir, exist_ok=True)  # Create download folder if not exists

for url, filename in download_links:
    filepath = os.path.join(download_dir, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        response = requests.get(url, stream=True)
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(response.raw, f)  # Save file
    else:
        print(f"{filename} already downloaded.")  # Skip if already exists

# Step 2: Extract files (zip or tar.gz)
os.makedirs(extract_dir, exist_ok=True)  # Create extraction folder if not exists

for _, filename in download_links:
    filepath = os.path.join(download_dir, filename)
    
    if filename.endswith(".zip"):
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)  # Extract zip files
    elif filename.endswith(".tar.gz"):
        with tarfile.open(filepath, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_dir)  # Extract tar.gz files
    else:
        print(f"Unknown file format: {filename}")  # Other formats ignored

# Step 3: Organize extracted files to final folders
for root, dirs, files in os.walk(extract_dir):
    for name in files:
        file_path = os.path.join(root, name)

        # Move PDFs to books folder
        if file_path.endswith('.pdf'):
            target_folder = os.path.join(final_data_dir, 'books')
        
        # Move HTML or TXT to websites folder
        elif file_path.endswith('.html') or file_path.endswith('.txt'):
            target_folder = os.path.join(final_data_dir, 'websites')
        
        else:
            continue  # Skip other file types

        os.makedirs(target_folder, exist_ok=True)  # Ensure target folder exists
        shutil.move(file_path, os.path.join(target_folder, name))  # Move file

print("Done!")  # All operations completed