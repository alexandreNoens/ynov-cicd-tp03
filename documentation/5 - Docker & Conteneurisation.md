# 5 - Docker & Conteneurisation

## Choix techniques

### Dockerfile

Le Dockerfile suit une approche multi-stage:

- Le stage `build` cree l'environnement virtuel et installe les dependances Python.
- Le stage `production` ne recopie que l'environnement virtuel et le code utile a l'execution.

Ce choix reduit la surface de l'image finale et evite d'embarquer des fichiers de build inutiles.

La base retenue est `python:3.12-alpine`. C'est un compromis simple et robuste:

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

Mesure effectuée localement le 2026-04-28 (après optimisation du Dockerfile) :

```bash
docker build -t tp03-app:latest .
docker image inspect tp03-app:latest --format '{{.Size}}'
# Analyse d'efficacité avec dive
dive tp03-app:latest
```

Résultat :

- `121000000` octets (environ `121 MB`)
- Espace potentiellement gaspillé : `594 kB`
- Score d'efficacité : `99 %`

Le seuil demandé de moins de `200MB` est donc largement respecté, avec une image optimisée et très peu de gaspillage.

## Trivy en CI

Le scan Trivy est désormais intégré à la CI.

Le pipeline CI construit l'image Docker finale, puis exécute un scan Trivy sur cette image. Le pipeline échoue automatiquement en cas de vulnérabilités de sévérité `HIGH` ou `CRITICAL`, conformément à la politique de sécurité du projet.

Ce contrôle permet de garantir que seules des images conformes aux exigences de sécurité sont produites et déployées.
