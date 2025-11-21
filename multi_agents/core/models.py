from typing import TypedDict, Optional, List, Dict, Any


class UserRequest(TypedDict):
    description: str
    budget: float
    gender: Optional[str]


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
