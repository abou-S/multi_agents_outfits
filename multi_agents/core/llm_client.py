import os
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# Charger automatiquement le .env à partir de la racine du projet
# (on remonte de 2 niveaux depuis ce fichier : core/ -> multi_agents/ -> racine)
BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class LLMClient:
    """
    Wrapper pour l'API Groq.
    Lit la clé dans le .env (GROQ_API_KEY).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
    ) -> None:
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY non défini. "
                "Ajoute-le dans un fichier .env à la racine du projet."
            )

        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content
