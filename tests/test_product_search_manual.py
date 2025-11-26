import os
import sys
import json

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.agents.product_search import ProductSearchAgent
from multi_agents.core.models import EventUnderstanding, StylistOutput


def main() -> None:
    event: EventUnderstanding = {
        "event_type": "mariage",
        "time_of_day": "soirée",
        "formality_level": "chic",
        "style": "minimaliste, chic",
        "budget": 200.0,
        "gender": "homme",
        "age": 30,
    }

    stylist_output: StylistOutput = {
        "outfits": [
            {
                "style_name": "Chic minimaliste",
                "description": "Costume bleu marine, chemise blanche et sneakers propres.",
                "formality_level": "chic",
                "total_budget": 200.0,
                "items": [
                    {"name": "costume bleu marine", "category": "costume", "max_price": 120.0},
                    {"name": "chemise blanche", "category": "chemise", "max_price": 40.0},
                    {"name": "baskette blanches", "category": "chaussures", "max_price": 40.0},
                ],
            }
        ]
    }

    agent = ProductSearchAgent()
    result = agent.run({"event": event, "stylist_output": stylist_output})

    print("\n=== Résultat ProductSearchAgent ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()