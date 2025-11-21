import os
import sys
import json

# Ajoute la racine du projet au PYTHONPATH
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.agents.event_analyzer import EventAnalyzerAgent


class FakeLLMClient:
    """
    Fake LLM pour tester EventAnalyzerAgent sans appeler Groq.
    """

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        # On renvoie une analyse fixe, exactement comme on veut la tester
        return json.dumps({
            "event_type": "mariage",
            "time_of_day": "soirée",
            "formality_level": "chic",
            "budget": 150.0,
            "gender": "homme"
        })


def test_event_analyzer_mariage_chic_soiree():
    fake_llm = FakeLLMClient()
    agent = EventAnalyzerAgent(llm_client=fake_llm)

    user_request = {
        "description": "Je vais à un mariage le soir, ambiance chic.",
        "budget": 150.0,
        "gender": "homme",
    }

    result = agent.run({"user_request": user_request})
    analysis = result["event_analysis"]

    assert analysis["event_type"] == "mariage"
    assert analysis["time_of_day"] == "soirée"
    assert analysis["formality_level"] == "chic"
    assert analysis["budget"] == 150.0
    assert analysis["gender"] == "homme"
