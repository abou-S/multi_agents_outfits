from multi_agents.orchestrator import Orchestrator


def main() -> None:
    print("=== Test Orchestrateur (Event + Styliste + Produits) ===\n")

    description = input(
        "Décris l'événement (ex: 'mariage le soir, ambiance chic, budget 150€') :\n> "
    )

    budget_str = input("Ton budget en euros (ex: 150) :\n> ")
    try:
        budget = float(budget_str.replace(",", "."))
    except ValueError:
        print("Budget invalide, on met 150€ par défaut.")
        budget = 150.0

    gender = input(
        "Genre (homme/femme, optionnel – entrer pour défaut homme) :\n> "
    ).strip().lower()
    if gender not in ["homme", "femme"]:
        gender = "homme"

    user_request = {
        "description": description,
        "budget": budget,
        "gender": gender,
    }

    # include_products=True → on active l'agent ProductSearch
    orch = Orchestrator()
    result = orch.run(user_request, include_products=True)

    print("\n--- Analyse de l'événement ---")
    print(result["event_analysis"])

    print("\n--- Propositions de tenues (Stylist LLM) ---")
    outfits = result["stylist_output"].get("proposed_outfits", [])
    if not outfits:
        print("Aucune tenue proposée.")
    else:
        for outfit in outfits:
            print("\n▶", outfit["style_name"])
            print("Description :", outfit["description"])
            print("Pièces nécessaires :")
            for item in outfit["items_needed"]:
                print(" -", item)

    # --- Partie produits (si disponible) ---
    product_search_output = result.get("product_search_output")

    if not product_search_output:
        print("\n(Aucun produit n'a été cherché ou trouvé.)")
        return

    print("\n=== Tenues avec produits (respect du budget) ===")

    outfits_with_products = product_search_output.get("outfits_with_products", [])
    if not outfits_with_products:
        print("Aucune tenue réalisable trouvée dans le budget.")
        return

    for outfit in outfits_with_products:
        print("\n💼 Tenue :", outfit["style_name"])
        print("Description :", outfit["description"])
        print(f"Total : {outfit['total_price']} {outfit['currency']}")

        print("Articles :")
        for item in outfit["items"]:
            print(f" - [{item['role']}] {item['name']} "
                  f"({item['price']} {item['currency']})")
            print(f"   Lien : {item['product_url']}")
            print(f"   Image : {item['image_url']}")
            print(f"   Source : {item['source']}")


if __name__ == "__main__":
    main()
