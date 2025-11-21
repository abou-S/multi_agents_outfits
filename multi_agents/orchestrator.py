from typing import Dict, Any

from multi_agents.agents.event_analyzer import EventAnalyzerAgent
from multi_agents.agents.stylist import StylistAgent
from multi_agents.agents.product_search import ProductSearchAgent
from multi_agents.core.llm_client import LLMClient


class Orchestrator:
    """
    Orchestrateur :
    - EventAnalyzerAgent (LLM) : comprend l'événement
    - StylistAgent (LLM)       : propose des idées de tenues
    - ProductSearchAgent       : cherche des produits concrets (budget-aware)

    Le paramètre include_products permet de garder la compatibilité avec les
    tests existants : si False, on ne fait pas la partie "search produits".
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()
        self.event_analyzer = EventAnalyzerAgent(llm_client=self.llm_client)
        self.stylist = StylistAgent(llm_client=self.llm_client)
        self.product_search = ProductSearchAgent(llm_client=self.llm_client)

    def run(self, user_request: Dict[str, Any], include_products: bool = False) -> Dict[str, Any]:
        # 1) Analyse de l'événement
        step1 = self.event_analyzer.run({"user_request": user_request})
        event_analysis = step1["event_analysis"]

        # 2) Propositions de tenues
        step2 = self.stylist.run({"event_analysis": event_analysis})
        stylist_output = step2["stylist_output"]

        result: Dict[str, Any] = {
            "event_analysis": event_analysis,
            "stylist_output": stylist_output,
        }

        # 3) (optionnel) Recherche produits + budget
        if include_products:
            step3 = self.product_search.run(
                {"event_analysis": event_analysis, "stylist_output": stylist_output}
            )
            product_search_output = step3["product_search_output"]
            result["product_search_output"] = product_search_output

        return result
