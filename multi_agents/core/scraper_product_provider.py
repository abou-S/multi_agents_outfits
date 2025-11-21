import time
from typing import List
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from multi_agents.core.models import Product, ProductSearchItemQuery
from multi_agents.core.product_provider import ProductProvider


class ScraperProductProvider(ProductProvider):
    """
    Provider qui scrappe un site e-commerce.
    ⚠️ À ADAPTER : URL de base, paramètres, sélecteurs CSS, respect des CGU du site.
    """

    BASE_URL = "https://www.zalando.fr"  # à remplacer par ton site

    def __init__(self, throttle_seconds: float = 1.0) -> None:
        self.throttle_seconds = throttle_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        })

    def search_products(self, query: ProductSearchItemQuery) -> List[Product]:
        time.sleep(self.throttle_seconds)

        q_keywords = self._build_keywords(query)

        params = {
            "q": q_keywords,
            "gender": query["attributes"].get("gender"),
        }
        params = {k: v for k, v in params.items() if v is not None}

        url = f"{self.BASE_URL}?{urlencode(params)}"
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        products: List[Product] = []

        # ⚠️ Sélecteurs à adapter au site réel
        for card in soup.select(".product-card")[:20]:
            name_el = card.select_one(".product-title")
            price_el = card.select_one(".product-price")
            link_el = card.select_one("a.product-link")
            img_el = card.select_one("img.product-image")

            if not (name_el and price_el and link_el and img_el):
                continue

            name = name_el.get_text(strip=True)
            price_text = price_el.get_text(strip=True)
            price = self._parse_price(price_text)

            if price > query["max_price"]:
                continue

            product_url = link_el.get("href", "")
            if product_url.startswith("/"):
                product_url = "https://www.exemple-mode.com" + product_url

            image_url = img_el.get("src", "")

            products.append(
                Product(
                    id=link_el.get("data-product-id", product_url),
                    name=name,
                    price=price,
                    currency="EUR",
                    product_url=product_url,
                    image_url=image_url,
                    source="exemple-mode",
                    category=query["category"],
                    gender=query["attributes"].get("gender", "unisex"),
                )
            )

        products.sort(key=lambda p: p["price"])
        return products

    def _build_keywords(self, query: ProductSearchItemQuery) -> str:
        parts = [query["role"]]
        attrs = query.get("attributes", {})
        for key in ["color", "fit", "formality_level", "gender"]:
            val = attrs.get(key)
            if isinstance(val, str):
                parts.append(val)
        return " ".join(parts)

    def _parse_price(self, text: str) -> float:
        digits = (
            text.replace("€", "")
            .replace(" ", "")
            .replace("\u00a0", "")
            .replace(",", ".")
        )
        try:
            return float(digits)
        except ValueError:
            return 99999.0
