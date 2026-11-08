# AWS IP Checker

Application web Flask qui vérifie si une adresse IP appartient à AWS, à partir des plages publiées par AWS
([ip-ranges.json](https://ip-ranges.amazonaws.com/ip-ranges.json)).

## Fonctionnalités

1. **Vérifier une IP** : indique si l'IP est AWS et, si oui, affiche pour chaque plage la région, le service,
   la première et la dernière IP ainsi que le nombre d'IPs.
2. **Vérifier une liste d'IPs** : indique si toutes les IPs sont AWS et si elles appartiennent à une même plage AWS.

Le fichier AWS est téléchargé une seule fois puis gardé en cache (`lru_cache`).

## Structure

```
app.py              # routes Flask
awsip.py            # logique métier (+ utilisable en ligne de commande)
templates/index.html
static/app.js
static/style.css
tests/              # tests unitaires (pytest)
API.md              # contrat de l'API
pyproject.toml      # dépendances (uv)
uv.lock             # versions figées (généré par uv, à commiter)
```

## Installation

Le projet utilise [uv](https://docs.astral.sh/uv/).

```bash
uv sync          # crée .venv et installe les dépendances (dont pytest)
```

## Utilisation

**Interface web**

```bash
uv run app.py
```
Puis ouvrir http://127.0.0.1:5000

**Ligne de commande**

```bash
uv run awsip.py 3.5.140.10                          # une IP
uv run awsip.py 3.5.140.10 3.5.141.2 8.8.8.8 ...    # une liste d'IPs
```

## API

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/lookup?ip=<ip>` | Plages AWS contenant l'IP |
| POST | `/api/check-list` | Body `{"ips": [...]}` : toutes AWS ? même réseau ? |

Détails des réponses et des erreurs : voir [API.md](docs/API.md).

## Tests

```bash
uv run pytest -q
```

Les tests n'utilisent pas le réseau : les données AWS sont remplacées par un faux jeu.

## Workflow Git

- Une branche par petite fonctionnalité : `feature/<nom>`
- Petits commits : `feat: ...`, `fix: ...`, `test: ...`, `refactor: ...`

## Auteurs

- Djrado ZOUNMENOU
- Pinhas GUIDI

Projet réalisé dans le cadre du TP Git – ESIGELEC.