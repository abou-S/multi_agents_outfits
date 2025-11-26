from typing import Dict, Any, Optional
import json

from .base import Agent
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt
from multi_agents.core.models import (
    EventUnderstanding,
    StylistOutput,
    OutfitPlan,
)


class StylistAgent(Agent):
    """
    Agent Stylist :
    - prend en entrée l'output de l'EventAnalyzer (EventUnderstanding)
    - propose une liste d'idées de tenues (outfits)
    - pour chaque tenue, gère un budget max par article
    - s'assure que la somme des max_price par tenue ne dépasse pas le budget global
    - renvoie un JSON structuré (StylistOutput)
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        super().__init__(name="stylist")
        self.llm = llm_client or LLMClient()
        self.system_prompt = load_prompt("stylist_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        data attendu :
        {
          "event": EventUnderstanding
        }

        Retour :
        {
          "outfits": [ ... ]  # StylistOutput
        }
        """
        event: EventUnderstanding = data["event"]

        user_prompt = self._build_user_prompt(event)

        raw_response = self.llm.chat(self.system_prompt, user_prompt)

        try:
            parsed: StylistOutput = json.loads(raw_response)
        except json.JSONDecodeError:
            print("[StylistAgent] JSON decode failed, raw LLM output:")
            print(raw)

            parsed = {"outfits": []}  # fallback

        # Sécuriser le budget par tenue (au cas où le LLM dépasse)
        budget_global = event.get("budget")
        safe_outfits = self._enforce_budget(parsed, budget_global)

        return {"outfits": safe_outfits}

    def _build_user_prompt(self, event: EventUnderstanding) -> str:
        """
        Le user prompt ne contient QUE les données d'entrée, pas les consignes.
        """
        lines = []
        lines.append("Voici la compréhension de l'événement par l'agent précédent :\n")
        lines.append(json.dumps(event, ensure_ascii=False, indent=2))
        lines.append(
            "\nPropose des tenues adaptées à cet événement et à ce style, "
            "en respectant le budget si présent."
        )
        return "\n".join(lines)

    def _enforce_budget(
        self,
        stylist_output: StylistOutput,
        budget_global: Optional[float],
    ) -> list[OutfitPlan]:
        """
        Vérifie pour chaque tenue que la somme des max_price ne dépasse pas
        le budget global (si défini). Si le budget est dépassé, la tenue
        est soit ajustée soit filtrée (ici on choisit de la filtrer).
        """
        outfits: list[OutfitPlan] = []

        for outfit in stylist_output.get("outfits", []):
            items = outfit.get("items", [])
            total = sum(float(item.get("max_price", 0.0)) for item in items)

            # Si un budget global est défini, on le respecte strictement
            if budget_global is not None and total > budget_global:
                # On ignore cette tenue car elle dépasse le budget
                continue

            # On met à jour total_budget pour être sûr qu'il est cohérent
            outfit["total_budget"] = float(total)
            outfits.append(outfit)

        return outfits
