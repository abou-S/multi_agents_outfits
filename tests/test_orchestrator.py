import os
import sys
import json

# Pour que "multi_agents" soit importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.orchestrator import Orchestrator


class FakeLLMClient:
    """
    Fake client LLM pour les tests d'intégration.
    Il imite la méthode .chat(system_prompt, user_prompt)
    mais renvoie une réponse JSON fixe.
    """

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        # On détecte quel agent parle grâce au contenu du system prompt
        if "analyse d'événements vestimentaires" in system_prompt:
            # Réponse pour EventAnalyzerAgent
            return json.dumps({
                "event_type": "mariage",
                "time_of_day": "soirée",
                "formality_level": "chic",
                "budget": 150.0,
                "gender": "homme"
            })
        elif "styliste professionnel" in system_prompt:
            # Réponse pour StylistAgent
            return json.dumps({
                "proposed_outfits": [
                    {
                        "style_name": "Tenue test chic",
                        "description": "Costume bleu de test, chemise blanche de test.",
                        "items_needed": [
                            "costume bleu test",
                            "chemise blanche test",
                            "chaussures noires test"
                        ],
                        "formality_level": "chic"
                    }
                ]
            })
        else:
            # Par sécurité
            return json.dumps({})


def test_orchestrator_flow_with_fake_llm():
    fake_llm = FakeLLMClient()
    orch = Orchestrator(llm_client=fake_llm)

    user_request = {
        "description": "Je vais à un mariage le soir, ambiance chic.",
        "budget": 150.0,
        "gender": "homme",
    }

    result = orch.run(user_request)

    # Vérifie qu'on a bien l'analyse d'événement
    assert "event_analysis" in result
    analysis = result["event_analysis"]
    assert analysis["event_type"] == "mariage"
    assert analysis["time_of_day"] == "soirée"
    assert analysis["formality_level"] == "chic"
    assert analysis["budget"] == 150.0
    assert analysis["gender"] == "homme"

    # Vérifie qu'on a bien les propositions de tenues
    assert "stylist_output" in result
    stylist_output = result["stylist_output"]
    assert "proposed_outfits" in stylist_output

    outfits = stylist_output["proposed_outfits"]
    assert len(outfits) == 1
    assert outfits[0]["style_name"] == "Tenue test chic"
    assert len(outfits[0]["items_needed"]) >= 1
