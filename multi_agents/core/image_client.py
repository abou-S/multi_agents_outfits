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
        """
        Appelle l'API Modelslab image-to-image et renvoie l'URL de la première image générée.
        """
        init_images = [user_image_url] + product_image_urls

        payload: Dict[str, Any] = {
            "init_image": init_images,
            "prompt": prompt,
            "model_id": self.model_id,
            "aspect-ratio": self.aspect_ratio,
            "key": self.api_key,
        }

        headers = {"Content-Type": "application/json"}

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

        # 👇 Debug léger pour voir ce que renvoie vraiment l'API (tu peux commenter après)
        print("[ModelslabImageClient] Raw response:")
        print(json.dumps(data, indent=2))

        # On suit EXACTEMENT la structure que tu as montrée :
        # {
        #   "status": "success",
        #   "output": ["https://...png"],
        #   "proxy_links": ["https://...png"],
        #   "meta": { ... }
        # }

        status = data.get("status")
        if status != "success":
            print(f"[ModelslabImageClient] Non-success status: {status}")
            return None

        output = data.get("output") or []
        proxy_links = data.get("proxy_links") or []

        # On privilégie output[0]
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, str):
                return first

        # sinon, on tente proxy_links[0]
        if isinstance(proxy_links, list) and proxy_links:
            first = proxy_links[0]
            if isinstance(first, str):
                return first

        print("[ModelslabImageClient] No usable URL in response.")
        return None

