import os
import sys
import json

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.agents.stylist import StylistAgent
from multi_agents.core.models import EventUnderstanding


def main() -> None:
    event: EventUnderstanding = {
        "event_type": "anniversaire",
        "time_of_day": "soirée",
        "formality_level": "chic",
        "style": "streetwear, minimaliste",
        "budget": 400,
        "gender": "homme",
        "age": 30,
    }

    agent = StylistAgent()
    result = agent.run({"event": event})

    print("\n=== Résultat StylistAgent ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
