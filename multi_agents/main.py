import json

from multi_agents.orchestrator import Orchestrator


def ask_float(prompt: str) -> float | None:
    txt = input(prompt).strip()
    if not txt:
        return None
    try:
        return float(txt.replace(",", "."))
    except ValueError:
        return None


def ask_int(prompt: str) -> int | None:
    txt = input(prompt).strip()
    if not txt:
        return None
    try:
        return int(txt)
    except ValueError:
        return None


def main() -> None:
    print("=== Assistant tenues (workflow complet) ===\n")

    description = input(
        "Décris l'événement et ton style (ex: 'Je vais à un mariage le soir, chic, budget 150€, style minimaliste') :\n> "
    )

    ui_budget = ask_float("\nBudget max en euros (optionnel, Enter pour sauter) :\n> ")

    gender = input("\nGenre (homme/femme, défaut = homme) :\n> ").strip().lower()
    if gender not in ("homme", "femme"):
        gender = "homme"

    age = ask_int("\nÂge (optionnel, Enter pour sauter) :\n> ")

    user_image_url = input(
        "\nURL publique de ta photo (optionnel, Enter pour ne pas générer de mannequin) :\n> "
    ).strip()
    if not user_image_url:
        user_image_url = None

    orchestrator = Orchestrator()

    print("\n=== Lancement du pipeline complet... ===\n")
    result = orchestrator.run_pipeline(
        description=description,
        ui_budget=ui_budget,
        ui_gender=gender,
        ui_age=age,
        user_image_url=user_image_url,
    )

    print("\n--- Analyse de l'événement ---")
    print(json.dumps(result["event"], ensure_ascii=False, indent=2))

    print("\n--- Tenues proposées (avec produits) ---")
    print(json.dumps(result["product_search_output"], ensure_ascii=False, indent=2))

    print("\n--- Résultat final (tenues + mannequin si photo fournie) ---")
    print(json.dumps(result["final_outfits"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
