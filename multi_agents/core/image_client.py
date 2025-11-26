import os
from typing import List, Dict, Any, Optional
import json

import requests
from dotenv import load_dotenv

load_dotenv()


class ModelslabImageClient:
    """
    Client simple pour l'API image-to-image de Modelslab.
    On ne fait qu'un wrapper autour de l'endpoint v7.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "seedream-4.0-i2i",
        aspect_ratio: str = "1:1",
        api_url: str = "https://modelslab.com/api/v7/images/image-to-image",
    ) -> None:
        self.api_key = api_key or os.getenv("MODELSLAB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MODELSLAB_API_KEY manquant. Ajoute-le dans ton .env "
                "(MODELSLAB_API_KEY=...)."
            )
        self.model_id = model_id
        self.aspect_ratio = aspect_ratio
        self.api_url = api_url

    def generate_outfit_image(
        self,
        user_image_url: str,
        product_image_urls: List[str],
        prompt: str,
    ) -> Optional[str]:
        init_images = [user_image_url]  # on reste sur la version user-only

        payload: Dict[str, Any] = {
            "init_image": init_images,
            "prompt": prompt,
            "model_id": self.model_id,
            "aspect-ratio": self.aspect_ratio,
            "key": self.api_key,
        }

        headers = {"Content-Type": "application/json"}

        # 🔁 On tente jusqu'à 2 fois max
        for attempt in range(2):
            try:
                resp = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
                resp.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                print(f"[ModelslabImageClient] HTTP error: {http_err} - {resp.text}")
                return None
            except Exception as err:
                print(f"[ModelslabImageClient] Other error: {err}")
                return None

            data = resp.json()
            print("[ModelslabImageClient] Raw response:")
            print(json.dumps(data, indent=2))

            status = data.get("status")
            if status == "success":
                output = data.get("output") or []
                proxy_links = data.get("proxy_links") or []

                if isinstance(output, list) and output:
                    first = output[0]
                    if isinstance(first, str):
                        return first

                if isinstance(proxy_links, list) and proxy_links:
                    first = proxy_links[0]
                    if isinstance(first, str):
                        return first

                print("[ModelslabImageClient] No usable URL in response.")
                return None

            # ici status != "success"
            message = data.get("message", "")
            print(f"[ModelslabImageClient] Non-success status: {status} - {message}")

            # si c'est une erreur serveur générique, on retente une fois
            if "server error occurred" in message.lower() and attempt == 0:
                print("[ModelslabImageClient] Retry once after server error...")
                time.sleep(3)
                continue

            # sinon on abandonne direct
            return None

        return None

