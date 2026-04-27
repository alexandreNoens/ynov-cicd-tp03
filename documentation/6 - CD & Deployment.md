# 6 - CD & Deployment

## Objectif

Mettre en place un pipeline de deploiement continu fonctionnel, meme sans serveur cible, en simulant le deploiement via publication d'images Docker dans un registry.

## Workflow CD implemente

Les processus d'intégration continue (CI) et de déploiement continu (CD) sont séparés en deux fichiers distincts.

Fichiers:
- `.github/workflows/ci.yml` (Construction de l'image Docker)
- `.github/workflows/cd.yml` (Déploiement)

### Intégration Continue (CI) et Build Docker

- **Fichier:** `ci.yml`
- **Déclencheurs:**
  - `pull_request` (n'importe quelle branche)
  - `push` sur `master`
- **Actions pertinentes pour le CD:**
  - Si tous les tests de la CI passent, l'image Docker est construite.
  - L'image est poussée sur le GitHub Container Registry (GHCR) (`ghcr.io`).
  - **Tags utilisés:**
    - Sur une PR: `pr-[numéro]` et `[sha_du_commit]`
    - Sur `master`: `[sha_du_commit]` et `latest`

### Testing (Staging automatique)

- **Fichier:** `cd.yml` (Job `deploy-testing`)
- **Déclencheurs:**
  - `workflow_run` (Se déclenche lorsque le workflow de CI se termine avec succès).
- **Action de déploiement simulée:**
  - Récupère l'image Docker qui vient d'être compilée et validée par la CI en utilisant le tag basé sur le SHA du commit (`head_sha`).
  - Simule un déploiement avec un `echo "Deploy [image] to testing"`.

### Production

- **Fichier:** `cd.yml` (Job `deploy-production`)
- **Déclencheurs:**
  - `workflow_run` (Se déclenche lorsque le workflow de CI se termine avec succès).
  - Condition: Ne s'exécute que si la branche d'origine de la CI est la branche par défaut (`master`).
- **Action de déploiement simulée:**
  - Récupère l'image Docker avec le tag `head_sha`.
  - Simule un déploiement avec un `echo "Deploy [image] to production"`.

Important:
- Le fichier `cd.yml` utilise la méthode de déclenchement `workflow_run`. C'est une bonne pratique de sécurité car cela permet d'isoler le CD de la CI (la CI build l'image de façon non privilégiée, et le CD s'exécute dans le contexte privilégié de la branche par défaut une fois l'image validée).

## Secrets et permissions

Ce pipeline utilise le jeton natif `GITHUB_TOKEN` pour interagir avec GHCR.

**Permissions requises dans `ci.yml` (pour construire et pousser) :**
- `contents: read`
- `packages: write`

**Permissions requises dans `cd.yml` (pour récupérer les images) :**
- `contents: read`
- `packages: read`

Si vous souhaitez Docker Hub a la place de GHCR:
- Changer REGISTRY en docker.io
- Ajouter secrets DOCKERHUB_USERNAME et DOCKERHUB_TOKEN
- Adapter l'etape docker/login-action

## Strategie de deploiement reelle recommandee

### Cible cloud proposee

- Cloud: AWS
- Service: ECS Fargate
- Registry: GHCR ou ECR
- Base de donnees: RDS PostgreSQL
- Reverse proxy / TLS: ALB + ACM

### Configuration type

- 1 service web FastAPI (min 1 task en staging, 2 tasks en production)
- Auto-scaling base sur CPU ou latence
- Variables sensibles stockees dans AWS Secrets Manager
- Migrations executees au deploiement (job one-shot)

### Estimation de cout mensuel (ordre de grandeur)

Staging:
- ECS Fargate (petite taille): ~15 a 30 EUR
- RDS PostgreSQL (db.t4g.micro): ~15 a 25 EUR
- ALB + trafic modere: ~15 a 25 EUR
- Total staging: ~45 a 80 EUR / mois

Production (petit trafic):
- ECS Fargate (2 tasks): ~30 a 70 EUR
- RDS PostgreSQL (instance plus robuste + backup): ~30 a 90 EUR
- ALB + logs + monitoring: ~20 a 50 EUR
- Total production: ~80 a 210 EUR / mois

Ces montants varient selon region, trafic, retention des logs et politique de sauvegarde.

## Validation attendue

- Toute modification de code dans une PR ou un commit déclenche la construction de l'image Docker (si les tests passent).
- La réussite de la CI déclenche automatiquement le workflow CD via l'événement `workflow_run`.
- **En PR :** Seul le déploiement simulé de Testing (`deploy-testing`) est exécuté.
- **Sur la branche principale :** Les déploiements Testing et Production s'exécutent.
