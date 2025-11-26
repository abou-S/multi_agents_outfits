import json
from typing import Dict, Any, Optional

from .base import Agent
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt
from multi_agents.core.models import EventUnderstanding


class EventAnalyzerAgent(Agent):
    """
    Agent qui analyse la demande utilisateur (texte libre) et en sort une structure EventUnderstanding.
    Utilise un LLM + prompt système, mais est robuste aux réponses non-JSON.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        super().__init__(name="event_analyzer")
        self.llm = llm_client or LLMClient()
        self.system_prompt = load_prompt("event_analyzer_system.txt")

    def run(self, data: Dict[str, Any]) -> EventUnderstanding:
        """
        data attendu :
        {
          "raw_text": str,
          "ui_budget": Optional[float],
          "ui_gender": str,
          "ui_age": Optional[int],
        }
        """
        description: str = data.get("raw_text", "")
        ui_budget: Optional[float] = data.get("ui_budget")
        ui_gender: str = data.get("ui_gender") or "homme"
        ui_age: Optional[int] = data.get("ui_age")

        # Construction du user prompt : uniquement des données, pas de consignes
        payload = {
            "description": description,
            "ui_budget": ui_budget,
            "ui_gender": ui_gender,
            "ui_age": ui_age,
        }

        user_prompt = (
            "Voici la demande de l'utilisateur et les informations fournies par l'interface :\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n\nAnalyse et renvoie l'objet JSON structuré comme demandé dans le prompt système."
        )

        raw = self.llm.chat(self.system_prompt, user_prompt)

        # --------- Parsing robuste --------- #
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Debug dans la console
            print("[EventAnalyzerAgent] JSON decode failed, raw LLM output:")
            print(raw)

            # Fallback : on construit un EventUnderstanding minimal à partir des infos UI
            event_type = "événement"
            time_of_day = "indéfini"
            formality_level = "casual"
            style = ""

            # Si tu veux, tu peux rajouter des heuristiques ici (détection de 'mariage', 'soir', etc.)
            fallback: EventUnderstanding = {
                "event_type": event_type,
                "time_of_day": time_of_day,
                "formality_level": formality_level,
                "style": style,
                "budget": ui_budget if ui_budget is not None else 100.0,
                "gender": ui_gender,
                "age": ui_age,
            }
            return fallback

        # On sécurise les champs et on remplit avec des valeurs par défaut si manquants
        event: EventUnderstanding = {
            "event_type": parsed.get("event_type", "événement"),
            "time_of_day": parsed.get("time_of_day", "indéfini"),
            "formality_level": parsed.get("formality_level", "casual"),
            "style": parsed.get("style", ""),
            "budget": parsed.get("budget", ui_budget),
            "gender": parsed.get("gender", ui_gender),
            "age": parsed.get("age", ui_age),
        }

        # Si le budget n'a pas été compris par le LLM, on récupère celui de l'UI
        if event["budget"] is None and ui_budget is not None:
            event["budget"] = ui_budget

        return event
