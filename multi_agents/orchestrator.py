from typing import Optional, Dict, Any

from multi_agents.agents.event_analyzer import EventAnalyzerAgent
from multi_agents.agents.stylist import StylistAgent
from multi_agents.agents.product_search import ProductSearchAgent
from multi_agents.agents.outfit_visualizer import OutfitVisualizerAgent

from multi_agents.core.llm_client import LLMClient
from multi_agents.core.zalando_scraper import ZalandoScraper
from multi_agents.core.image_client import ModelslabImageClient
from multi_agents.core.models import (
    EventUnderstanding,
    StylistOutput,
    ProductSearchOutput,
    ResolvedOutfit,
)


class Orchestrator:
    """
    Orchestrateur global du workflow :
      1) EventAnalyzerAgent : comprend la demande de l'utilisateur
      2) StylistAgent       : propose des idées de tenues + budget par article
      3) ProductSearchAgent : va chercher des produits Zalando pour chaque article
      4) OutfitVisualizer   : génère un mannequin portant la tenue

    Méthode principale : run_pipeline(...)
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.llm = llm_client or LLMClient()

        # Agents
        self.event_analyzer = EventAnalyzerAgent(llm_client=self.llm)
        self.stylist = StylistAgent(llm_client=self.llm)

        scraper = ZalandoScraper(
            max_page=1,
            max_results=3,
        )
        self.product_search = ProductSearchAgent(
            llm_client=self.llm,
            scraper=scraper,
        )

        image_client = ModelslabImageClient()
        self.visualizer = OutfitVisualizerAgent(
            llm_client=self.llm,
            image_client=image_client,
            max_outfits=3,
        )

    def run_pipeline(
        self,
        description: str,
        ui_budget: Optional[float] = None,
        ui_gender: str = "homme",
        ui_age: Optional[int] = None,
        user_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lance tout le workflow sur une seule demande utilisateur.

        - description : texte libre décrivant l'événement, le style, etc.
        - ui_budget   : budget éventuellement saisi dans l'UI (peut être None)
        - ui_gender   : "homme" / "femme" (par défaut "homme")
        - ui_age      : âge si disponible
        - user_image_url : URL publique de la photo du user (si None, pas de mannequin généré)

        Retourne un dict avec :
        {
          "event": EventUnderstanding,
          "stylist_output": StylistOutput,
          "product_search_output": ProductSearchOutput,
          "final_outfits": list[ResolvedOutfit]
        }
        """

        # 1) Analyse de l'événement
        event: EventUnderstanding = self._run_event_analyzer(
            description=description,
            ui_budget=ui_budget,
            ui_gender=ui_gender,
            ui_age=ui_age,
        )

        # 2) Propositions de tenues
        stylist_output: StylistOutput = self._run_stylist(event)

        # 3) Recherche de produits Zalando
        product_search_output: ProductSearchOutput = self._run_product_search(
            event,
            stylist_output,
        )

        # 4) Visualisation (mannequin) - optionnel si pas d'image user
        if user_image_url:
            final_outfits = self._run_visualizer(
                event,
                product_search_output,
                user_image_url,
            )
        else:
            # si pas de photo utilisateur, on renvoie simplement les tenues avec produits
            final_outfits = product_search_output["outfits"]

        return {
            "event": event,
            "stylist_output": stylist_output,
            "product_search_output": product_search_output,
            "final_outfits": final_outfits,
        }

    # ---------------- Sous-étapes privées ----------------

    def _run_event_analyzer(
        self,
        description: str,
        ui_budget: Optional[float],
        ui_gender: str,
        ui_age: Optional[int],
    ) -> EventUnderstanding:
        data = {
            "raw_text": description,
            "ui_budget": ui_budget,
            "ui_gender": ui_gender,
            "ui_age": ui_age,
        }
        result = self.event_analyzer.run(data)
        # EventAnalyzerAgent renvoie déjà un EventUnderstanding
        return result  # type: ignore

    def _run_stylist(self, event: EventUnderstanding) -> StylistOutput:
        result = self.stylist.run({"event": event})
        # StylistAgent.run renvoie {"outfits": [...]}
        return result  # type: ignore

    def _run_product_search(
        self,
        event: EventUnderstanding,
        stylist_output: StylistOutput,
    ) -> ProductSearchOutput:
        result = self.product_search.run(
            {"event": event, "stylist_output": stylist_output}
        )
        # ProductSearchAgent.run renvoie {"product_search_output": {...}}
        return result["product_search_output"]  # type: ignore

    def _run_visualizer(
        self,
        event: EventUnderstanding,
        product_search_output: ProductSearchOutput,
        user_image_url: str,
    ) -> list[ResolvedOutfit]:
        result = self.visualizer.run(
            {
                "event": event,
                "product_search_output": product_search_output,
                "user_image_url": user_image_url,
            }
        )
        # OutfitVisualizerAgent.run renvoie {"outfits": [...]}
        return result["outfits"]  # type: ignore
