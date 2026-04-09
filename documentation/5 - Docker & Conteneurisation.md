# 5 - Docker & Conteneurisation

## Choix techniques

### Dockerfile

Le Dockerfile suit une approche multi-stage:

- Le stage `build` cree l'environnement virtuel et installe les dependances Python.
- Le stage `production` ne recopie que l'environnement virtuel et le code utile a l'execution.

Ce choix reduit la surface de l'image finale et evite d'embarquer des fichiers de build inutiles.

La base retenue est `python:3.12-slim`. C'est un compromis simple et robuste:

- plus legere qu'une image Debian complete,
- plus facile a maintenir qu'une image distroless pour un projet pedagogique,
- compatible avec l'execution de `uvicorn` et du `HEALTHCHECK` Python.

L'image finale tourne en utilisateur non-root via `app`, ce qui limite l'impact d'une compromission du conteneur.

### Optimisation du cache

L'ordre des instructions est volontaire:

1. creation de l'environnement virtuel,
2. copie du fichier de dependances verrouillees,
3. installation des dependances,
4. copie du code source.

Ainsi, une modification du code applicatif ne reinvalide pas la couche d'installation des dependances. Les rebuilds sont donc plus rapides.

### Compose local

Le fichier `docker-compose.yml` sert au developpement local avec deux services:

- `app` pour l'API FastAPI,
- `db` pour PostgreSQL.

Le volume `postgres_data` conserve les donnees, et le reseau `app_network` isole les services du projet.

### Securite

Les secrets ne sont pas inscrits dans l'image. La configuration passe par les variables d'environnement et le fichier `.env.example` documente le format attendu sans embarquer d'information sensible.

Un `HEALTHCHECK` applicatif est present pour verifier que l'API repond sur `/health`.

## Taille de l'image

Mesure effectuee localement le 2026-04-09:

```bash
docker build -t tp03-app:local .
docker image inspect tp03-app:local --format '{{.Size}}'
```

Resultat:

- `199500302` octets
- environ `199.5 MB`

Le seuil demande de moins de `200MB` est donc respecte, mais avec peu de marge.

## Trivy en CI

Ce point n'est pas encore implemente.

Il reste present dans le backlog du projet comme exigence a traiter ensuite:

- construire l'image dans la CI,
- lancer un scan Trivy sur l'image finale,
- faire echouer le pipeline sur les vulnerabilites `HIGH` et `CRITICAL` selon la politique retenue.
