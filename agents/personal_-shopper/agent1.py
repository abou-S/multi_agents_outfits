import whisper
import json
import os
from groq import Groq

# 1) Ici on utilise juste whisper pour le moment 
model = whisper.load_model("small")

def transcrire_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path, language="fr")
    return result["text"].strip()

# 2) Client Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def texte_vers_json(texte: str) -> dict:
    prompt = f"""
Tu reçois la description d'un besoin vestimentaire en français.

Tu DOIS renvoyer UNIQUEMENT un JSON valide avec exactement ces clés :
- "budget" : nombre en euros (ou null si tu ne sais pas)
- "evenement" : type d'événement (ex: "anniversaire", "mariage", "soirée", "entretien", "sortie entre amis", etc.)
- "sexe" : "homme", "femme" ou "inconnu"
- "style" : style vestimentaire souhaité
- "preferences" : liste de contraintes ou préférences

Si tu n'es pas sûr de l'évènement, mets "inconnu" dans "evenement".
Ne renvoie rien d'autre que le JSON.

Texte utilisateur :
\"\"\"{texte}\"\"\""""

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Tu es un parseur qui ne renvoie que du JSON valide."},
            {"role": "user", "content": prompt},
        ],
    )

    raw = chat.choices[0].message.content
    parsed = json.loads(raw)

    # ------------------------------------------------------------------
    # 🔧 Correctifs automatiques
    # ------------------------------------------------------------------

    # 1. Correction des fautes d'événements
    ev = parsed.get("evenement", "").lower()

    corrections_evenement = {
        "soiré": "soirée",
        "soire": "soirée",
        "soirée ": "soirée",
        "anniveraire": "anniversaire",
        "anniv": "anniversaire",
        "birthday": "anniversaire",
        "batéme" : "baptême",
        
    }

    if ev in corrections_evenement:
        parsed["evenement"] = corrections_evenement[ev]

    # 2. Nettoyage des préférences
    prefs = parsed.get("preferences", [])
    prefs_a_supprimer = [
        "conforme au style",
        "aucune",
        "rien",
        "aucun",
        "",
    ]

    parsed["preferences"] = [
        p for p in prefs if p.lower() not in prefs_a_supprimer
    ]

    if not parsed["preferences"]:
        parsed["preferences"] = []

    return parsed


def agent1(audio_path: str) -> dict:
    texte = transcrire_audio(audio_path)
    infos = texte_vers_json(texte)
    return infos


if __name__ == "__main__":
    data = agent1("demo.wav")
    print(json.dumps(data, indent=2, ensure_ascii=False))
