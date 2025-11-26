import os
import sys
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Assurer que le package local multi_agents est importable
CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(CURRENT_DIR)

from multi_agents.orchestrator import Orchestrator  # type: ignore

load_dotenv()


def run_pipeline_with_orchestrator(
    description: str,
    budget: Optional[float],
    gender: str,
    age: Optional[int],
    user_image_url: Optional[str],
) -> Dict[str, Any]:
    orchestrator = Orchestrator()
    result = orchestrator.run_pipeline(
        description=description,
        ui_budget=budget,
        ui_gender=gender,
        ui_age=age,
        user_image_url=user_image_url,
    )
    return result


# ------------ UI Streamlit ------------ #

st.set_page_config(
    page_title="AI Outfit Assistant",
    page_icon="🧥",
    layout="wide",
)

# Un peu de CSS pour rendre l’UI plus clean
st.markdown(
    """
    <style>
    .outfit-card {
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        background-color: #ffffff;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }
    .items-scroll {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding-bottom: 0.5rem;
        margin-top: 0.5rem;
    }
    .item-card {
        min-width: 210px;
        max-width: 220px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        padding: 0.75rem;
        background-color: #f9fafb;
        flex-shrink: 0;
    }
    .item-card img {
        width: 100%;
        border-radius: 10px;
        object-fit: cover;
    }
    .item-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.4rem;
        margin-bottom: 0.1rem;
    }
    .item-meta {
        font-size: 0.8rem;
        color: #4b5563;
        margin: 0;
    }
    .item-link {
        font-size: 0.8rem;
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }
    .item-link:hover {
        text-decoration: underline;
    }
    .small-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ====== Header ====== #
st.title("🧥 AI Outfit Assistant")
st.caption("Trouve des tenues adaptées à ton événement, ton style et ton budget – avec preview visuelle IA.")

# ====== Formulaire (full width, comme ton wireframe) ====== #
st.markdown("---")
st.subheader("📝 Décris ton besoin")

with st.form("outfit_form"):
    description = st.text_area(
        "Décris l'événement et ton style",
        value="Je vais à un mariage le soir, ambiance chic, style minimaliste.",
        help="Parle de l'événement, du contexte, de ton style, etc.",
        height=140,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        budget_str = st.text_input(
            "Budget total (en € – optionnel)",
            value="150",
            help="Laisse vide si tu veux que l'IA l'infère à partir de ta description.",
        )

    with col2:
        gender = st.selectbox(
            "Genre",
            options=["homme", "femme"],
            index=0,
        )

    with col3:
        age_str = st.text_input(
            "Âge (optionnel)",
            value="30",
        )

    user_image_url = st.text_input(
        "URL de ta photo (optionnel)",
        value="",
        help="Pour l'instant, colle ici une URL d'image publique (raw GitHub, hébergeur d'image, etc.).",
    )

    submitted = st.form_submit_button("🚀 Générer les tenues")


# ====== Helpers pour parser les nombres ====== #
def parse_float(x: str) -> Optional[float]:
    x = x.strip()
    if not x:
        return None
    try:
        return float(x.replace(",", "."))
    except ValueError:
        return None


def parse_int(x: str) -> Optional[int]:
    x = x.strip()
    if not x:
        return None
    try:
        return int(x)
    except ValueError:
        return None


budget = parse_float(budget_str)
age = parse_int(age_str)
user_image_url = user_image_url.strip() or None


# ====== Logique principale ====== #
if submitted:
    if not description.strip():
        st.error("Merci de décrire l'événement avant de lancer l'analyse.")
    else:
        with st.spinner("Analyse de l'événement, génération des tenues et recherche de produits... ⏳"):
            try:
                result = run_pipeline_with_orchestrator(
                    description=description,
                    budget=budget,
                    gender=gender,
                    age=age,
                    user_image_url=user_image_url,
                )
            except Exception as e:
                st.error(f"Erreur lors de l'exécution du pipeline : {e}")
                st.stop()

        event = result.get("event", {})
        product_search_output = result.get("product_search_output", {})
        final_outfits: List[Dict[str, Any]] = result.get("final_outfits", [])

        # ====== Logging backend du JSON final ====== #
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = logs_dir / f"session_{ts}.json"

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        st.success(f"Résultat sauvegardé dans `{log_path}` (backend).")

        # Bouton pour télécharger le JSON final directement
        st.download_button(
            label="💾 Télécharger le JSON complet",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name=f"outfit_session_{ts}.json",
            mime="application/json",
        )

        # ====== Bloc Analyse de l'événement (repliable) ====== #
        with st.expander("🧠 Analyse de ta demande (Event Analyzer)", expanded=False):
            st.json(event)

        # ====== Affichage des tenues finales ====== #
        st.markdown("---")
        st.subheader("👗 Tenues générées")

        if not final_outfits:
            st.warning(
                "Aucune tenue n'a pu être générée avec ces paramètres. "
                "Essaie avec un budget plus élevé ou une description différente."
            )
        else:
            for idx, outfit in enumerate(final_outfits):
                st.markdown(f"#### Tenue {idx + 1} — {outfit.get('style_name', 'Sans nom')}")

                # Container global pour la tenue (style carte)
                with st.container():
                    st.markdown('<div class="outfit-card">', unsafe_allow_html=True)

                    col_img, col_info = st.columns([1.3, 2])

                    # ==== Colonne image générée ==== #
                    with col_img:
                        preview_url = outfit.get("preview_image_url")
                        if preview_url:
                            st.image(preview_url, caption="Aperçu IA", use_container_width=True)
                        else:
                            st.info(
                                "Aucun aperçu visuel généré pour cette tenue "
                                "(pas de photo utilisateur ou erreur Modelslab)."
                            )

                    # ==== Colonne infos + articles ==== #
                    with col_info:
                        st.markdown(
                            f"<div class='small-label'>INFORMATIONS TENUE</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Description :** {outfit.get('description', '')}")
                        st.markdown(
                            f"**Formalité :** {outfit.get('formality_level', '').capitalize()} &nbsp;&nbsp; | "
                            f" **Total estimé :** {outfit.get('total_budget', 0):.2f} €"
                        )

                        items: List[Dict[str, Any]] = outfit.get("items", [])

                        if items:
                            st.markdown(
                                "<div class='small-label' style='margin-top:0.8rem;'>ARTICLES</div>",
                                unsafe_allow_html=True,
                            )

                            # Génération HTML des cards articles (scroll horizontal)
                            cards_html = "<div class='items-scroll'>"
                            for item in items:
                                chosen = item.get("chosen_product", {})
                                img_url = chosen.get("image")
                                product_name = chosen.get("name", "Produit")
                                brand = chosen.get("brand", "N/A")
                                color = chosen.get("color", "N/A")
                                price = chosen.get("price", 0)
                                url = chosen.get("url")

                                cards_html += "<div class='item-card'>"

                                if img_url:
                                    cards_html += f"<img src='{img_url}' alt='article' />"

                                cards_html += f"<div class='item-title'>{product_name}</div>"
                                cards_html += (
                                    f"<p class='item-meta'>Marque : {brand}<br/>"
                                    f"Couleur : {color}<br/>"
                                    f"Prix : {price:.2f} €</p>"
                                )
                                if url:
                                    cards_html += (
                                        f"<a class='item-link' href='{url}' target='_blank'>"
                                        "Voir sur le site marchand →</a>"
                                    )

                                cards_html += "</div>"  # fin item-card

                            cards_html += "</div>"  # fin items-scroll

                            st.markdown(cards_html, unsafe_allow_html=True)
                        else:
                            st.info("Aucun article trouvé pour cette tenue.")

                    st.markdown("</div>", unsafe_allow_html=True)  # fin outfit-card

                # Optionnel : prompt utilisé pour l'image (debug)
                if outfit.get("preview_prompt"):
                    with st.expander("🧪 Prompt utilisé pour l'image (debug)", expanded=False):
                        st.code(outfit["preview_prompt"])
