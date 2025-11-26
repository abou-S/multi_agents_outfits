import os
import time
import json
from typing import List
from urllib.parse import quote_plus


import requests
from dotenv import load_dotenv

from multi_agents.core.models import ProductCandidate

load_dotenv()


class ZalandoScraper:
    """
    Wrapper autour de l'actor Apify 'saswave~zalando-scraper' pour Zalando.

    - Utilise APIFY_API_TOKEN dans le .env
    - Pour chaque recherche, lance un run, attend la fin et récupère les items.
    - Filtre par prix max et quelques critères simples.
    """

    ACTOR_ID = "saswave~zalando-scraper"

    def __init__(self, max_wait_seconds: int = 60, poll_interval: float = 2.0) -> None:
        self.api_token = os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "APIFY_API_TOKEN manquant. Ajoute-le dans ton .env "
                "(APIFY_API_TOKEN=...)."
            )
        self.max_wait_seconds = max_wait_seconds
        self.poll_interval = poll_interval

    def search(
        self,
        search_text: str,
        gender_path: str,
        max_price: float,
    ) -> List[ProductCandidate]:
        """
        Lance un run Apify pour une requête Zalando et renvoie une liste de ProductCandidate.
        """

        # Encoder la query comme dans le navigateur (espaces -> +)
        q = quote_plus(search_text)  # "costume bleu marine ..." -> "costume+bleu+marine+..."

        # price_to doit être un entier en euros
        price_to = int(max_price)

        # ✅ URL optimisée : filtre prix directement côté Zalando
        base_url = f"https://www.zalando.fr/{gender_path}/?q={q}&price_to={price_to}"

        # Construire l'URL de base Zalando (FR)
        #base_url = f"https://www.zalando.fr/{gender_path}/?q={search_text}"

        run_url = f"https://api.apify.com/v2/acts/{self.ACTOR_ID}/runs?token={self.api_token}"
        payload = {
            "url": base_url,
            "max_page": 1,
        }

        run_resp = requests.post(run_url, json=payload, timeout=30)
        run_resp.raise_for_status()
        run_data = run_resp.json()
        run_id = run_data["data"]["id"]

        # Polling jusqu'à la fin du run
        start_time = time.time()
        status = "RUNNING"
        status_url = (
            f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_token}"
        )

        while True:
            status_resp = requests.get(status_url, timeout=15)
            status_resp.raise_for_status()
            status_data = status_resp.json()["data"]
            status = status_data["status"]

            if status in ("SUCCEEDED", "FAILED", "TIMED_OUT"):
                break

            if time.time() - start_time > self.max_wait_seconds:
                break

            time.sleep(self.poll_interval)

        if status != "SUCCEEDED":
            return []

        dataset_id = status_data["defaultDatasetId"]
        items_url = (
            f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            f"?clean=1&format=json&token={self.api_token}"
        )
        items_resp = requests.get(items_url, timeout=30)
        items_resp.raise_for_status()
        raw_items = items_resp.json()

        return self._filter_and_normalize_items(
            raw_items, max_price=max_price, keyword=search_text
        )

    def _filter_and_normalize_items(
        self,
        items: list,
        max_price: float,
        keyword: str,
    ) -> List[ProductCandidate]:
        filtered: List[ProductCandidate] = []

        for item in items:
            # Filtrer les ADS
            if item.get("isSponsored") or item.get("sponsored"):
                continue

            # Filtrer par prix
            raw_price = item.get("price")
            if raw_price is None:
                continue

            try:
                price = float(str(raw_price).replace(",", "."))
            except ValueError:
                continue

            if price > max_price:
                continue

            # Filtrer par nom (approx)
            name = item.get("name", "")
            if not name:
                continue

            if keyword.split()[0].lower() not in name.lower():
                # Filtre léger, tu peux l’ajuster
                pass

            # Normaliser
            image_field = item.get("image") or item.get("images") or []
            if isinstance(image_field, list):
                image_url = image_field[0] if image_field else None
            else:
                image_url = image_field

            candidate: ProductCandidate = {
                "name": name,
                "brand": item.get("brand") or item.get("manufacturer"),
                "price": price,
                "currency": item.get("currency") or "EUR",
                "url": item.get("url", ""),
                "image": image_url,
                "sku": item.get("sku"),
                "color": item.get("color"),
            }
            filtered.append(candidate)

        # On peut trier par prix croissant
        filtered.sort(key=lambda c: c["price"])
        # limiter le nombre de candidats passés au LLM
        return filtered[:10]
