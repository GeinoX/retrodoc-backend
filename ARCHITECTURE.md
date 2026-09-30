# Architecture du backend RetroDoc

## Séparation des dépôts

- `retrodoc-frontend` — application React, consomme l'API REST versionnée.
- `retrodoc-backend` (ce dépôt) — API Django REST Framework.

Toute communication entre les deux passe exclusivement par l'API versionnée
(`/api/v1/...`). Aucun accès direct à la base de données depuis le frontend.

## Structure du dépôt backend

retrodoc-backend/
├── config/ # Configuration du projet (voir ci-dessous), aucune logique métier
├── apps/ # Applications de domaine métier
│ ├── accounts/
│ ├── documents/
│ ├── lost_reports/
│ ├── found_reports/
│ ├── matching/
│ ├── stations/
│ ├── notifications/
│ ├── handovers/
│ ├── audit/
│ └── administration/
├── api/ # Exposition REST (routage, sérialisation), namespace /api/v1/
├── tests/ # Tests transverses (parcours de bout en bout)
└── manage.py


## `config/` — configuration uniquement

- `settings/base.py`, `settings/development.py`, `settings/production.py` : réglages Django.
- `urls.py`, `asgi.py`, `wsgi.py` : points d'entrée du projet.

Aucune règle métier ne doit être écrite dans `config/`.

## `apps/<domaine>/` — une application par domaine métier

Chaque application représente **un seul domaine** de responsabilité :

| Application | Responsabilité |
|---|---|
| `accounts` | Comptes utilisateurs, agents, authentification |
| `documents` | Documents d'identité (types, données de base) |
| `lost_reports` | Signalements de documents perdus |
| `found_reports` | Déclarations de documents trouvés |
| `matching` | Rapprochement entre documents perdus et trouvés |
| `stations` | Postes de police |
| `notifications` | Envoi de notifications (e-mail, etc.) |
| `handovers` | Remise physique d'un document récupéré |
| `audit` | Journal des actions sensibles (recherches, accès) |
| `administration` | Gestion administrative interne |

### Convention interne à chaque application

- `models.py` — structure des données, règles de validation au niveau du modèle.
- `services.py` — logique métier qui ne tient pas dans une méthode de modèle
  (calculs, coordination entre plusieurs modèles, règles de décision).
  **Les vues ne contiennent jamais de logique métier : elles appellent les services.**
- `serializers.py` — traduction entre objets Python/Django et JSON, pour l'API.
- `views.py` — reçoit la requête HTTP, appelle un service ou un serializer, renvoie une réponse.
- `admin.py` — intégration à l'administration Django.
- `tests.py` (ou dossier `tests/`) — tests propres à cette application.

## `api/` — exposition REST uniquement

Contient le routage (`/api/v1/...`) et regroupe les `serializers.py` exposés
publiquement. Ne contient **aucune** règle métier : celle-ci vit toujours dans
l'application de domaine correspondante.

## Nommage

- Applications : `snake_case`, au pluriel quand elles gèrent une collection
  (`lost_reports`, `stations`), au singulier sinon (`matching`, `audit`).
- Modèles : `PascalCase` (`LostReport`, `Station`).
- Fichiers et fonctions : `snake_case`.

## État actuel de la migration

L'application historique `retrouves/` regroupe encore, à ce jour, plusieurs des
domaines listés ci-dessus (documents, postes de police, déclarations). Elle
continue de fonctionner telle quelle. Sa répartition progressive vers les
applications `apps/` correspondantes fera l'objet de tâches dédiées ultérieures,
domaine par domaine, pour éviter de perturber les migrations de base de données
existantes.