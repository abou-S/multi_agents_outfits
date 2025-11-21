import json
from pathlib import Path
from typing import List

from multi_agents.core.models import Product, ProductSearchItemQuery
from multi_agents.core.product_provider import ProductProvider


class FakeProductProvider(ProductProvider):
    """
    Provider fake basé sur un fichier JSON local.
    Utilisé pour le développement et les tests.
    """

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[1]  # multi_agents/
        data_path = base_dir / "data" / "products_fake.json"
        with data_path.open("r", encoding="utf-8") as f:
            self.products: List[Product] = json.load(f)

    def search_products(self, query: ProductSearchItemQuery) -> List[Product]:
        role = query["role"]
        category = query["category"]
        max_price = query["max_price"]
        gender = query["attributes"].get("gender")

        candidates: List[Product] = [
            p for p in self.products
            if p["category"] == category
            and (gender is None or p["gender"] == gender)
            and p["price"] <= max_price
        ]

        # On trie du moins cher au plus cher
        candidates.sort(key=lambda p: p["price"])
        return candidates
