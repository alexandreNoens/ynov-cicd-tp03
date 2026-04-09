# 1 code & design patterns

### Pattern 1 - Repository

Ou: [app/repositories/student.py](../app/repositories/student.py)

Pourquoi:

- centraliser toutes les requetes SQL dans une couche dediee;
- isoler la persistance du transport HTTP;
- simplifier les tests unitaires du stockage.

Impact testabilite:

- les tests repository valident les regles de persistance sans passer par HTTP;
- les tests de routes valident l'API sans dupliquer la logique SQL.

Exemple :


```python
def create_student(student: StudentCreate) -> Student:
	query = """
	INSERT INTO students (firstName, lastName, email, grade, field)
	VALUES (?, ?, ?, ?, ?)
	"""
	try:
		with get_connection() as connection:
			cursor = connection.execute(
				query,
				(
					student.firstName,
					student.lastName,
					student.email,
					student.grade,
					student.field,
				),
			)
			created_student_id = cursor.lastrowid
	except sqlite3.IntegrityError as exc:
		if "students.email" in str(exc):
			raise StudentEmailAlreadyExistsError() from exc

	created_student = get_student_by_id(created_student_id)
	return created_student
```

Source: [app/repositories/student.py](../app/repositories/student.py#L60)


### Pattern 2 - DTO / Validation Object (Pydantic models)

Ou: [app/models/student.py](../app/models/student.py)

Pourquoi:

- imposer un contrat d'entree explicite;
- appliquer les contraintes (taille, borne, enum, email) au plus tot;
- reduire le risque de donnees invalides en base.

Impact testabilite:

- les erreurs de validation sont predictibles et testables (400);
- la couche route reste concise car la validation est externalisee.

Exemple :

```python
class StudentCreate(BaseModel):
	firstName: str = Field(min_length=2)
	lastName: str = Field(min_length=2)
	email: str
	grade: float = Field(ge=0, le=20)
	field: Literal["informatique", "mathématiques", "physique", "chimie"]

	@field_validator("email")
	@classmethod
	def validate_email(cls, value: str) -> str:
		if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
			raise ValueError("Email invalide")
		return value
```

Source: [app/models/student.py](../app/models/student.py#L7)

### Pattern 3 - Exception translation (Domain -> HTTP)

Ou: [app/exceptions/student.py](../app/exceptions/student.py) et [app/routes/student.py](../app/routes/student.py)

Pourquoi:

- exprimer des erreurs metier explicites (`StudentNotFoundError`, `StudentEmailAlreadyExistsError`);
- traduire proprement ces erreurs en codes HTTP semantiques (404/409);
- eviter de propager des exceptions techniques brutes au client.

Impact testabilite:

- verification directe des mappings d'erreur dans les tests de routes;
- comportement stable et documentable pour les consommateurs de l'API.

Exemple :

```python
try:
	return update_student(parsed_student_id, student_to_update)
except StudentNotFoundError as exc:
	raise HTTPException(
		status_code=404, detail="student not found"
	) from exc
except StudentEmailAlreadyExistsError as exc:
	raise HTTPException(
		status_code=409,
		detail="student email already exists",
	) from exc
```

Source: [app/routes/student.py](../app/routes/student.py#L88)

### Pattern 4 - Decorator

Ou: [app/routes/student.py](../app/routes/student.py), [app/models/student.py](../app/models/student.py) et [app/main.py](../app/main.py)

Pourquoi:

- ajouter des comportements (routing, validation, gestion de cycle de vie) sans modifier la logique metier interne;
- garder le code declaratif et lisible.

Impact testabilite:

- les comportements decorés sont testables via les endpoints et les validations;
- la logique metier reste isolee des mecanismes framework.

Exemple :

```python
@router.post("/students", response_model=Student, status_code=201)
def post_student(payload: dict[str, Any]) -> Student:
	try:
		student_to_create = StudentCreate(**payload)
	except ValidationError as exc:
		raise HTTPException(
			status_code=400, detail=json.loads(exc.json())
		) from exc

@field_validator("email")
@classmethod
def validate_email(cls, value: str) -> str:
	if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
		raise ValueError("Email invalide")
	return value
```

Source: [app/routes/student.py](../app/routes/student.py#L52) et [app/models/student.py](../app/models/student.py#L14)

Autre exemple dans le cycle de vie de l'application:

```python
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
	init_db()
	yield
```

Source: [app/main.py](../app/main.py#L10)

### Pattern 5 - Factory Method (tests)

Ou: [tests/conftest.py](../tests/conftest.py)

Pourquoi:

- centraliser la creation de jeux de donnees de test;
- parametrer facilement les cas de test via des overrides.

Impact testabilite:

- reduction de duplication dans les tests;
- scenarios plus lisibles et plus faciles a maintenir.

Exemple :

```python
@pytest.fixture
def student_payload_factory() -> Callable[..., dict[str, object]]:
	def make_payload(**overrides: object) -> dict[str, object]:
		payload = _default_student_payload()
		payload.update(overrides)
		return payload

	return make_payload


@pytest.fixture
def student_create_factory() -> Callable[..., StudentCreate]:
	def make_student(**overrides: object) -> StudentCreate:
		payload = _default_student_payload()
		payload.update(overrides)
		return StudentCreate(**payload)

	return make_student
```

Source: [tests/conftest.py](../tests/conftest.py#L32)

### Pattern 6 - Chain of Responsibility (pipeline FastAPI)

Ou: [app/routes/student.py](../app/routes/student.py) et [app/models/student.py](../app/models/student.py)

Pourquoi:

- traiter une requete en etapes successives (validation, execution, mapping erreurs);
- separer les responsabilites de chaque etape.

Impact testabilite:

- chaque etape est verifiable via des tests d'API (400/404/409/200);
- facilite l'identification de la couche qui regressse.

Exemple :

```python
@router.put("/students/{student_id}", response_model=Student)
def put_student(student_id: str, payload: dict[str, Any]) -> Student:
	try:
		parsed_student_id = int(student_id)
	except ValueError as exc:
		raise HTTPException(
			status_code=400,
			detail="student id must be a valid number",
		) from exc

	try:
		student_to_update = StudentCreate(**payload)
	except ValidationError as exc:
		raise HTTPException(
			status_code=400, detail=json.loads(exc.json())
		) from exc

	try:
		return update_student(parsed_student_id, student_to_update)
	except StudentNotFoundError as exc:
		raise HTTPException(
			status_code=404, detail="student not found"
		) from exc
```

Source: [app/routes/student.py](../app/routes/student.py#L70)
