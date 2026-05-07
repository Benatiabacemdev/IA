# Project Overview

## Objective

Local RAG (Retrieval-Augmented Generation) application that lets users query documents from multiple sources using a locally-hosted LLM. Documents are indexed in a vector database and retrieved by semantic similarity to answer natural-language questions — without sending data to any external AI service.

## Tech stack

| Component | Technology |
|---|---|
| UI | Streamlit (multi-page) |
| LLM | Ollama (self-hosted, model configurable at runtime) |
| Embeddings | Ollama (`mxbai-embed-large`) |
| Vector store | Qdrant |
| Document sources | SharePoint (Microsoft Graph API), local filesystem |
| Sync metadata | PostgreSQL |

## Pages

| Page | Role |
|---|---|
| `home.py` | Chat interface — user asks questions, answers are generated via RAG |
| `synchronisation.py` | Ingests documents from SharePoint or local folders into the vector store; tracks sync state in PostgreSQL |
| `qdrantSettings.py` | Vector store inspection and management |

## RAG pipeline

1. **Ingestion** (`synchronisation.py`) — documents are fetched (SharePoint via Graph API or local FS), chunked by `RAGHelper`, embedded by Ollama, and stored in Qdrant. Sync state (file IDs, timestamps) is persisted in PostgreSQL to avoid re-indexing unchanged files.
2. **Retrieval** (`ConfidenceRetriever`) — custom LangChain retriever that filters chunks by cosine similarity threshold (≥ 0.65). Falls back to top-2 results if no chunk clears the threshold but at least one has score ≥ 0.3.
3. **Generation** (`home.py`) — retrieved chunks are assembled into a context string and injected into a strict prompt that forbids the LLM from using knowledge outside the provided context.

---

# Project Architecture Conventions

## Folder structure

| Folder | Role |
|---|---|
| `helpers/` | Helper classes and utility methods (DB clients, API wrappers, retrievers, etc.) |
| `models/` | Data/entity classes (dataclasses, domain objects with no business logic) |
| `pages/` | Streamlit pages — UI logic only, no reusable classes defined here |
| `templates/` | HTML/CSS templates used by Streamlit pages |
| `env/` | Environment configuration files (`.env`) |

## Rules

- **Never define helper classes or utility methods inside a page file.** If a class is reusable or not strictly UI logic, create it in `helpers/`.
- **Never define data models inside a page file.** Create them in `models/`.
- Pages import from `helpers/` and `models/`, not the other way around.
