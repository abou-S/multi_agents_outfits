from typing import Dict, Any, Optional, List
import json

from .base import Agent
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt
from multi_agents.core.zalando_scraper import ZalandoScraper
from multi_agents.core.models import (
    EventUnderstanding,
    StylistOutput,
    ProductCandidate,
    OutfitItemResolved,
    ResolvedOutfit,
    ProductSearchOutput,
    QueryBuilderInput,
    QueryBuilderOutput,
    ProductSelectorInput,
    ProductSelectorOutput,
)


class ProductSearchAgent(Agent):
    """
    Agent de recherche produits / scraping :
    - prend en entrée l'output du StylistAgent + le contexte d'événement,
    - pour chaque article :
        * génère une requête de recherche Zalando via un LLM (Query Builder),
        * scrappe Zalando via Apify,
        * sélectionne le meilleur produit via un LLM (Product Selector),
    - renvoie des tenues enrichies avec un produit choisi par article.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        scraper: Optional[ZalandoScraper] = None,
    ) -> None:
        super().__init__(name="product_search")
        self.llm = llm_client or LLMClient()
        self.scraper = scraper or ZalandoScraper()

        self.query_builder_system = load_prompt("query_builder_system.txt")
        self.product_selector_system = load_prompt("product_selector_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        data attendu :
        {
          "event": EventUnderstanding,
          "stylist_output": StylistOutput
        }

        Retour :
        {
          "product_search_output": ProductSearchOutput
        }
        """
        event: EventUnderstanding = data["event"]
        stylist_output: StylistOutput = data["stylist_output"]

        resolved_outfits: List[ResolvedOutfit] = []

        for outfit in stylist_output["outfits"]:
            resolved_items: List[OutfitItemResolved] = []

            for item in outfit["items"]:
                resolved = self._resolve_single_item(
                    event=event,
                    outfit=outfit,
                    item=item,
                )
                if resolved is not None:
                    resolved_items.append(resolved)

            if not resolved_items:
                continue

            total_price = sum(it["chosen_product"]["price"] for it in resolved_items)

            # Vérifier le budget global (si défini)
            budget_global = event.get("budget")
            if budget_global is not None and total_price > budget_global:
                # On pourrait ici implémenter une stratégie plus intelligente,
                # pour l'instant on ignore la tenue si elle dépasse le budget réel.
                continue

            resolved_outfits.append(
                ResolvedOutfit(
                    style_name=outfit["style_name"],
                    description=outfit["description"],
                    formality_level=outfit["formality_level"],
                    total_budget=round(total_price, 2),
                    items=resolved_items,
                )
            )

        output: ProductSearchOutput = {"outfits": resolved_outfits}
        return {"product_search_output": output}

    # ---------- Résolution d'un seul item ----------

    def _resolve_single_item(
        self,
        event: EventUnderstanding,
        outfit: Dict[str, Any],
        item: Dict[str, Any],
    ) -> Optional[OutfitItemResolved]:
        """
        Résout un item :
        - construit la requête (QueryBuilder LLM)
        - scrappe Zalando
        - choisit le meilleur produit (ProductSelector LLM)
        """
        # 1) Query Builder LLM
        qb_input: QueryBuilderInput = {
            "item_name": item["name"],
            "category": item["category"],
            "max_price": float(item["max_price"]),
            "style": event["style"],
            "event_type": event["event_type"],
            "formality_level": event["formality_level"],
            "gender": event["gender"],
        }

        search_text, gender_path, max_price = self._build_query(qb_input)

        # 2) Scraper Zalando via Apify
        candidates: List[ProductCandidate] = self.scraper.search(
            search_text=search_text,
            gender_path=gender_path,
            max_price=max_price,
        )
        if not candidates:
            return None

        # 3) Product Selector LLM
        selector_input: ProductSelectorInput = {
            "item_name": item["name"],
            "category": item["category"],
            "style": event["style"],
            "event_type": event["event_type"],
            "formality_level": event["formality_level"],
            "gender": event["gender"],
            "candidates": candidates[:5],  # on limite à 5 pour le LLM
        }

        chosen_product = self._select_product(selector_input, candidates)

        if chosen_product is None:
            return None

        return OutfitItemResolved(
            name=item["name"],
            category=item["category"],
            max_price=float(item["max_price"]),
            chosen_product=chosen_product,
        )

    # ---------- Sous-fonctions LLM ----------

    def _build_query(
        self,
        qb_input: QueryBuilderInput,
    ) -> tuple[str, str, float]:
        user_prompt = (
            "Voici les informations sur l'article à rechercher :\n\n"
            + json.dumps(qb_input, ensure_ascii=False, indent=2)
            + "\n\nConstruit la requête de recherche Zalando appropriée."
        )
        raw = self.llm.chat(self.query_builder_system, user_prompt)

        try:
            parsed: QueryBuilderOutput = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback simple
            search_text = f"{qb_input['item_name']} {qb_input['category']} {qb_input['gender']}"
            gender_path = qb_input["gender"] if qb_input["gender"] in ("homme", "femme") else "unisex"
            return search_text, gender_path, qb_input["max_price"]

        search_text = parsed.get("search_text") or qb_input["item_name"]
        gender_path = parsed.get("gender_path") or qb_input["gender"]
        if gender_path not in ("homme", "femme", "unisex"):
            gender_path = "unisex"

        max_price = parsed.get("max_price", qb_input["max_price"])
        try:
            max_price = float(max_price)
        except (TypeError, ValueError):
            max_price = qb_input["max_price"]

        return search_text, gender_path, max_price

    def _select_product(
        self,
        selector_input: ProductSelectorInput,
        candidates: List[ProductCandidate],
    ) -> Optional[ProductCandidate]:
        user_prompt = (
            "Voici le contexte et les produits candidats pour un article de la tenue :\n\n"
            + json.dumps(selector_input, ensure_ascii=False, indent=2)
            + "\n\nChoisis le meilleur produit en respectant les consignes du système."
        )

        raw = self.llm.chat(self.product_selector_system, user_prompt)

        try:
            parsed: ProductSelectorOutput = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback : prendre le moins cher
            return candidates[0] if candidates else None

        idx = parsed.get("chosen_index", 0)
        if not isinstance(idx, int):
            idx = 0

        if idx < 0 or idx >= len(candidates):
            idx = 0

        return candidates[idx]
