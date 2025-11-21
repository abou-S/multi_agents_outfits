from typing import Dict, Any
import json

from .base import Agent
from multi_agents.core.models import UserRequest, EventAnalysis
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt


class EventAnalyzerAgent(Agent):
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        super().__init__(name="event_analyzer")
        self.llm = llm_client or LLMClient()
        self.system_prompt = load_prompt("event_analyzer_system.txt")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_req: UserRequest = data["user_request"]

        user_prompt = f"""
Description de l'événement : {user_req['description']}
Budget (en euros) : {user_req['budget']}
Genre (si connu) : {user_req.get('gender')}

Tu dois retourner exactement ce JSON :

{{
  "event_type": "...",
  "time_of_day": "...",
  "formality_level": "...",
  "budget": {user_req['budget']},
  "gender": "..."
}}
"""

        raw_response = self.llm.chat(self.system_prompt, user_prompt)

        try:
            parsed: EventAnalysis = json.loads(raw_response)
        except json.JSONDecodeError:
            parsed = {
                "event_type": "autre",
                "time_of_day": "non précisé",
                "formality_level": "standard",
                "budget": user_req["budget"],
                "gender": user_req.get("gender"),
            }

        parsed.setdefault("budget", user_req["budget"])
        if "gender" not in parsed:
            parsed["gender"] = user_req.get("gender")

        return {"event_analysis": parsed}
