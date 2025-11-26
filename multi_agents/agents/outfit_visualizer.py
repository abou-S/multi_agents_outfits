# multi_agents/agents/outfit_visualizer.py

from typing import Dict, Any, Optional, List
import json

from .base import Agent
from multi_agents.core.llm_client import LLMClient
from multi_agents.core.prompts import load_prompt
from multi_agents.core.image_client import ModelslabImageClient
from multi_agents.core.models import (
    EventUnderstanding,
    ProductSearchOutput,
    ResolvedOutfit,
    MannequinPromptOutput,
)


class OutfitVisualizerAgent(Agent):
    """
    Agent responsable de générer un aperçu visuel (mannequin) pour chaque tenue.
    - Input : event + product_search_output + user_image_url
    - Output : même structure que product_search_output, mais chaque tenue est enrichie
      avec :
        - preview_image_url
        - preview_prompt
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        image_client: Optional[ModelslabImageClient] = None,
        max_outfits: int = 3,
    ) -> None:
        super().__init__(name="outfit_visualizer")
        self.llm = llm_client or LLMClient()
        self.image_client = image_client or ModelslabImageClient()
        self.system_prompt = load_prompt("outfit_visualizer_system.txt")
        self.max_outfits = max_outfits

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        data attendu :
        {
          "event": EventUnderstanding,
          "product_search_output": ProductSearchOutput,
          "user_image_url": "https://..."
        }

        Retour :
        {
          "outfits": [ ... ]  # même structure que ProductSearchOutput, enrichie
        }
        """
        event: EventUnderstanding = data["event"]
        ps_output: ProductSearchOutput = data["product_search_output"]
        user_image_url: str = data["user_image_url"]

        enriched_outfits: List[ResolvedOutfit] = []

        for idx, outfit in enumerate(ps_output["outfits"][: self.max_outfits]):
            # On travaille sur une copie pour être safe
            outfit_copy: ResolvedOutfit = dict(outfit)  # type: ignore


            image_url, prompt = self._generate_visual_for_outfit(
                event=event,
                outfit=outfit_copy,
                user_image_url=user_image_url,
            )

            outfit_copy["preview_image_url"] = image_url
            outfit_copy["preview_prompt"] = prompt

            enriched_outfits.append(outfit_copy)

        return {"outfits": enriched_outfits}

    def _generate_visual_for_outfit(
        self,
        event: EventUnderstanding,
        outfit: ResolvedOutfit,
        user_image_url: str,
    ) -> tuple[Optional[str], str]:
        """
        Génère une image pour une tenue :
        - récupère les images produits
        - génère un prompt via LLM
        - appelle Modelslab
        Retourne (image_url, prompt_utilisé)
        """
        product_image_urls: List[str] = []
        items_data_for_prompt: List[Dict[str, Any]] = []

        for item in outfit["items"]:
            chosen = item["chosen_product"]
            img = chosen.get("image")
            if not img:
                continue

            product_image_urls.append(img)
            items_data_for_prompt.append(
                {
                    "name": item["name"],
                    "category": item["category"],
                    "product_name": chosen.get("name"),
                    "color": chosen.get("color"),
                    "brand": chosen.get("brand"),
                }
            )

        if not product_image_urls:
            # Rien à afficher, pas d'image
            return None, ""

        # Prompt LLM
        prompt = self._build_mannequin_prompt(event, outfit, items_data_for_prompt)

        print("[OutfitVisualizer] product_image_urls:", product_image_urls)


        # Appel Modelslab
        image_url = self.image_client.generate_outfit_image(
            user_image_url=user_image_url,
            product_image_urls=product_image_urls,
            prompt=prompt,
        )

        return image_url, prompt

    def _build_mannequin_prompt(
        self,
        event: EventUnderstanding,
        outfit: ResolvedOutfit,
        items_data_for_prompt: List[Dict[str, Any]],
    ) -> str:
        payload = {
            "event": event,
            "outfit": {
                "style_name": outfit["style_name"],
                "description": outfit["description"],
                "formality_level": outfit["formality_level"],
            },
            "items": items_data_for_prompt,
        }

        user_prompt = (
            "Here is the event context and the chosen outfit with its items:\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + "\n\nGenerate the JSON with the 'prompt' field as requested."
        )

        raw = self.llm.chat(self.system_prompt, user_prompt)

        try:
            parsed: MannequinPromptOutput = json.loads(raw)
            prompt = parsed.get("prompt", "")
        except json.JSONDecodeError:
            prompt = (
                "Use the first image as the base person. Keep the same face, skin tone and body shape. "
                "Use the other images only as clothing references. "
                "Dress the person according to the described outfit in a clean, realistic, fashion style."
            )

        return prompt
