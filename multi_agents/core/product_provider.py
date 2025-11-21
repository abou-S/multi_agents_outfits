from abc import ABC, abstractmethod
from typing import List

from multi_agents.core.models import Product, ProductSearchItemQuery


class ProductProvider(ABC):
    """
    Interface générique pour une source de produits (API, scraping, catalogue local...).
    """

    @abstractmethod
    def search_products(self, query: ProductSearchItemQuery) -> List[Product]:
        """
        Recherche des produits pour un item précis.
        """
        raise NotImplementedError
