# 🎭 Deauville Festival du Rire 2027

Projet Python orienté-objet — Festival du Rire de Deauville (10–13 juin 2027).

Application complète : modèle métier, stockage JSON, CLI interactive et API REST (FastAPI).

---

## Table des matières

- [Installation](#installation)
- [Lancement](#lancement)
- [Tests](#tests)
- [Structure du projet](#structure-du-projet)
- [Architecture & choix techniques](#architecture--choix-techniques)
- [Règles métier](#règles-métier)
- [État d'avancement](#état-davancement)

---

## Installation

```bash
git clone https://github.com/medhajita/deauville-starter-project.git
cd deauville-starter-project
uv sync
```

> Requiert Python 3.11+ et [uv](https://docs.astral.sh/uv/).

---

## Lancement

### CLI interactive

```bash
uv run main.py
```

Menu disponible :
1. Programme d'une journée
2. Liste des artistes
3. Spectacles en cours
4. 3 prochaines performances
5. En cours + à venir

### API REST (FastAPI)

```bash
uv run uvicorn api.app:app --reload
```

- API disponible sur `http://localhost:8000/api`
- Site public sur `http://localhost:8000/`
- Admin sur `http://localhost:8000/admin/`
- Documentation auto : `http://localhost:8000/docs`

---

## Tests

```bash
uv run pytest
uv run pytest -v          # détail
uv run pytest tests/test_performances.py  # un fichier
```

---

## Structure du projet

```
deauville-starter/
├── data/
│   └── festival.json          # Données persistantes (4 salles, 12 artistes, 23 spectacles)
│
├── festival/                  # Domaine métier (aucune dépendance externe)
│   ├── __init__.py
│   ├── artists.py             # class Artist
│   ├── venues.py              # class Venue
│   ├── performances.py        # Performance / SoloPerformance / LineupPerformance / WorkshopPerformance
│   ├── festival.py            # class Festival — orchestration + règles
│   ├── utils.py               # create_slug() — normalisation unicode
│   └── errors.py              # FestivalError / ValidationError / NotFoundError / ConflictError / StorageError
│
├── storage/
│   └── json_storage.py        # load_festival() / save_festival()
│
├── cli/
│   └── commands.py            # Affichage terminal
│
├── api/
│   ├── __init__.py
│   ├── app.py                 # Routes FastAPI
│   └── schemas.py             # Schémas Pydantic
│
├── tests/                     # Suite pytest
│   ├── conftest.py
│   ├── test_artists.py
│   ├── test_venues.py
│   ├── test_performances.py
│   ├── test_conflicts.py
│   ├── test_workshops.py
│   ├── test_programme.py
│   ├── test_storage.py
│   ├── test_updates.py
│   └── test_api.py
│
├── web/
│   ├── public/                # Site public (HTML/CSS/JS statiques)
│   └── admin/                 # Interface admin (HTML/CSS/JS statiques)
│
├── main.py                    # Point d'entrée CLI
└── pyproject.toml
```

---

## Architecture & choix techniques

### Objets du festival

| Classe | Responsabilité |
|--------|----------------|
| `Artist` | Nom, slug (auto-généré), bio, photo. Valide son propre nom. |
| `Venue` | Nom, slug, capacité (≥ 1), adresse. |
| `Performance` | Classe de base : title, venue, start, end, duration, festival_day, id. |
| `SoloPerformance` | Hérite de `Performance` + artiste solo + âge minimum. |
| `LineupPerformance` | Hérite de `Performance` + host + actes (≥ 2, durée minimale calculée). |
| `WorkshopPerformance` | Hérite de `Performance` + teacher + participants + max_participants. |
| `Festival` | Contient venues, artists, performances. Applique toutes les règles. |

### Héritage et polymorphisme

Les trois types de performances partagent la même base (`Performance`) : identifiant, timing, venue, `festival_day`. Ce qui diffère (artistes impliqués, règles de durée, participants) est dans les sous-classes. `Festival` utilise `isinstance` pour router la logique spécifique.

### Où vivent les règles ?

Toutes les règles métier passent par `Festival`. Aucune couche (CLI, API) ne peut ajouter une performance sans passer par `Festival.add_performance()` — qui enchaîne toutes les vérifications dans l'ordre. Le modèle ne peut pas être contourné.

### Gestion des erreurs

Hiérarchie d'exceptions personnalisées sous `FestivalError` :
- `ValidationError` — données invalides (nom vide, durée hors plage...)
- `NotFoundError` → HTTP 404
- `ConflictError` → HTTP 409
- `StorageError` — problème de lecture/écriture JSON

### Séparation stockage / modèle

`storage/json_storage.py` est la seule couche qui connaît JSON. Passer à SQLite ne touche que ce fichier — le domaine `festival/` est inchangé.

### Slug

La fonction `create_slug()` dans `utils.py` normalise les noms en supprimant les accents (NFD + filtre catégorie `Mn`), les caractères spéciaux, et en remplaçant les espaces par des tirets.

### ID performance

Construit à partir du slug de la salle et de l'heure de début : `"le-kiosque-2027-06-12-0100"`. Unique par construction (une salle ne peut pas avoir deux shows au même moment).

### Jour festival

Un spectacle débutant avant 06h00 appartient au jour précédent (`festival_day` = `start - 1 jour`).

### Sauvegarde atomique

`save_festival()` écrit d'abord dans un fichier `.tmp` puis le renomme — évite la corruption en cas d'interruption.

---

## Règles métier

| Règle | Appliquée dans |
|-------|----------------|
| Nom non vide (artiste, venue, titre, participant) | `__init__` de chaque classe |
| Capacité venue ≥ 1 | `Venue.__init__` |
| Durée performance : 1–360 min | `Performance.__init__` |
| Âge minimum : 0–18 | `SoloPerformance.__init__` |
| Lineup : ≥ 2 actes, host ∉ actes, durée min | `LineupPerformance.__init__` |
| Workshop : max_participants ≥ 1, noms uniques | `WorkshopPerformance.__init__` |
| Performance dans les jours du festival | `Festival.check_festival_day()` |
| Venue + artistes doivent exister | `Festival.check_performance_venue/artists()` |
| 30 min entre deux shows (même venue) | `Festival.check_venue_conflict()` |
| 30 min entre deux shows (même artiste) | `Festival.check_artist_conflict()` |
| Capacité workshop = min(max_participants, venue.capacity) | `Festival.get_performance_capacity()` |
| Participant unique (insensible à la casse) | `Festival.add_participant()` |
| Mise à jour atomique (rollback si échec) | `Festival.update_performance()` |

---

## État d'avancement

| Niveau | Statut | Détail |
|--------|--------|--------|
| P1 — Modèle + CLI | ✅ Fait | Toutes les règles, erreurs lisibles, CLI complète |
| P2 — Classes OOP | ✅ Fait | Héritage, encapsulation, exceptions custom, storage séparé |
| P3 — API REST | ✅ Fait | FastAPI, routes selon API.md, tests pytest |
| Extension SQLite | ❌ Non fait | — |

---

## Historique des fichiers

| Date | Fichiers |
|------|----------|
| 07/10/2026 | Squelette initial (`utils.py`, `web/`, `.gitignore`) |
| 11–12/10/2026 | Domaine métier (`performances.py`, `artists.py`, `venues.py`) |
| 20/10/2026 | `festival.py`, `errors.py` |
| 21/10/2026 | Tests complets (`test_artists` → `test_conflicts`) |
| 22/10/2026 | API FastAPI (`api/`), `cli/commands.py`, `main.py` |
| 23/10/2026 | Données JSON finalisées |

---

*Projet réalisé dans le cadre du cours de Programmation Orientée Objet — Msc IA, ECE Paris.*
