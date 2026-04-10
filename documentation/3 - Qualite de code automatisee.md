# 3 qualite de code automatisee

## Etat global

- linting et formatting: OK
- pre-commit hook lint + format: OK
- verification lint par pipeline CI (double filet): OK
- sonarcloud + quality gate dans la CI: OK
- cache des dependances Python dans la CI: OK
- scan securite des dependances dans la CI: OK
- dependabot: OK

## Linting & Formatting

La stack de qualite Python est basee sur Ruff.

Elements en place:

- regles Ruff personnalisees: `E`, `F`, `I`
- longueur de ligne fixee a `80`
- cible Python `py312`
- formatage automatique via Ruff formatter

Preuves:

- configuration Ruff: [pyproject.toml](../pyproject.toml)
- commande lint: [Makefile](../Makefile)
- commande format: [Makefile](../Makefile)

## Pre-commit hook

Un hook Git pre-commit est configure pour executer automatiquement:

1. `make format`
2. `make lint`

Si le format modifie des fichiers, le commit est bloque pour obliger un restage des changements.

Preuves:

- script hook: [.githooks/pre-commit](../.githooks/pre-commit)
- installation des hooks: [Makefile](../Makefile)
- cible pre-commit: [Makefile](../Makefile)

## Double filet de securite (local + CI)

Etat actuel:

- filet local: OK (hook pre-commit)
- filet CI: OK (job dedie lint + format-check)

Preuves:

- pipeline CI: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- commandes qualite: [Makefile](../Makefile)

## Analyse statique et SonarCloud

Etat actuel: implemente dans la CI.

Elements en place:

- execution d'un scan SonarCloud dans un job dedie
- attente explicite du resultat quality gate
- timeout configure pour eviter un job bloque indefiniment

Preuves:

- workflow CI: [.github/workflows/ci.yml](../.github/workflows/ci.yml)

## Securite des dependances

Dependabot est configure et complete par un scan en CI.

Preuve:

- config Dependabot: [.github/dependabot.yml](../.github/dependabot.yml)
- job de scan securite: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- commande de scan: [Makefile](../Makefile)

Etat par exigence:

- activation d'un outil de scan de dependances: OK (Dependabot + pip-audit)
- echec pipeline en cas de vulnerabilite detectee par le scan CI: OK

## Performance CI: cache dependances Python

L'action composite de setup Python active un cache pour reduire les temps d'installation.

Elements caches:

- cache pip (`~/.cache/pip`)
- cache uv (`~/.cache/uv`)

Preuve:

- action composite: [.github/actions/setup-python-env/action.yml](../.github/actions/setup-python-env/action.yml)
