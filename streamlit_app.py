import os
import sys
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

# Assurer que le package local multi_agents est importable
CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(CURRENT_DIR)

from multi_agents.orchestrator import Orchestrator  # type: ignore

load_dotenv()


# ================== UI Streamlit ================== #

st.set_page_config(
    page_title="AI Outfit Assistant",
    page_icon="🧥",
    layout="wide",
)

# CSS perso (cartes + scroll horizontal)
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
st.caption("Décris ton événement, et l’IA génère des tenues complètes, des articles et un aperçu visuel.")


# ====== Formulaire ====== #
st.markdown("---")
st.subheader("📝 Décris ton besoin")

with st.form("outfit_form"):
    description_text = st.text_area(
        "Décris l'événement et ton style",
        value="Je vais à un mariage le soir, ambiance chic, style minimaliste.",
        height=140,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        budget_str = st.text_input("Budget total (€ – optionnel)", value="150")

    with col2:
        gender = st.selectbox("Genre", options=["homme", "femme"], index=0)

    with col3:
        age_str = st.text_input("Âge (optionnel)", value="30")

    user_image_url = st.text_input(
        "URL de ta photo (optionnel)",
        value="",
        help="Colle une URL d’image publique (raw GitHub, ou hébergement).",
    )

    submitted = st.form_submit_button("🚀 Générer les tenues")


# ====== Helpers ====== #
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


# ================== Pipeline avec progression ================== #
if submitted:
    if not description_text.strip():
        st.error("Merci de décrire l'événement avant de lancer l'analyse.")
        st.stop()

    final_description = description_text.strip()

    # Placeholders de statut
    progress_bar = st.progress(0, text="Initialisation du pipeline...")
    status_box = st.empty()

    orchestrator = Orchestrator()

    try:
        # 1) Analyse de l'événement
        progress_bar.progress(15, text="Analyse de ta demande (EventAnalyzer)...")
        status_box.info("🧠 Analyse de ta demande (type d'événement, moment de la journée, style, budget...)")
        event = orchestrator._run_event_analyzer(
            description=final_description,
            ui_budget=budget,
            ui_gender=gender,
            ui_age=age,
        )

        # 2) Génération des tenues par le Styliste
        progress_bar.progress(40, text="Génération des idées de tenues (Stylist)...")
        status_box.info("🎨 Le Styliste IA propose des idées de tenues adaptées à ton contexte et ton budget...")
        stylist_output = orchestrator._run_stylist(event)

        # 3) Recherche produits Zalando
        progress_bar.progress(70, text="Recherche des articles sur Zalando...")
        status_box.info("🛒 Recherche des articles correspondants sur Zalando (veste, chemise, chaussures, etc.)...")
        product_search_output = orchestrator._run_product_search(
            event=event,
            stylist_output=stylist_output,
        )

        # 4) Génération de l’aperçu IA (mannequin)
        if user_image_url:
            progress_bar.progress(90, text="Génération de l'aperçu visuel (mannequin IA)...")
            status_box.info("🧍‍♂️ Génération de l’aperçu visuel de la tenue sur ton mannequin...")
            final_outfits = orchestrator._run_visualizer(
                event=event,
                product_search_output=product_search_output,
                user_image_url=user_image_url,
            )
        else:
            progress_bar.progress(90, text="Finalisation des tenues (sans aperçu visuel)...")
            status_box.info("✅ Tenues générées (sans mannequin, aucune photo utilisateur fournie).")
            final_outfits = product_search_output["outfits"]

        progress_bar.progress(100, text="Terminé ✅")
        status_box.success("✨ Tenues générées avec succès !")

    except Exception as e:
        progress_bar.empty()
        status_box.error(f"Erreur lors du pipeline : {e}")
        st.stop()

    # ================== Affichage UI final ================== #

    # Résumé de l'événement
    st.markdown("---")
    st.subheader("🎯 Résumé de l'événement")

    event_type = event.get("event_type", "événement")
    time_of_day = event.get("time_of_day", "")
    formality = event.get("formality_level", "")
    style = event.get("style", "")
    ev_budget = event.get("budget")
    gender_ev = event.get("gender")
    age_ev = event.get("age")

    line = f"Tu cherches une tenue pour un **{event_type}**"
    if time_of_day:
        line += f" en **{time_of_day}**"
    if formality:
        line += f", style **{formality}**"
    if style:
        line += f", touche **{style}**"
    if ev_budget:
        line += f", budget **{ev_budget:.0f}€**"
    if gender_ev or age_ev:
        info = []
        if gender_ev:
            info.append(gender_ev)
        if age_ev:
            info.append(f"{age_ev} ans")
        line += f" ({', '.join(info)})."

    st.markdown(line)

    # Tenues
    st.markdown("---")
    st.subheader("👗 Tenues générées")

    if not final_outfits:
        st.warning("Aucune tenue trouvée. Essaie avec un budget plus élevé.")
        st.stop()

    for idx, outfit in enumerate(final_outfits):
        st.markdown(f"### Tenue {idx + 1} — {outfit.get('style_name', 'Sans nom')}")

        with st.container():
            st.markdown('<div class="outfit-card">', unsafe_allow_html=True)

            col_img, col_info = st.columns([1.3, 2])

            # Aperçu IA
            with col_img:
                preview = outfit.get("preview_image_url")
                if preview:
                    st.image(preview, caption="Aperçu IA", use_container_width=True)
                else:
                    st.info("Aucun aperçu visuel généré (pas de photo user ?).")

            # Infos tenue + articles
            with col_info:
                st.markdown(
                    "<div class='small-label'>INFORMATIONS TENUE</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(f"**Description :** {outfit.get('description', '')}")
                st.markdown(
                    f"**Formalité :** {outfit.get('formality_level', '').capitalize()} | "
                    f"**Total estimé :** {outfit.get('total_budget', 0):.2f} €"
                )

                items = outfit.get("items", [])
                if items:
                    st.markdown(
                        "<div class='small-label' style='margin-top:0.8rem;'>ARTICLES</div>",
                        unsafe_allow_html=True,
                    )

                    html = "<div class='items-scroll'>"
                    for item in items:
                        p = item.get("chosen_product", {})
                        img = p.get("image")
                        name = p.get("name", "Produit")
                        brand = p.get("brand", "N/A")
                        color = p.get("color", "N/A")
                        price = p.get("price", 0)
                        url = p.get("url", "")

                        html += "<div class='item-card'>"
                        if img:
                            html += f"<img src='{img}'/>"
                        html += f"<div class='item-title'>{name}</div>"
                        html += (
                            f"<p class='item-meta'>Marque : {brand}<br/>"
                            f"Couleur : {color}<br/>"
                            f"Prix : {price:.2f} €</p>"
                        )
                        if url:
                            html += (
                                f"<a class='item-link' href='{url}' target='_blank'>"
                                "Voir l’article →</a>"
                            )
                        html += "</div>"

                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.info("Aucun article pour cette tenue.")

            st.markdown("</div>", unsafe_allow_html=True)
