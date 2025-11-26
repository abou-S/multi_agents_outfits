# multi_agents_outfits

Ce dépôt contient un petit projet d'analyse d'événements vestimentaires et des prompts destinés à un modèle LLM.

Contenu confirmé (racine du dépôt)
- requirements.txt
- multi_agents/  
  - prompts/event_analyzer_system.txt  (prompt système utilisé pour l'analyse d'événements)

But de ce projet
- Fournir un prompt et une logique (à implémenter) pour convertir des descriptions d'événements en un JSON structuré pour guider le choix vestimentaire.
- Fournir un point de départ pour exécuter une requête LLM en local.

1. Prérequis
- Python 3.8+
- Une clé OpenAI (ou autre clé pour l'API LLM que vous utilisez)
- Git (optionnel)

2. Installation
1) Créer et activer un environnement virtuel :
   - Linux / macOS:
     - python -m venv .venv
     - source .venv/bin/activate
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1

2) Installer les dépendances :
   - pip install -r requirements.txt

3. Configuration (clé API)
- Créez un fichier `.env` à la racine contenant au minimum :
  OPENAI_API_KEY=sk_...
- Le projet utilise python-dotenv si vous souhaitez charger automatiquement `.env`.

4. Exécution — démonstrateur minimal (exemple)
- Le dépôt contient le prompt système dans :
  `multi_agents/prompts/event_analyzer_system.txt`

- Exemple rapide (fonctionnera sans code supplémentaire du dépôt) :
  1) Sauvegardez votre description d'événement dans une variable shell, puis exécutez ce court script Python qui lit le prompt et appelle l'API OpenAI (nécessite `openai` installé et OPENAI_API_KEY défini) :

  ```bash
  # Exemple (bash)
  export OPENAI_API_KEY="votre_cle"
  python - <<'PY'
  import os, openai, json
  # ...existing code...
  prompt = open("multi_agents/prompts/event_analyzer_system.txt", "r", encoding="utf-8").read()
  user_description = "Soirée d'entreprise informelle en intérieur, budget 80. Femme, soirée en début de soirée."
  full = prompt + "\n\nUtilisateur: " + user_description + "\n\nRéponds:"
  openai.api_key = os.getenv("OPENAI_API_KEY")
  resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"system","content":prompt},{"role":"user","content":user_description}], max_tokens=400)
  # Affiche le texte brut renvoyé par le modèle
  print(resp["choices"][0]["message"]["content"])
  PY
  ```

  - Adaptez le modèle (`gpt-4o-mini`) en fonction de votre accès.

5. Tests
- Si des tests existent, exécutez :
  - pytest -q
- Installation pytest (si nécessaire) :
  - pip install pytest

6. Structure recommandée (ce que j'ai créé)
- multi_agents/
  - prompts/
    - event_analyzer_system.txt   # prompt système (présent)
  - (code d'API / CLI / modules)  # à implémenter ou à consulter si déjà présent
- requirements.txt
- README.md

7. Conseils d'usage et bonnes pratiques
- Toujours valider la sortie JSON du LLM (parser strict) avant intégration.
- Ne jamais exposer la clé API dans le dépôt.
- Pour automatiser localement, créez un petit module `multi_agents/cli.py` qui :
  - lit une description d'événement,
  - lit le prompt système,
  - appelle l'API LLM,
  - valide et normalise le JSON de sortie.

Dépannage rapide
- ModuleNotFoundError: vérifiez l'activation du venv et l'installation des dépendances.
- "401 Unauthorized" de l'API: vérifiez `OPENAI_API_KEY`.
- Réponse non-JSON: forcez le modèle à répondre strictement en JSON (le prompt système le demande déjà).

Fin.