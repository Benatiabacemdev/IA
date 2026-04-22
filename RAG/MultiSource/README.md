# RAG MultiSource

Système de **Retrieval-Augmented Generation (RAG)** permettant d'ingérer des documents PDF depuis plusieurs sources (dossier local et SharePoint Microsoft), de les indexer dans une base vectorielle, puis d'interroger leur contenu via une interface de chat conversationnel.

Le LLM et le modèle d'embeddings tournent **entièrement en local** grâce à [Ollama](https://ollama.com/), sans aucun envoi de données vers des API cloud.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Structure du projet](#structure-du-projet)
- [Pipeline de données](#pipeline-de-données)

---

## Fonctionnalités

- **Chat conversationnel** sur vos documents, avec mémoire de la conversation
- **Synchronisation locale** : sélection d'un dossier et ingestion automatique des PDFs
- **Synchronisation SharePoint** : connexion via Microsoft Graph API (OAuth2 / Azure AD)
- **Détection des changements** : les documents déjà synchronisés sont ignorés ; ceux modifiés sont mis à jour
- **Administration du vector store** : consultation et suppression des collections Qdrant
- **100 % local** : LLM, embeddings et base vectorielle hébergés sur votre infrastructure

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Interface Streamlit                      │
│                                                             │
│  ┌──────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│  │   Chat   │   │ Synchronisation │   │  Vector Store   │  │
│  │ (home)   │   │  Local / SP     │   │    Settings     │  │
│  └────┬─────┘   └────────┬────────┘   └────────┬────────┘  │
└───────┼──────────────────┼────────────────────┼────────────┘
        │                  │                     │
        ▼                  ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                       Couche Helpers                       │
│                                                           │
│  ┌──────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  RAGHelper   │  │  QdrantHelper  │  │PostgresHelper │ │
│  │  (PDF/chunk) │  │  (embeddings)  │  │  (metadata)   │ │
│  └──────────────┘  └────────────────┘  └───────────────┘ │
│                                                           │
│  ┌──────────────────────────────────┐                     │
│  │       SharePointHelper           │                     │
│  │  (Microsoft Graph API / OAuth2)  │                     │
│  └──────────────────────────────────┘                     │
└───────────────────────────────────────────────────────────┘
        │                  │                     │
        ▼                  ▼                     ▼
┌─────────────┐   ┌─────────────────┐   ┌──────────────────┐
│   Ollama    │   │     Qdrant      │   │   PostgreSQL     │
│  LLM local  │   │  Vector Store   │   │   Métadonnées    │
│  port 11434 │   │   port 6333     │   │   port 5432      │
└─────────────┘   └─────────────────┘   └──────────────────┘
```

---

## Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| UI | [Streamlit](https://streamlit.io/) | Interface web multi-pages |
| Orchestration RAG | [LangChain](https://www.langchain.com/) | Chaîne de retrieval + mémoire conversationnelle |
| LLM local | [Ollama](https://ollama.com/) (`qwen3:0.6b`) | Inférence du modèle de langage |
| Embeddings | OllamaEmbeddings (1024 dims, cosine) | Vectorisation des chunks |
| Base vectorielle | [Qdrant](https://qdrant.tech/) | Recherche sémantique |
| Métadonnées | [PostgreSQL](https://www.postgresql.org/) | Suivi des documents ingérés |
| Extraction PDF | PyPDF2 | Lecture et extraction du texte PDF |
| Auth cloud | MSAL + azure-identity | OAuth2 / Azure Active Directory |
| API SharePoint | Microsoft Graph API | Liste et téléchargement des fichiers |
| Infrastructure | Docker Compose | Orchestration des services |
| Accélération | NVIDIA GPU (optionnel) | Réservation GPU pour Ollama |

---

## Prérequis

- **Docker** et **Docker Compose**
- **Python 3.10+**
- **Ollama** installé et le modèle tiré (`ollama pull qwen3:0.6b`)
- Un tenant **Azure / Microsoft 365** avec une App Registration (pour SharePoint)
- GPU NVIDIA optionnel (le `docker-compose.yml` le configure automatiquement)

---

## Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd RAG/MultiSource

# 2. Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux / macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer les volumes Docker nécessaires
docker volume create qdrant_storage
docker volume create ollama_storage

# 5. Démarrer les services
docker-compose up -d
```

---

## Configuration

Créer le fichier `env/.env` à partir du modèle ci-dessous :

```env
# --- LLM (Ollama) ---
LLM_NAME=qwen3:0.6b
LLM_URL=http://localhost:11434

# --- Qdrant ---
DB_QD_LOCATION=localhost
DB_QD_PORT=6333
DB_QD_API_KEY=
DB_QD_COLLECTION_NAME=documents

# --- PostgreSQL ---
DB_PG_HOST=localhost
DB_PG_PORT=5432
DB_PG_NAME=LLM-UIDs
DB_PG_USER=sample
DB_PG_PASSWORD=sample

# --- SharePoint / Azure AD ---
SP_CLIENT_ID=<app-registration-client-id>
SP_CLIENT_SECRET=<app-registration-client-secret>
SP_TENANT_ID=<azure-tenant-id>
SP_SITE_URL=<tenant>.sharepoint.com/sites/<site-name>
```

> **Important :** ne jamais commiter ce fichier. Vérifier que `env/.env` figure dans `.gitignore`.

### Créer l'App Registration Azure (pour SharePoint)

1. Aller dans **Azure Portal → App registrations → New registration**
2. Ajouter les permissions API Microsoft Graph : `Sites.Read.All`, `Files.Read.All`
3. Créer un **client secret** et reporter les valeurs dans `.env`

---

## Démarrage

```bash
# Lancer l'application Streamlit
streamlit run app.py
```

L'application est accessible sur `http://localhost:8501`.

| Service | URL | Usage |
|---|---|---|
| Application | http://localhost:8501 | Interface principale |
| Qdrant Dashboard | http://localhost:6333/dashboard | Exploration des vecteurs |
| Adminer (DB admin) | http://localhost:8080 | Administration PostgreSQL |
| Ollama API | http://localhost:11434 | API LLM locale |

---

## Structure du projet

```
MultiSource/
│
├── app.py                          # Point d'entrée Streamlit — routing des pages
├── requirements.txt                # Dépendances Python
├── docker-compose.yml              # Orchestration des services (Ollama, Qdrant, PG, Adminer)
│
├── env/
│   └── .env                        # Variables d'environnement (non versionné)
│
├── models/
│   └── document.py                 # Dataclass DocumentModel
│
├── helpers/
│   ├── ragHelper.py                # Extraction PDF (PyPDF2) + découpage en chunks
│   ├── qdrantHelper.py             # Connexion Qdrant, ajout/suppression de vecteurs
│   ├── postgresHelper.py           # CRUD métadonnées documents
│   ├── sharepointHelper.py         # Intégration Microsoft Graph API (auth + liste + téléchargement)
│   └── sharepointRestHelper.py     # Intégration alternative via REST API SharePoint
│
├── pages/
│   ├── home.py                     # Interface de chat (ConversationalRetrievalChain)
│   ├── synchronisation.py          # Sync documents : onglets Local et SharePoint
│   ├── qdrantSettings.py           # Administration du vector store
│   └── admins.py                   # Upload manuel PDF (désactivé)
│
├── templates/
│   └── htmlTemplates.py            # Templates HTML/CSS pour l'affichage du chat
│
└── database/
    └── dbConfig.gz                 # Sauvegarde de la base PostgreSQL
```

---

## Pipeline de données

### Ingestion (synchronisation)

```
Dossier local / SharePoint
         │
         ▼
  Listage des PDFs
         │
         ▼
  Pour chaque fichier :
  ┌──────────────────────────────────────────────┐
  │  Vérification en base (nom + chemin + taille │
  │  + dates) → déjà synchronisé ? → skip        │
  │  Modifié ? → suppression des anciens vecteurs │
  └──────────────────────────────────────────────┘
         │
         ▼
  Extraction texte (PyPDF2)
         │
         ▼
  Découpage en chunks (1000 chars, overlap 200)
         │
         ▼
  Génération des embeddings (OllamaEmbeddings, 1024 dims)
         │
         ▼
  Stockage vecteurs → Qdrant
  Stockage métadonnées → PostgreSQL
```

### Requête (chat)

```
Question utilisateur
         │
         ▼
  ConversationalRetrievalChain (LangChain)
         │
         ├── Embedding de la question (Ollama)
         │         │
         │         ▼
         │   Recherche sémantique (Qdrant, cosine similarity)
         │         │
         │         ▼
         │   Chunks pertinents récupérés
         │
         ▼
  LLM (qwen3:0.6b via Ollama) génère la réponse
  avec les chunks comme contexte
         │
         ▼
  Mémoire conversationnelle mise à jour
  (ConversationBufferMemory)
         │
         ▼
  Réponse affichée (balises <think> filtrées)
```
