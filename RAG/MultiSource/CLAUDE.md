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
