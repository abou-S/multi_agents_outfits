import os
import sys
import json

from typing import Dict, Any
import json

from .base import Agent
from multi_agents.core.models import EventAnalysis, StylistOutput
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)


class StylistAgent(Agent):
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        super().__init__(name="stylist")
        self.llm = llm_client or LLMClient()
        self.system_prompt = load_prompt("stylist_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        analysis: EventAnalysis = data["event_analysis"]

        user_prompt = f"""
Voici l'analyse de l'événement :

{json.dumps(analysis, ensure_ascii=False, indent=2)}

Génère entre 2 et 4 idées de tenues adaptées à ce contexte.
Tu dois répondre EXCLUSIVEMENT avec un JSON de la forme :

{{
  "proposed_outfits": [
    {{
      "style_name": "...",
      "description": "...",
      "items_needed": ["...", "..."],
      "formality_level": "..."
    }}
  ]
}}
"""

        raw_response = self.llm.chat(self.system_prompt, user_prompt)

        try:
            parsed: StylistOutput = json.loads(raw_response)
        except json.JSONDecodeError:
            parsed = {"proposed_outfits": []}

        return {"stylist_output": parsed}
