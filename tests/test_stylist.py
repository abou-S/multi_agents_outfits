import os
import sys

# Ajoute la racine du projet au PYTHONPATH
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.agents.stylist import StylistAgent


def test_stylist_mariage_chic_homme():
    agent = StylistAgent()

    event_analysis = {
        "event_type": "mariage",
        "time_of_day": "soirée",
        "formality_level": "chic",
        "budget": 150.0,
        "gender": "homme",
    }

    result = agent.run({"event_analysis": event_analysis})
    stylist_output = result["stylist_output"]

    assert "proposed_outfits" in stylist_output
    outfits = stylist_output["proposed_outfits"]

    # On s'attend à au moins 2 tenues pour ce cas
    assert len(outfits) >= 2

    # Vérifie que chaque tenue a les champs attendus
    for outfit in outfits:
        assert "style_name" in outfit
        assert "description" in outfit
        assert "items_needed" in outfit
        assert isinstance(outfit["items_needed"], list)
        assert len(outfit["items_needed"]) > 0
