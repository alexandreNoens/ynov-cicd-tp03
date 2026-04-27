# Projet CI/CD & DevOps Production-Ready

[![CI](https://github.com/alexandreNoens/ynov-cicd-tp03/actions/workflows/ci.yml/badge.svg)](https://github.com/alexandreNoens/ynov-cicd-tp03/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](#prérequis)
[![FastAPI](https://img.shields.io/badge/FastAPI-modern-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Ruff](https://img.shields.io/badge/lint-ruff-46a2f1?logo=ruff)](https://docs.astral.sh/ruff)
[![Pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest)](https://docs.pytest.org/)

Concevez, developpez et deployez une application complete avec un pipeline CI/CD professionnel, une architecture de code solide, et une infrastructure reproductible. Votre code, votre pipeline, vos choix, vos justifications.

## Lancement rapide

1. Copier les variables d'environnement:

```bash
cp .env.example .env
```

2. Installer les dependances Python:

```bash
make install
```

3. Lancer PostgreSQL en local:

```bash
make compose-up
```

4. Initialiser schema + donnees:

```bash
make install-db
```

5. Lancer l'API:

```bash
make serve
```

6. Executer la suite de tests:

```bash
make check
```

## Lancement avec Docker

1. Copier les variables d'environnement:

```bash
cp .env.example .env
```

2. Construire et lancer API + PostgreSQL:

```bash
docker compose up --build
```

3. Tester l'API:

```bash
curl http://localhost:8000/health
```

## Rendu / Documentation

La documentation du projet est centralisee dans le dossier [documentation](documentation).

Document a consulter:

- [1 - Code & Design Patterns.md](documentation/1%20-%20Code%20&%20Design%20Patterns.md)
- [2 - Tests.md](documentation/2%20-%20Tests.md)
- [3 - Qualite de code automatisee.md](documentation/3%20-%20Qualite%20de%20code%20automatisee.md)
- [4 - Git & Conventions.md](documentation/4%20-%20Git%20&%20Conventions.md)
- [5 - Docker & Conteneurisation.md](documentation/5%20-%20Docker%20%26%20Conteneurisation.md)
- [6 - CD & Deployment.md](documentation/6%20-%20CD%20%26%20Deployment.md)
- [TODO.md](documentation/TODO.md)

Arborescence :

```text
documentation/
├── 1 - Code & Design Patterns.md
├── 2 - Tests.md
├── 3 - Qualite de code automatisee.md
├── 4 - Git & Conventions.md
├── 5 - Docker & Conteneurisation.md
├── 6 - CD & Deployment.md
└── TODO.md
```
