from typing import TypedDict, Optional, List, Dict, Any


class UserRequest(TypedDict):
    description: str
    budget: float
    gender: Optional[str]

class EventUnderstanding(TypedDict):
    event_type: str
    time_of_day: str
    formality_level: str
    style: str
    budget: Optional[float]
    gender: str
    age: Optional[int]


class EventUnderstanding(TypedDict):
    event_type: str
    time_of_day: str
    formality_level: str
    style: str
    budget: Optional[float]
    gender: str
    age: Optional[int]

"""styliste stuff"""

class OutfitItemBudget(TypedDict):
    name: str              # ex: "costume bleu marine"
    category: str          # ex: "costume", "chemise", "chaussures"
    max_price: float       # budget max pour cet article


class OutfitPlan(TypedDict):
    style_name: str        # ex: "Chic minimaliste"
    description: str       # texte descriptif de la tenue
    formality_level: str   # "chic", "décontracté", etc.
    total_budget: float    # somme des max_price des items
    items: List[OutfitItemBudget]


class StylistOutput(TypedDict):
    outfits: List[OutfitPlan]

"""""""""bra bra """

"""""product search stuff"""""

# 🔹 Représente un produit scrappé depuis Zalando (candidate)
class ProductCandidate(TypedDict, total=False):
    name: str
    brand: Optional[str]
    price: float
    currency: Optional[str]
    url: str
    image: Optional[str]
    sku: Optional[str]
    color: Optional[str]


# 🔹 Produit final choisi par l’agent (LLM ou heuristique)
class ChosenProduct(TypedDict):
    name: str
    brand: Optional[str]
    price: float
    currency: Optional[str]
    url: str
    image: Optional[str]
    sku: Optional[str]
    color: Optional[str]


# 🔹 Item provenant du StylistAgent enrichi d’un produit choisi
class OutfitItemResolved(TypedDict):
    name: str               # ex: "chemise blanche"
    category: str           # ex: "chemise"
    max_price: float        # budget max défini par StylistAgent
    chosen_product: ChosenProduct

class MannequinPromptOutput(TypedDict):
    prompt: str



# 🔹 Une tenue après résolution complète
class ResolvedOutfit(TypedDict):
    style_name: str
    description: str
    formality_level: str
    total_budget: float     # somme des prix réels des chosen_product
    items: List[OutfitItemResolved]
    # Ajout (optionnel) :
    preview_image_url: Optional[str]  # URL du mannequin généré
    preview_prompt: Optional[str]     # prompt utilisé pour générer l'image


# 🔹 Sortie finale de l’agent Product Search
class ProductSearchOutput(TypedDict):
    outfits: List[ResolvedOutfit]
"""""product search stuff"""""

"""PRODUIT / SCRAPPING"""
# ---------- Produits / Scraping ----------

class ProductCandidate(TypedDict, total=False):
    name: str
    brand: Optional[str]
    price: float
    currency: Optional[str]
    url: str
    image: Optional[str]
    sku: Optional[str]
    color: Optional[str]


class ChosenProduct(TypedDict):
    name: str
    brand: Optional[str]
    price: float
    currency: Optional[str]
    url: str
    image: Optional[str]
    sku: Optional[str]
    color: Optional[str]


class OutfitItemResolved(TypedDict):
    name: str
    category: str
    max_price: float
    chosen_product: ChosenProduct


class ResolvedOutfit(TypedDict):
    style_name: str
    description: str
    formality_level: str
    total_budget: float
    items: List[OutfitItemResolved]


class ProductSearchOutput(TypedDict):
    outfits: List[ResolvedOutfit]


# ---------- Sous-agents LLM produits ----------

class QueryBuilderInput(TypedDict):
    item_name: str
    category: str
    max_price: float
    style: str
    event_type: str
    formality_level: str
    gender: str


class QueryBuilderOutput(TypedDict):
    search_text: str
    gender_path: str
    max_price: float


class ProductSelectorInput(TypedDict):
    item_name: str
    category: str
    style: str
    event_type: str
    formality_level: str
    gender: str
    candidates: List[ProductCandidate]


class ProductSelectorOutput(TypedDict):
    chosen_index: int
    reason: Optional[str]
"""pRODUIT / SCRAPPING"""


class EventAnalysis(TypedDict, total=False):
    event_type: str
    time_of_day: str
    formality_level: str
    budget: float
    gender: Optional[str]


class OutfitIdea(TypedDict):
    style_name: str
    description: str
    items_needed: List[str]
    formality_level: str


class StylistOutput(TypedDict):
    proposed_outfits: List[OutfitIdea]


# ---------- Plan de recherche produits (par le LLM) ----------

class ProductSearchItemQuery(TypedDict):
    role: str            # ex: "costume", "chemise"
    category: str        # ex: "suit", "shirt"
    max_price: float
    attributes: Dict[str, Any]  # ex: {"color": "navy", "fit": "slim", "gender": "homme"}


class OutfitProductQuery(TypedDict):
    style_name: str
    description: str
    items_queries: List[ProductSearchItemQuery]


class ProductSearchPlan(TypedDict):
    outfits_queries: List[OutfitProductQuery]


# ---------- Produits concrets ----------

class Product(TypedDict):
    id: str
    name: str
    price: float
    currency: str
    product_url: str
    image_url: str
    source: str       # ex: "FakeStore", "MonSite", "Zalando"
    category: str
    gender: str


class OutfitProductItem(TypedDict):
    role: str
    product_id: str
    name: str
    price: float
    currency: str
    product_url: str
    image_url: str
    source: str


class OutfitWithProducts(TypedDict):
    style_name: str
    description: str
    items: List[OutfitProductItem]
    total_price: float
    currency: str


class ProductSearchOutput(TypedDict):
    outfits_with_products: List[OutfitWithProducts]
  