from abc import ABC, abstractmethod
from typing import Dict, Any


class Agent(ABC):
    """
    Classe de base pour tous les agents.
    Chaque agent prend un dict en entrée et renvoie un dict en sortie.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Logique principale de l'agent."""
        pass
