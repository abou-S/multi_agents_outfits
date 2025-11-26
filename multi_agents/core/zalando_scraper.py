import os
import time
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class ZalandoScraper:
    """
    Wrapper autour de l'actor Apify 'saswave~zalando-scraper'.
    """

    ACTOR_ID = "saswave~zalando-scraper"

    def __init__(
        self,
        max_wait_seconds: int = 60,
        poll_interval: float = 2.0,
        max_page: int = 1,
        max_results: int = 5,
    ) -> None:
        self.api_token = os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN manquant dans .env")

        self.max_wait_seconds = max_wait_seconds
        self.poll_interval = poll_interval
        self.max_page = max_page          # 👈 nécessaire
        self.max_results = max_results    # 👈 nécessaire

    def search(
        self,
        search_text: str,
        gender_path: str,
        max_price: float,
    ) -> List[Dict[str, Any]]:
        from urllib.parse import quote_plus

        q = quote_plus(search_text)
        price_to = int(max_price)

        url = f"https://www.zalando.fr/{gender_path}/?q={q}&price_to={price_to}"

        run_url = f"https://api.apify.com/v2/acts/{self.ACTOR_ID}/runs?token={self.api_token}"
        payload = {
            "url": url,
            "max_page": self.max_page,
        }

        resp = requests.post(run_url, json=payload)
        resp.raise_for_status()
        run_data = resp.json()
        run_id = run_data["data"]["id"]

        # --- Polling ---
        start = time.time()
        while True:
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_token}"
            status_data = requests.get(status_url).json()
            status = status_data["data"]["status"]

            if status in ("SUCCEEDED", "FAILED", "TIMED_OUT"):
                break
            if time.time() - start > self.max_wait_seconds:
                break
            time.sleep(self.poll_interval)

        dataset_id = status_data["data"]["defaultDatasetId"]
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=1&format=json&token={self.api_token}"
        raw_items = requests.get(items_url).json()

        return self._normalize(raw_items, max_price=max_price)

    def _normalize(self, items: list, max_price: float) -> List[Dict[str, Any]]:
        results = []

        for item in items:
            if item.get("isSponsored") or item.get("sponsored"):
                continue

            raw_price = item.get("price")
            if raw_price is None:
                continue

            try:
                price = float(str(raw_price).replace(",", "."))
            except ValueError:
                continue

            if price > max_price:
                continue

            # 🔍 Normalisation de l'image : accepter string OU liste
            image_field = item.get("image") or item.get("images")
            if isinstance(image_field, list):
                image_url = image_field[0] if image_field else None
            else:
                image_url = image_field  # peut être str ou None

            results.append(
                {
                    "name": item.get("name"),
                    "brand": item.get("brand") or item.get("manufacturer"),
                    "price": price,
                    "currency": item.get("currency") or "EUR",
                    "url": item.get("url"),
                    "image": image_url,   # ✅ toujours une seule URL ou None
                    "sku": item.get("sku"),
                    "color": item.get("color"),
                }
            )

        results.sort(key=lambda x: x["price"])
        return results[: self.max_results]

