# MyOutfit
Description
- MyOutfit est un système multi-agent qui aide les personnes sans idée de tenue à préparer une tenue pour un événement (ex. mariage, sortie, soirée).
- L'utilisateur peut décrire sa demande par écrit ou par message vocal, en précisant son budget.
- Le multi-agent propose des idées de tenues adaptées au contexte et au budget, liste les articles avec références (liens ou identifiants) et fournit pour chaque tenue une image du mannequin (photo de la personne) portant la tenue afin de visualiser le rendu.
- L'objectif : proposer des looks simples, respectant le budget, avec les références produit pour faciliter l'achat.

Capture d'écran
- Voici un aperçu de l'application.

![MyOutfit - capture d'écran](assets/Screenshot-MyOutfit.png)

Prérequis
- Python 3.8+
- Clé API Groq (ou autre LLM compatible) dans la variable d'environnement `GROQ_API_KEY`
- Dépendances : pip install -r requirements.txt

Installation rapide
1. Créez et activez un environnement virtuel (optionnel mais recommandé)
   - macOS / Linux:
     python -m venv .venv
     source .venv/bin/activate
   - Windows (PowerShell):
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1

2. Installez les dépendances :
   pip install -r requirements.txt

Configuration
- Créez un fichier `.env` à la racine (ou exportez les variables). Ne commitez jamais ce fichier.
- Variables requises (chaque variable sur sa propre ligne) :
```env
GROQ_API_KEY="votre_groq_api_key
APIFY_API_TOKEN="votre_apify_api_token"
APIFY_ZALANDO_ACTOR_ID="votre_apify_zalando_actor_id"
```

Où sont les prompts ?
- Les prompts systèmes se trouve dans :
  multi_agents/prompts/

Exemple d'exécution:
```bash
streamlit run streamlit_app.py
```