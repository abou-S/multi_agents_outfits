import json
from multi_agents.agents.event_analyzer import EventAnalyzerAgent


def main() -> None:
    print("=== Test manuel : EventAnalyzerAgent ===\n")

    raw_text = (
        "Je vais à un date ce soir. "
        "J'aime un style minimaliste et un peu streetwear, "
        "et j'ai un budget d'environ 200 euros."
    )

    ui_budget = 200.0
    ui_gender = "homme"
    ui_age = 30

    agent = EventAnalyzerAgent()

    result = agent.run(
        {
            "raw_text": raw_text,
            "ui_budget": ui_budget,
            "ui_gender": ui_gender,
            "ui_age": ui_age,
        }
    )

    print("\n--- Résultat ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
