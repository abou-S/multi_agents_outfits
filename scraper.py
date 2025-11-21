from apify_client import ApifyClient
import csv
import os
from dotenv import load_dotenv

# 1️⃣ Charger le token depuis .env
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    raise ValueError("⚠️ APIFY_TOKEN manquant dans le fichier .env")

# 2️⃣ Initialiser le client Apify
client = ApifyClient(APIFY_TOKEN)

# 3️⃣ Configurer les URLs à scraper
start_urls = [
    {"url": "https://www.zalando.fr/lipsy-bottes-burgundy-red-li711n022-g11.html"}
]

# 4️⃣ Lancer le scraper
run = client.actor("lhotanova/zalando-scraper").call(run_input={
    "startUrls": start_urls,
    "maxItems": 100,
    "maxConcurrency": 10,
    "maxRequestRetries": 5
})

# 5️⃣ Récupérer les résultats depuis le dataset
dataset_id = run["defaultDatasetId"]
items = client.dataset(dataset_id).list_items().items

# 6️⃣ Sauvegarder dans CSV
csv_file = "zalando_products.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Brand", "Name", "Price", "URL", "Sizes", "Images"])
    
    for item in items:
        writer.writerow([
            item.get("brand"),
            item.get("name"),
            item.get("price"),
            item.get("url"),
            ", ".join(item.get("sizes", [])) if item.get("sizes") else "",
            ", ".join(item.get("images", [])) if item.get("images") else ""
        ])

print(f"✅ Scraping terminé. {len(items)} produits sauvegardés dans {csv_file}")
