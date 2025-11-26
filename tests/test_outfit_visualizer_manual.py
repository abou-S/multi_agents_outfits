import os
import sys
import json

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from multi_agents.agents.outfit_visualizer import OutfitVisualizerAgent
from multi_agents.core.models import EventUnderstanding, ProductSearchOutput


def main() -> None:
    # 1) Contexte de l'événement (simulé pour le test)
    event: EventUnderstanding = {
        "event_type": "mariage",
        "time_of_day": "soirée",
        "formality_level": "chic",
        "style": "minimaliste, chic",
        "budget": 150.0,
        "gender": "homme",
        "age": 30,
    }

    # 2) Ton product_search_output EXACT, juste adapté en dict Python
    product_search_output: ProductSearchOutput = {
        "outfits": [
            {
                "style_name": "Chic minimaliste",
                "description": "Costume bleu marine, chemise blanche et sneakers propres.",
                "formality_level": "chic",
                "total_budget": 77.27,
                "items": [
                    {
                        "name": "costume bleu marine",
                        "category": "costume",
                        "max_price": 120.0,
                        "chosen_product": {
                            "name": "M&M FORMAL BLAZER - Veste de costume - dark blue",
                            "brand": "Pier One",
                            "price": 39.99,
                            "currency": "EUR",
                            "url": "https://www.zalando.fr/pier-one-formal-blazer-dark-blue-pi922a03c-k11.html",
                            "image": "https://img01.ztat.net/article/spp-media-p1/027b75e435484099a1f017e0f830b7bc/4a8a09cd5d4346b48954f766a530e2cf.jpg?imwidth=200",
                            "sku": "PI922A03C-K11",
                            "color": "dark blue/bleu marine"
                        }
                    },
                    {
                        "name": "chemise blanche",
                        "category": "chemise",
                        "max_price": 40.0,
                        "chosen_product": {
                            "name": "KLASSISCHES - Chemise classique - white",
                            "brand": "Only & Sons",
                            "price": 20.29,
                            "currency": "EUR",
                            "url": "https://www.zalando.fr/only-and-sons-klassisches-chemise-classique-white-os322d086-a11.html",
                            "image": "https://img01.ztat.net/article/spp-media-p1/f0c4c167163f37c3a8daa58b92d6b03d/206aab6f5c674211801501a2dbd168d1.jpg?imwidth=200",
                            "sku": "OS322D086-A11",
                            "color": "white/blanc"
                        }
                    },
                    {
                        "name": "baskette blanches",
                        "category": "chaussures",
                        "max_price": 40.0,
                        "chosen_product": {
                            "name": "UNISEX - Baskets basses - white",
                            "brand": "Pier One",
                            "price": 16.99,
                            "currency": "EUR",
                            "url": "https://www.zalando.fr/pier-one-unisex-baskets-basses-white-pi915o01x-a11.html",
                            "image": "https://img01.ztat.net/article/spp-media-p1/362b61a338284298bf380601ac535db4/1d3d81b520084230baaea0b17a99e203.jpg?imwidth=200&filter=packshot",
                            "sku": "PI915O01X-A11",
                            "color": "white/blanc"
                        }
                    }
                ]
            }
        ]
    }

    # 3) Image utilisateur (pour l’instant une URL de test)
    #user_image_url = "https://github.com/abou-S/multi_agents_outfits/blob/abou/assets/user_photo_test.jpg" 
    user_image_url = "https://raw.githubusercontent.com/abou-S/multi_agents_outfits/abou/assets/user_photo_test.jpg"


    # 4) Instancier l’agent
    agent = OutfitVisualizerAgent()

    # 5) Appel de l’agent
    result = agent.run(
        {
            "event": event,
            "product_search_output": product_search_output,
            "user_image_url": user_image_url,
        }
    )

    print("\n=== Résultat OutfitVisualizerAgent (enrichi) ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
