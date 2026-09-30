# RetroDoc
## Structure du projet

- `config/` — configuration du projet, séparée du code métier :
  - `settings/base.py` — réglages communs à tous les environnements
  - `settings/development.py` — réglages de développement (utilisés par défaut)
  - `settings/production.py` — réglages de production
- `retrouves/` — application de domaine : documents, postes de police, profils agents
- `api/` — exposition REST (namespace `/api/v1/`), consommée par le frontend React

Chaque nouveau domaine métier doit être créé comme une application Django distincte
(`python manage.py startapp <nom>`), plutôt que d'ajouter du code dans `retrouves/`
ou `api/`. L'application `api/` ne doit contenir que du routage et de la sérialisation ;
la logique métier reste dans l'application de domaine correspondante.