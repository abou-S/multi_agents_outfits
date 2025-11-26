from typing import Dict, Any, Optional
import json
from multi_agents.core.models import EventUnderstanding

from .base import Agent
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt


class EventAnalyzerAgent(Agent):
    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        super().__init__(name="event_analyzer")
        self.llm = llm_client or LLMClient()
        self.system_prompt = load_prompt("event_analyzer_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        data attendu :
        {
          "raw_text": "...",          # description texte ou transcription Whisper
          "ui_budget": 200.0 | None,  # budget provenant de l'UI (optionnel)
          "ui_gender": "homme" | "femme" | None,
          "ui_age": int | None
        }

        Retour :
        {
          "event_type": "...",
          "time_of_day": "...",
          "formality_level": "...",
          "style": "...",
          "budget": 200,
          "gender": "...",
          "age": 30
        }
        """
        raw_text: str = data.get("raw_text", "").strip()
        ui_budget: Optional[float] = data.get("ui_budget")
        ui_gender: Optional[str] = data.get("ui_gender")
        ui_age: Optional[int] = data.get("ui_age")

        user_prompt = self._build_user_prompt(
            raw_text=raw_text,
            ui_budget=ui_budget,
            ui_gender=ui_gender,
            ui_age=ui_age,
        )

        raw_response = self.llm.chat(self.system_prompt, user_prompt)

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback minimal si le LLM envoie autre chose que du JSON
            parsed = {}

        # Sécuriser et injecter les valeurs UI au besoin

        # event_type
        event_type = parsed.get("event_type", "autre")

        # time_of_day
        time_of_day = parsed.get("time_of_day", "non précisé")

        # formality_level
        formality_level = parsed.get("formality_level", "standard")

        # style (string ou None)
        style = parsed.get("style")
        if style is None:
            style = ""

        # budget : priorité au ui_budget si fourni
        budget = parsed.get("budget")
        if ui_budget is not None:
            budget = ui_budget
        if budget is None:
            budget = None  # explicite

        # gender : priorité au ui_gender si fourni
        gender = parsed.get("gender", "non précisé")
        if ui_gender is not None:
            gender = ui_gender

        # age : priorité au ui_age si fourni
        age = parsed.get("age")
        if ui_age is not None:
            age = ui_age
        if age is None:
            age = None

        # ✅ On renvoie EXACTEMENT le JSON attendu
        result: EventUnderstanding = {
            "event_type": event_type,
            "time_of_day": time_of_day,
            "formality_level": formality_level,
            "style": style,
            "budget": budget,
            "gender": gender,
            "age": age,
        }

        return result


    def _build_user_prompt(
        self,
        raw_text: str,
        ui_budget: Optional[float],
        ui_gender: Optional[str],
        ui_age: Optional[int],
    ) -> str:
        lines = []

        lines.append("Voici les informations disponibles sur l'utilisateur et sa demande :\n")

        lines.append("Description de l'événement (texte libre) :")
        if raw_text:
            lines.append(f"\"{raw_text}\"")
        else:
            lines.append("(aucune description fournie)")

        lines.append("\nDonnées fournies par l'interface :")
        lines.append(f"- ui_budget: {ui_budget!r}")
        lines.append(f"- ui_gender: {ui_gender!r}")
        lines.append(f"- ui_age: {ui_age!r}")

        lines.append("\nAnalyse ces informations et remplis l'objet JSON demandé.")
        return "\n".join(lines)
