import os
import sys
from typing import Optional
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ====== Whisper (optionnel, si tu as un venv compatible) ====== #
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# ====== Micro recorder (pour le bouton d'enregistrement) ====== #
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

# Assurer que multi_agents est visible
CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(CURRENT_DIR)

from multi_agents.orchestrator import Orchestrator  # type: ignore

load_dotenv()


# ========= Whisper utils (audio -> texte) ========= #

@st.cache_resource
def load_whisper_model():
    """Charge le modèle Whisper 'small' une seule fois."""
    if not WHISPER_AVAILABLE:
        return None
    # Charge le modèle en RAM une seule fois
    return whisper.load_model("small")


def transcrire_audio_bytes(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Sauvegarde les bytes dans un fichier temporaire et lance Whisper dessus.
    Optimisé pour CPU avec FP32 explicite.
    """
    model = load_whisper_model()
    if model is None:
        raise RuntimeError("Whisper n'est pas disponible dans cet environnement.")

    tmp_dir = Path("tmp_audio")
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = tmp_dir / filename

    with open(tmp_path, "wb") as f:
        f.write(audio_bytes)

    # Options optimisées pour CPU
    result = model.transcribe(
        str(tmp_path),
        language="fr",
        fp16=False,  # Force FP32 pour éviter le warning
        verbose=False,  # Désactive les logs détaillés
    )
    
    return result["text"].strip()


# ========= Helpers ========= #

def to_float(x: str) -> Optional[float]:
    x = x.strip()
    if not x:
        return None
    try:
        return float(x.replace(",", "."))
    except ValueError:
        return None


def to_int(x: str) -> Optional[int]:
    x = x.strip()
    if not x:
        return None
    try:
        return int(x)
    except ValueError:
        return None


# ========= UI de base ========= #

st.set_page_config(
    page_title="AI Outfit Assistant",
    page_icon="🧥",
    layout="wide",
)

st.title("🧥 AI Outfit Assistant")
st.caption(
    "Décris ton événement en texte ou en vocal, et l'IA génère des tenues complètes "
    "avec aperçu visuel et liens produits."
)

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

st.markdown("---")
st.subheader("📝 Décris ton besoin")

# ========= Choix du mode d'entrée ========= #

mode = st.radio(
    "Mode d'entrée",
    options=["Texte", "Audio"],
    horizontal=True,
)

description_text: str = ""
audio_bytes: Optional[bytes] = None

if mode == "Texte":
    description_text = st.text_area(
        "Décris l'événement et ton style",
        value="Je vais à un mariage le soir, ambiance chic, style minimaliste.",
        height=140,
    )

else:
    st.markdown("### 🎙️ Enregistrement vocal")
    
    # Info sur les performances Whisper
    with st.expander("ℹ️ À propos de la transcription"):
        st.info(
            "**Transcription locale avec Whisper (modèle 'small')**\n\n"
            "⏱️ La première utilisation peut prendre 2-3 minutes (téléchargement du modèle).\n\n"
            "⏱️ Les transcriptions suivantes sont plus rapides (~30-60 secondes pour 1 min d'audio).\n\n"
            "💡 Garde tes enregistrements courts (15-30 sec) pour de meilleures performances."
        )

    if MIC_AVAILABLE:
        recorded_audio = mic_recorder(
            start_prompt="🎤 Cliquer pour enregistrer",
            stop_prompt="⏹️ Arrêter",
            just_once=True,
            use_container_width=True,
            format="wav",
        )
        if recorded_audio:
            audio_bytes = recorded_audio["bytes"]
            st.audio(audio_bytes, format="audio/wav")
    else:
        st.error(
            "Le composant `streamlit-mic-recorder` n'est pas installé.\n\n"
            "Installe-le avec : `pip install streamlit-mic-recorder`."
        )

    st.markdown("### 📁 Ou uploader un fichier audio")
    uploaded_file = st.file_uploader(
        "Importer un fichier audio (mp3, wav, ogg, webm, m4a)",
        type=["mp3", "wav", "ogg", "webm", "m4a"],
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        audio_bytes = file_bytes
        st.audio(audio_bytes)

# ========= Paramètres utilisateur ========= #

col1, col2, col3 = st.columns(3)
with col1:
    budget_input = st.text_input("Budget total (€ – optionnel)", value="150")
with col2:
    gender = st.selectbox("Genre", ["homme", "femme"], index=0)
with col3:
    age_input = st.text_input("Âge (optionnel)", value="30")

user_image_url = st.text_input(
    "URL de ta photo (optionnel)",
    value="",
    help="Colle une URL d'image publique (par ex. lien direct GitHub raw ou autre hébergeur).",
)

run_button = st.button("🚀 Générer les tenues")

budget = to_float(budget_input)
age = to_int(age_input)
user_image_url = user_image_url.strip() or None

# ========= Pipeline complet ========= #

if run_button:
    # 1) Obtenir la description finale

    if mode == "Texte":
        if not description_text.strip():
            st.error("Merci de décrire l'événement avant de lancer l'analyse.")
            st.stop()
        final_description = description_text.strip()
    else:
        if not WHISPER_AVAILABLE:
            st.error(
                "Whisper n'est pas disponible (`openai-whisper` non installé ou incompatible). "
                "Le mode audio ne peut pas fonctionner pour le moment."
            )
            st.stop()

        if audio_bytes is None:
            st.error("Aucun audio fourni (ni enregistrement, ni fichier uploadé).")
            st.stop()

        with st.spinner("🎧 Transcription en cours avec Whisper (cela peut prendre 30-60 secondes)..."):
            try:
                final_description = transcrire_audio_bytes(audio_bytes, "user_audio.wav")
            except Exception as e:
                st.error(f"Erreur lors de la transcription audio : {e}")
                st.stop()

        st.success("Transcription réussie ✅")
        st.info(f"Texte reconnu :\n\n> {final_description}")

    # 2) Exécuter le workflow par étapes

    orchestrator = Orchestrator()
    progress = st.progress(0, text="Initialisation du pipeline...")
    status = st.empty()

    try:
        # Event Analyzer
        progress.progress(15, text="Analyse de ta demande (EventAnalyzer)...")
        status.info("🧠 Analyse de l'événement (type, moment, style, budget...)")
        event = orchestrator._run_event_analyzer(
            description=final_description,
            ui_budget=budget,
            ui_gender=gender,
            ui_age=age,
        )

        # Stylist
        progress.progress(40, text="Génération des idées de tenues (Stylist)...")
        status.info("🎨 Le Styliste IA imagine plusieurs tenues adaptées.")
        stylist_output = orchestrator._run_stylist(event)

        # Product search
        progress.progress(70, text="Recherche des articles sur Zalando...")
        status.info("🛒 Recherche des vêtements correspondants (costume, chemise, chaussures, etc.)...")
        product_search_output = orchestrator._run_product_search(
            event=event,
            stylist_output=stylist_output,
        )

        # Visualizer
        if user_image_url:
            progress.progress(90, text="Génération de l'aperçu visuel (mannequin IA)...")
            status.info("🧍 Génération de l'aperçu visuel avec la tenue sur ton mannequin.")
            final_outfits = orchestrator._run_visualizer(
                event=event,
                product_search_output=product_search_output,
                user_image_url=user_image_url,
            )
        else:
            progress.progress(90, text="Finalisation des tenues (sans aperçu visuel)...")
            status.info("✅ Tenues générées (aucune photo utilisateur fournie).")
            final_outfits = product_search_output.get("outfits", [])

        progress.progress(100, text="Terminé ✅")
        status.success("✨ Tenues générées avec succès !")

    except Exception as e:
        progress.empty()
        status.error(f"Erreur lors de l'exécution du pipeline : {e}")
        st.stop()

    # 3) Affichage final

    st.markdown("---")
    st.subheader("🎯 Résumé de l'événement")

    event_type = event.get("event_type", "événement")
    time_of_day = event.get("time_of_day", "")
    formality = event.get("formality_level", "")
    style = event.get("style", "")
    ev_budget = event.get("budget")
    gender_ev = event.get("gender")
    age_ev = event.get("age")

    summary = f"Tu cherches une tenue pour un **{event_type}**"
    if time_of_day:
        summary += f" en **{time_of_day}**"
    if formality:
        summary += f", style **{formality}**"
    if style:
        summary += f", touche **{style}**"
    if ev_budget:
        summary += f", budget **{ev_budget:.0f}€**"
    if gender_ev or age_ev:
        infos = []
        if gender_ev:
            infos.append(gender_ev)
        if age_ev:
            infos.append(f"{age_ev} ans")
        summary += f" ({', '.join(infos)})."

    st.markdown(summary)

    st.markdown("---")
    st.subheader("👗 Tenues générées")

    if not final_outfits:
        st.warning("Aucune tenue trouvée. Essaie avec un budget légèrement plus élevé ou une description différente.")
        st.stop()

    for idx, outfit in enumerate(final_outfits):
        st.markdown(f"### Tenue {idx+1} — {outfit.get('style_name', 'Sans nom')}")

        with st.container():
            st.markdown('<div class="outfit-card">', unsafe_allow_html=True)

            col_img, col_info = st.columns([1.3, 2])

            # Image IA
            with col_img:
                preview = outfit.get("preview_image_url")
                if preview:
                    st.image(preview, caption="Aperçu IA", use_container_width=True)
                else:
                    st.info("Aucun aperçu visuel généré pour cette tenue.")

            # Infos + articles
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
                if not items:
                    st.info("Aucun article listé pour cette tenue.")
                else:
                    st.markdown(
                        "<div class='small-label' style='margin-top:0.8rem;'>ARTICLES</div>",
                        unsafe_allow_html=True,
                    )

                    html = "<div class='items-scroll'>"
                    for item in items:
                        prod = item.get("chosen_product", {})
                        img = prod.get("image")
                        name = prod.get("name", "Produit")
                        brand = prod.get("brand", "N/A")
                        color = prod.get("color", "N/A")
                        price = prod.get("price", 0)
                        url = prod.get("url", "")

                        html += "<div class='item-card'>"
                        if img:
                            html += f"<img src='{img}' alt='article' />"
                        html += f"<div class='item-title'>{name}</div>"
                        html += (
                            f"<p class='item-meta'>Marque : {brand}<br/>"
                            f"Couleur : {color}<br/>"
                            f"Prix : {price:.2f} €</p>"
                        )
                        if url:
                            html += (
                                f"<a class='item-link' href='{url}' target='_blank'>Voir l'article →</a>"
                            )
                        html += "</div>"

                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)