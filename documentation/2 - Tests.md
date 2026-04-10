# 2 tests

## Repartition actuelle

Le projet contient principalement des tests unitaires et des tests d'integration.

- tests unitaires: validation du modele `Student`
- tests d'integration: repository + PostgreSQL
- tests d'integration: routes FastAPI + validation + base de donnees
- tests techniques complementaires: healthcheck et cycle de vie de l'application

Comme il s'agit d'une API pure sans interface web, les tests end-to-end ne sont pas le niveau de test prioritaire ici.

## Tests unitaires

Les tests unitaires couvrent la logique de validation du modele Pydantic.

Exemples verifies:

- valeur par defaut de `id`
- validation de `first_name`
- validation de `last_name`
- validation de l'email
- bornes de `grade`
- enum `field`

Exemple:

```python
def test_email_invalid_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(**student_payload(email="invalid-email"))
```

Source: [tests/models/test_student_model.py](../tests/models/test_student_model.py#L19)

Evaluation par rapport a la grille:

- la logique de validation est bien couverte;
- les tests sont courts, stables et rapides;
- chaque test verifie un comportement cible;
- les assertions sont presentes;
- le nommage est explicite, meme s'il ne suit pas exactement le format litteral `should [resultat] when [condition]`.

Concernant la structure AAA:

- elle est bien respectee dans l'esprit;
- les etapes Arrange / Act / Assert ne sont pas commentees explicitement, mais elles restent lisibles dans la plupart des tests.

## Tests d'integration

Deux niveaux d'integration sont presents.

### Integration repository + base de donnees

Les tests repository verifient l'interaction entre la couche d'acces aux donnees et PostgreSQL.

Cas verifies:

- lecture liste/detail
- creation
- mise a jour
- suppression
- contraintes d'unicite
- recherche
- statistiques
- cas limites sur base vide

Exemple:

```python
def test_list_students_returns_students_ordered_by_id() -> None:
    students = list_students()

    assert isinstance(students, list)
    assert len(students) == 5
    assert all(isinstance(student, Student) for student in students)
    assert [student.id for student in students] == [1, 2, 3, 4, 5]
```

Source: [tests/repositories/test_student_repository.py](../tests/repositories/test_student_repository.py#L22)

### Integration routes + application + base de donnees

Les tests de routes utilisent `TestClient` et valident le comportement HTTP complet.

Cas verifies:

- `200` sur les cas nominaux
- `201` sur creation
- `400` sur payload ou parametres invalides
- `404` sur ressource absente
- `409` sur conflit d'email
- pagination
- tri
- recherche
- statistiques

Exemple:

```python
def test_get_students_returns_json_array_with_status_200(
    client: TestClient,
) -> None:
    response = client.get("/students")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
```

Source: [tests/routes/test_students_route.py](../tests/routes/test_students_route.py#L6)

## Isolation et base de test

L'isolation des tests repose sur une remise a zero automatique de la base avant chaque test.

Exemple:

```python
@pytest.fixture(autouse=True)
def reset_database() -> None:
    reset_db()
```

Source: [tests/conftest.py](../tests/conftest.py#L22)

Analyse:

- la suite est deterministe;
- les tests ne dependent pas de l'ordre d'execution;
- les donnees de depart sont recreees a chaque test.

Point important:

- la base de test n'est pas une base in-memory;
- elle est reinitialisee automatiquement par `reset_db()` avant chaque test.

Pour aller encore plus loin, une amelioration possible serait de separer explicitement les environnements `dev` et `test` avec une base PostgreSQL de test dediee.

## Mocking

Le projet utilise tres peu de mocking, ce qui est plutot sain ici.

Cas present:

- `monkeypatch` est utilise dans deux tests repository pour simuler un cas d'echec apres creation ou mise a jour.

Pourquoi c'est acceptable:

- cela permet de tester un chemin d'erreur difficile a provoquer naturellement;
- le mock reste local et cible.

Limite:

- ce n'est pas une dependance externe au sens strict;
- dans une lecture tres stricte de la consigne, ces deux tests sont davantage des tests defensifs que des tests fonctionnels centraux.

## Tests end-to-end

Les tests end-to-end ne sont pas implementes, et cela est justifiable ici.

Pourquoi:

- le projet est une API REST sans front web;
- il n'y a pas de parcours utilisateur navigateur a simuler avec Playwright, Cypress ou Selenium.

Compensation mise en place:

- une couverture forte des tests d'integration HTTP;
- verification des cas nominaux et des cas d'erreur;
- verification du demarrage applicatif via le lifespan.

## Couverture de code

La couverture minimale demandee est de 70%.

Etat du projet:

- seuil bloque a 90% dans la commande de test
- couverture reelle mesuree: 100%

Ce point est donc valide au-dela du minimum attendu.

Attention toutefois:

- `100%` de couverture ne garantit pas l'absence de bugs;
- la valeur de la suite vient surtout de la pertinence des assertions et des cas testes.

## Rapport et pipeline

Etat actuel verifie:

- la couverture est calculee localement et en CI via `pytest-cov`;
- le seuil est bloquant (`--cov-fail-under=90`);
- les tests unitaires et d'integration executent chacun un coverage;
- le detail par fichier est visible dans la sortie terminal.

Etat CI actuel:

- les jobs `unit-tests` et `integration-tests` executent la couverture;
- aucun artefact de coverage n'est publie pour le moment;
- SonarCloud est execute dans un job dedie, mais la couverture y est exclue via la configuration courante.

Si besoin pour la suite du projet, il faudra ajouter un export XML puis publier l'artefact:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml
```

puis publier `coverage.xml` comme artefact de pipeline.
