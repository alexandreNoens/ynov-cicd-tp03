# 3 qualite de code automatisee

## Etat global

- linting et formatting: OK
- pre-commit hook lint + format: OK
- dependabot: OK
- sonarcloud / quality gate / commentaire PR: TODO
- verification lint par pipeline CI (double filet): TODO
- echec pipeline sur vulnerabilite critique: TODO

## Linting & Formatting

La stack de qualite Python est basee sur Ruff.

Elements en place:

- regles Ruff personnalisees: `E`, `F`, `I`
- longueur de ligne fixee a `80`
- cible Python `py312`
- formatage automatique via Ruff formatter

Preuves:

- configuration Ruff: [pyproject.toml](../pyproject.toml)
- commande lint: [Makefile](../Makefile#L36)
- commande format: [Makefile](../Makefile#L41)

## Pre-commit hook

Un hook Git pre-commit est configure pour executer automatiquement:

1. `make format`
2. `make lint`

Si le format modifie des fichiers, le commit est bloque pour obliger un restage des changements.

Preuves:

- script hook: [.githooks/pre-commit](../.githooks/pre-commit)
- installation des hooks: [Makefile](../Makefile#L18)
- cible pre-commit: [Makefile](../Makefile#L44)

## Double filet de securite (local + CI)

Etat actuel:

- filet local: OK (hook pre-commit)
- filet CI: TODO

Action restante:

- faire verifier le lint aussi dans la pipeline CI.

## Analyse statique et SonarCloud

Etat actuel: TODO.

Le plan d'implementation SonarCloud est decrit ici:

- [TODO - SonarQube.md](TODO%20-%20SonarQube.md)

Points cibles:

- scan Sonar dans la CI
- quality gate: `0 bugs`, `0 vulnerabilities`, `duplication < 3%`, `coverage >= 70%`
- commentaire automatique sur les PR

## Securite des dependances

Dependabot est configure.

Preuve:

- config Dependabot: [.github/dependabot.yml](../.github/dependabot.yml)

Etat par exigence:

- activation d'un outil de scan de dependances: OK (Dependabot)
- echec pipeline en cas de vulnerabilite critique: TODO
