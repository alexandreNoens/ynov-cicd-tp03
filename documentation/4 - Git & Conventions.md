# 4 git & conventions

## Template commit utilise

J'utilise un template de commit situe dans `~/.gitmessage`:

```text
# 50-character subject line
#
# 72-character wrapped longer description. This should answer:
#
# * Why was this change necessary? (goals, use cases, stories, etc.)
# * How does it address the problem? (implementations, algorithms, etc.)
# * Are there any side effects?
#
# See links to relevant web pages, issue trackers, blog articles, etc.
# See: https://example.com/
# See: [Example Page](https://example.com/)
# Resolves: #1234
#
# Add co-authors if you worked on this code with others:
#
# Co-authored-by: Full Name <email@example.com>
# Co-authored-by: Full Name <email@example.com>
#
# ## Help ##
#
# Subject line imperative uppercase verbs:
#
#   Add = Create a capability e.g. feature, test, dependency.
#   Drop = Delete a capability e.g. feature, test, dependency.
#   Fix = Fix an issue e.g. bug, typo, accident, misstatement.
#   Bump = Increase the version of something e.g. a dependency.
#   Make = Change the build process, or tools, or infrastructure.
#   Start = Begin doing something; e.g. enable a toggle, feature flag, etc.
#   Stop = End doing something; e.g. disable a toggle, feature flag, etc.
#   Optimize = A change that MUST be just about performance, e.g. speed up code.
#   Document = A change that MUST be only in the documentation, e.g. help files.
#   Refactor = A change that MUST be just refactoring.
#   Reformat = A change that MUST be just format, e.g. indent line, trim space, etc.
#   Rephrase = A change that MUST be just textual, e.g. edit a comment, doc, etc.
#
# For the subject line:
#   * Use 50 characters maximum.
#   * Do not use a sentence-ending period.
#
# For the body text:
#   * Use as many lines as you like.
#   * Use 72 characters maximum per line for typical word wrap text.
```

Activation locale:

Ce template est configure dans `~/.gitconfig`:

```ini
[commit]
  gpgsign = true
  template = ~/.gitmessage
```

`gpgsign = true` active la signature des commits avec GPG.
L'objectif est de garantir l'authenticite des commits et d'ajouter
une preuve de provenance dans l'historique Git.

J'utilise aussi Neovim pour rediger les messages de commit:

```ini
[core]
  editor = nvim
```


## Strategie de branches

Strategie cible: GitHub Flow.

- branche principale protegee: `main` (ou `master` selon le repo)
- developpement sur branches courtes:
  - `feature/...`
  - `fix/...`
  - `ci/...`
  - `refactor/...`
- cycle de travail:
  1. creer une branche
  2. ouvrir une PR
  3. valider CI et review
  4. merger dans la branche principale

## Bloquer master et rendre la PR obligatoire

Dans la protection de branche, j'ai active les options suivantes:

- `Require a pull request before merging`:
  interdiction de push direct sur la branche protegee (master);
  tous les changements passent par une PR.
- `Require conversation resolution before merging`:
  toutes les conversations de review doivent etre resolues avant merge.
- `Require signed commits`:
  les commits doivent etre signes et verifies;
  c'est coherent avec ma configuration `gpgsign = true`.
- `Require status checks to pass before merging`:
  les checks CI definis doivent etre au vert avant le merge.
  Cette regle rend la CI bloquante sur la branche protegee.
- `Require branches to be up to date before merging`:
  la branche de PR doit etre testee avec le code le plus recent de
  `master` avant de pouvoir merger.

Option recommandee mais non activee dans mon contexte:

- `Require approvals`:
  en developpement solo, cette regle est difficilement applicable,
  car je ne dispose pas d'un second reviewer pour approuver la PR.
  En revanche, des qu'on est au moins 2 developpeurs, il faut l'activer
  pour imposer une relecture du code par une autre personne avant merge.
