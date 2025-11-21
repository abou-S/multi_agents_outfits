from typing import Dict, Any, List
import json

from .base import Agent
from multi_agents.core.models import (
    EventAnalysis,
    StylistOutput,
    ProductSearchPlan,
    OutfitWithProducts,
    OutfitProductItem,
    ProductSearchOutput,
)
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.product_provider import ProductProvider
from multi_agents.core.fake_product_provider import FakeProductProvider
from multi_agents.core.prompts import load_prompt


class ProductSearchAgent(Agent):
    """
    Agent intelligent de recherche produits :
    - utilise un LLM pour planifier les recherches (budget par item, catégories, attributs)
    - utilise un ProductProvider (fake ou scraper) pour chercher les articles
    - compose des tenues complètes avec prix, liens, images
    - respecte le budget global pour chaque tenue.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        provider: ProductProvider | None = None,
    ) -> None:
        super().__init__(name="product_search")
        self.llm = llm_client or LLMClient()
        # En dev/test : FakeProductProvider, plus tard : ScraperProductProvider()
        self.provider = provider or FakeProductProvider()
        self.system_prompt = load_prompt("product_search_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        analysis: EventAnalysis = data["event_analysis"]
        stylist_output: StylistOutput = data["stylist_output"]

        plan = self._plan_product_search(analysis, stylist_output)
        outfits_with_products = self._execute_plan(analysis, plan)

        output: ProductSearchOutput = {
            "outfits_with_products": outfits_with_products
        }
        return {"product_search_output": output}

    def _plan_product_search(
        self,
        analysis: EventAnalysis,
        stylist_output: StylistOutput,
    ) -> ProductSearchPlan:
        payload = {
            "event_analysis": analysis,
            "stylist_output": stylist_output,
        }

        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)

        raw = self.llm.chat(self.system_prompt, user_prompt)
        try:
            plan: ProductSearchPlan = json.loads(raw)
        except json.JSONDecodeError:
            plan = {"outfits_queries": []}

        return plan

    def _execute_plan(
        self,
        analysis: EventAnalysis,
        plan: ProductSearchPlan,
    ) -> List[OutfitWithProducts]:
        budget = analysis["budget"]
        outfits_with_products: List[OutfitWithProducts] = []

        for outfit_query in plan["outfits_queries"]:
            items: List[OutfitProductItem] = []
            total_price = 0.0
            currency = "EUR"

            for item_query in outfit_query["items_queries"]:
                candidates = self.provider.search_products(item_query)
                if not candidates:
                    items = []
                    total_price = 0.0
                    break

                product = candidates[0]  # le moins cher

                total_price += product["price"]
                currency = product["currency"]

                # On arrête si on dépasse le budget global
                if total_price > budget:
                    items = []
                    total_price = 0.0
                    break

                items.append(
                    OutfitProductItem(
                        role=item_query["role"],
                        product_id=product["id"],
                        name=product["name"],
                        price=product["price"],
                        currency=product["currency"],
                        product_url=product["product_url"],
                        image_url=product["image_url"],
                        source=product["source"],
                    )
                )

            if items and total_price <= budget:
                outfits_with_products.append(
                    OutfitWithProducts(
                        style_name=outfit_query["style_name"],
                        description=outfit_query["description"],
                        items=items,
                        total_price=round(total_price, 2),
                        currency=currency,
                    )
                )

        return outfits_with_products
