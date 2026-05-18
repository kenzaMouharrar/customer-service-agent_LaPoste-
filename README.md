# La Poste Agent - Demo IA Service Client

Ce projet est une demo d'agent IA de service client pour La Poste, basee sur un workflow LangGraph.

L'application prend des evenements entrants (emails, formulaires, appels), enrichit le contexte client, interroge une base documentaire RAG, puis produit:

- une decision (creation de ticket ou non),
- un niveau d'escalade eventuel,
- un brouillon de reponse client.

## Vous trouvez dans ce lien pour une démo enregistré en vidéo

https://drive.google.com/drive/folders/1r920vlwMuS4a7EENGCffKqUKtOh1bbVD?usp=sharing

## Objectif du projet

- Simuler un traitement intelligent des demandes clients multi-canaux.
- Illustrer un pipeline agentique orchestrant plusieurs etapes metier.
- Fournir une interface Streamlit pour visualiser les demandes et les resultats.

## Structure du projet

### Racine

- `main.py`: point d'entree Python minimal.
- `pyproject.toml`: metadonnees projet et dependances principales.
- `requirements.txt`: actuellement vide.
- `scripts/run_demo.py`: lance des scenarios de demo sur des evenements JSON.
- `tests/`: tests unitaires et tests de workflow.

### Dossier `app/`

- `app/core/`: composants transverses (config, logger, LLM, utilitaires).
- `app/graph/workflow.py`: coeur du workflow LangGraph.
- `app/models/`: schemas et enums metier.
- `app/rag/`: indexation/recherche RAG hybride (BM25 + FAISS + RRF).
- `app/services/`: mocks de services externes (CRM, ticketing, mailer, etc.).
- `app/ui/`: interfaces Streamlit (dashboard conseiller).

### Donnees

- `data/events/`: evenements d'entree de demo (email, call, form).
- `data/rag_docs/`: documents markdown servant de base de connaissance.
- `data/runtime/rag/`: index RAG persistants (FAISS, BM25, chunks).
- `data/crm/` et `data/tickets/`: donnees de simulation.

## Prerequis

- Python 3.11+
- Une cle API Mistral valide (variable `MISTRAL_API_KEY`)

## Installation

### Option 1 - avec `uv` (recommande)

1. Installer les dependances:

```bash
uv sync
```

2. Creer un fichier `.env` a la racine du projet:

```env
MISTRAL_API_KEY=ta_cle_api_mistral
```

### Option 2 - avec `pip`

1. Creer et activer un environnement virtuel:

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat
```

2. Installer les dependances declarees dans `pyproject.toml`:

```bash
pip install -e .
```

3. Creer le fichier `.env`:

```env
MISTRAL_API_KEY=ta_cle_api_mistral
```

## Lancer l'application

### 1) Interface Streamlit principale

Depuis la racine du projet:

```bash
streamlit run app/ui/streamlit_app.py
```

L'interface s'ouvre dans le navigateur (en general sur `http://localhost:8501`).

### 2) Executer la demo workflow en ligne de commande

Scenario par defaut:

```bash
python scripts/run_demo.py
```

Tous les scenarios:

```bash
python scripts/run_demo.py --all
```

Resume compact:

```bash
python scripts/run_demo.py --summary
```

Scenario specifique:

```bash
python scripts/run_demo.py event_003_critical.json
```

## RAG: (re)construire les index

Si les index RAG sont absents/corrompus, reconstruire:

```bash
python -m app.rag.indexer
```

## Lancer les tests

```bash
pytest -q
```

## Notes importantes

- Sans `MISTRAL_API_KEY`, la generation de brouillon via LLM ne demarrera pas.
- Le dossier `data/runtime/rag/` contient des index deja presents dans ce workspace.
- Les fichiers de `app/ui/` incluent plusieurs variantes d'interface Streamlit; `streamlit_app.py` est l'entree principale actuelle.
